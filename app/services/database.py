from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables BEFORE importing Google Cloud
load_dotenv()
dotenv_local_path = os.path.join(os.getcwd(), '.env.local')
if os.path.exists(dotenv_local_path):
    load_dotenv(dotenv_local_path, override=True)

from google.cloud import firestore
from google.api_core.exceptions import NotFound
from pydantic import ValidationError

from app.models import User, Task, FitnessLog, TaskPriority, TaskStatus, FitnessLogType


def _get_firestore_client() -> firestore.Client:
    """Initialize and return Firestore client.

    Prefers GOOGLE_CLOUD_PROJECT from env; otherwise falls back to default creds.
    """
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if project_id:
        return firestore.Client(project=project_id)
    return firestore.Client()


def get_firestore_client() -> firestore.Client:
    """Public function to get Firestore client"""
    return _get_firestore_client()


db = _get_firestore_client()


# Collection names
USERS_COLLECTION = "users"
TASKS_COLLECTION = "tasks"
FITNESS_LOGS_COLLECTION = "fitness_logs"


# ----------------------
# User CRUD
# ----------------------
def create_user(user: User) -> User:
    doc_ref = db.collection(USERS_COLLECTION).document(user.user_id)
    doc_ref.set(user.to_dict())
    return user


def get_user(user_id: str) -> Optional[User]:
    doc_ref = db.collection(USERS_COLLECTION).document(user_id)
    doc = doc_ref.get()
    if not doc.exists:
        return None
    data = doc.to_dict() or {}
    try:
        return User.from_dict(data)
    except ValidationError as exc:
        raise ValueError(f"Invalid user data for {user_id}: {exc}")


def update_user(user_id: str, updates: Dict[str, Any]) -> Optional[User]:
    doc_ref = db.collection(USERS_COLLECTION).document(user_id)
    try:
        doc_ref.update(updates)
    except NotFound:
        return None
    return get_user(user_id)


def delete_user(user_id: str) -> bool:
    doc_ref = db.collection(USERS_COLLECTION).document(user_id)
    try:
        doc_ref.delete()
        return True
    except NotFound:
        return False


def list_users(limit: int = 50) -> List[User]:
    docs = db.collection(USERS_COLLECTION).limit(limit).stream()
    users: List[User] = []
    for doc in docs:
        data = doc.to_dict() or {}
        try:
            users.append(User.from_dict(data))
        except ValidationError:
            continue
    return users


# ----------------------
# Task CRUD
# ----------------------
def create_task(task: Task) -> Task:
    doc_ref = db.collection(TASKS_COLLECTION).document(task.task_id)
    doc_ref.set(task.to_dict())
    return task


def get_task(task_id: str) -> Optional[Task]:
    doc_ref = db.collection(TASKS_COLLECTION).document(task_id)
    doc = doc_ref.get()
    if not doc.exists:
        return None
    data = doc.to_dict() or {}
    try:
        return Task.from_dict(data)
    except ValidationError as exc:
        raise ValueError(f"Invalid task data for {task_id}: {exc}")


def update_task(task_id: str, updates: Dict[str, Any]) -> Optional[Task]:
    doc_ref = db.collection(TASKS_COLLECTION).document(task_id)
    try:
        doc_ref.update(updates)
    except NotFound:
        return None
    return get_task(task_id)


def delete_task(task_id: str) -> bool:
    doc_ref = db.collection(TASKS_COLLECTION).document(task_id)
    try:
        doc_ref.delete()
        return True
    except NotFound:
        return False


def list_tasks_by_user(
    user_id: str,
    limit: int = 100,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    date_range: Optional[Tuple[Optional[Any], Optional[Any]]] = None,
) -> List[Task]:
    """List tasks for a user with defensive error handling"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        query = db.collection(TASKS_COLLECTION).where("user_id", "==", user_id)

        if status is not None:
            query = query.where("status", "==", status.value)
        if priority is not None:
            query = query.where("priority", "==", priority.value)
        
        # When filtering by date range, order by due_date to avoid composite index requirement
        # Otherwise order by created_at for chronological listing
        order_field = "created_at"
        
        if date_range is not None:
            start, end = date_range
            if start is not None:
                query = query.where("due_date", ">=", start)
                order_field = "due_date"  # Must order by same field we're filtering
            if end is not None:
                query = query.where("due_date", "<=", end)
                order_field = "due_date"  # Must order by same field we're filtering

        query = query.order_by(order_field, direction=firestore.Query.DESCENDING).limit(limit)
        docs = query.stream()
        tasks: List[Task] = []
        for doc in docs:
            data = doc.to_dict() or {}
            try:
                tasks.append(Task.from_dict(data))
            except ValidationError as e:
                logger.warning(f"Skipping invalid task: {e}")
                continue
        
        logger.info(f"Found {len(tasks)} tasks for user {user_id}")
        return tasks
    
    except Exception as e:
        logger.error(f"Error querying tasks for user {user_id}: {str(e)}", exc_info=True)
        # Return empty list instead of throwing - defensive programming
        return []


# ----------------------
# FitnessLog CRUD
# ----------------------
# Feature flag for migration
USE_NEW_STRUCTURE = True

def create_fitness_log(log: FitnessLog) -> FitnessLog:
    """Create fitness log (supports both old and new structure)"""
    if USE_NEW_STRUCTURE:
        # NEW: Save to user's subcollection
        doc_ref = db.collection('users').document(log.user_id)\
                    .collection('fitness_logs').document(log.log_id)
        doc_ref.set(log.to_dict())
    else:
        # OLD: Save to flat collection
        doc_ref = db.collection(FITNESS_LOGS_COLLECTION).document(log.log_id)
        doc_ref.set(log.to_dict())
    return log


def get_fitness_log(log_id: str, user_id: str = None) -> Optional[FitnessLog]:
    """Get fitness log by ID"""
    if USE_NEW_STRUCTURE and user_id:
        # NEW: Get from user's subcollection
        doc_ref = db.collection('users').document(user_id)\
                    .collection('fitness_logs').document(log_id)
        doc = doc_ref.get()
        if not doc.exists:
            return None
        data = doc.to_dict() or {}
        try:
            return FitnessLog.from_dict(data)
        except ValidationError as exc:
            raise ValueError(f"Invalid fitness log data for {log_id}: {exc}")
    else:
        # OLD: Get from flat collection
        doc_ref = db.collection(FITNESS_LOGS_COLLECTION).document(log_id)
        doc = doc_ref.get()
        if not doc.exists:
            return None
        data = doc.to_dict() or {}
        try:
            return FitnessLog.from_dict(data)
        except ValidationError as exc:
            raise ValueError(f"Invalid fitness log data for {log_id}: {exc}")


def update_fitness_log(log_id: str, updates: Dict[str, Any], user_id: str = None) -> Optional[FitnessLog]:
    """Update fitness log"""
    if USE_NEW_STRUCTURE and user_id:
        # NEW: Update in user's subcollection
        doc_ref = db.collection('users').document(user_id)\
                    .collection('fitness_logs').document(log_id)
        try:
            doc_ref.update(updates)
        except NotFound:
            return None
        return get_fitness_log(log_id, user_id)
    else:
        # OLD: Update in flat collection
        doc_ref = db.collection(FITNESS_LOGS_COLLECTION).document(log_id)
        try:
            doc_ref.update(updates)
        except NotFound:
            return None
        return get_fitness_log(log_id)


def delete_fitness_log(log_id: str, user_id: str = None) -> bool:
    """Delete fitness log"""
    if USE_NEW_STRUCTURE and user_id:
        # NEW: Delete from user's subcollection
        doc_ref = db.collection('users').document(user_id)\
                    .collection('fitness_logs').document(log_id)
        try:
            doc_ref.delete()
            return True
        except NotFound:
            return False
    else:
        # OLD: Delete from flat collection
        doc_ref = db.collection(FITNESS_LOGS_COLLECTION).document(log_id)
        try:
            doc_ref.delete()
            return True
        except NotFound:
            return False


def list_fitness_logs_by_user(
    user_id: str,
    limit: int = 100,
    start_ts: Optional[Any] = None,
    end_ts: Optional[Any] = None,
    log_type: Optional[FitnessLogType] = None,
) -> List[FitnessLog]:
    """List fitness logs for a user (with automatic fallback to old structure)"""
    import logging
    logger = logging.getLogger(__name__)
    
    logs: List[FitnessLog] = []
    
    try:
        if USE_NEW_STRUCTURE:
            # NEW: Query user's subcollection (no user_id filter needed!)
            logger.info(f"Querying NEW structure for user: {user_id}")
            query = db.collection('users').document(user_id)\
                      .collection('fitness_logs')
            
            # Apply filters - timestamp filters first, then log_type
            if start_ts is not None:
                query = query.where("timestamp", ">=", start_ts)
            if end_ts is not None:
                query = query.where("timestamp", "<=", end_ts)
            
            # Always order by timestamp (the field we're filtering on)
            query = query.order_by("timestamp", direction=firestore.Query.DESCENDING)
            
            # Apply log_type filter AFTER ordering to avoid composite index issues
            # We'll filter in memory instead
            query = query.limit(limit * 2 if log_type else limit)  # Fetch more if we need to filter
            docs = query.stream()
            
            for doc in docs:
                data = doc.to_dict() or {}
                try:
                    log = FitnessLog.from_dict(data)
                    # Apply log_type filter in memory if specified
                    if log_type is None or log.log_type == log_type:
                        logs.append(log)
                        if len(logs) >= limit:  # Stop once we have enough
                            break
                except ValidationError as e:
                    logger.warning(f"Skipping invalid fitness log: {e}")
                    continue
            
            logger.info(f"Found {len(logs)} logs in NEW structure (after filtering)")
            
            # If no logs found in new structure, try old structure as fallback
            if len(logs) == 0:
                logger.info(f"No logs in NEW structure, trying OLD structure for user: {user_id}")
                return _query_old_structure(user_id, limit, start_ts, end_ts, log_type)
            
            return logs
        else:
            # OLD: Query flat collection with user_id filter
            return _query_old_structure(user_id, limit, start_ts, end_ts, log_type)
    
    except Exception as e:
        logger.error(f"Error querying fitness logs for user {user_id}: {str(e)}", exc_info=True)
        # Try fallback to old structure
        logger.info("Attempting fallback to OLD structure due to error")
        try:
            return _query_old_structure(user_id, limit, start_ts, end_ts, log_type)
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {str(fallback_error)}", exc_info=True)
            return []


def _query_old_structure(
    user_id: str,
    limit: int,
    start_ts: Optional[Any],
    end_ts: Optional[Any],
    log_type: Optional[FitnessLogType],
) -> List[FitnessLog]:
    """Query fitness logs from old flat collection structure"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Querying OLD structure for user: {user_id}")
    query = db.collection(FITNESS_LOGS_COLLECTION).where("user_id", "==", user_id)
    
    if log_type is not None:
        query = query.where("log_type", "==", log_type.value)
    if start_ts is not None:
        query = query.where("timestamp", ">=", start_ts)
    if end_ts is not None:
        query = query.where("timestamp", "<=", end_ts)
    
    query = query.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit)
    docs = query.stream()
    
    logs: List[FitnessLog] = []
    for doc in docs:
        data = doc.to_dict() or {}
        try:
            logs.append(FitnessLog.from_dict(data))
        except ValidationError as e:
            logger.warning(f"Skipping invalid fitness log: {e}")
            continue
    
    logger.info(f"Found {len(logs)} logs in OLD structure")
    return logs


