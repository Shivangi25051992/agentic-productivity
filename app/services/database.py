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
    query = db.collection(TASKS_COLLECTION).where("user_id", "==", user_id)

    if status is not None:
        query = query.where("status", "==", status.value)
    if priority is not None:
        query = query.where("priority", "==", priority.value)
    if date_range is not None:
        start, end = date_range
        if start is not None:
            query = query.where("due_date", ">=", start)
        if end is not None:
            query = query.where("due_date", "<=", end)

    query = query.order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
    docs = query.stream()
    tasks: List[Task] = []
    for doc in docs:
        data = doc.to_dict() or {}
        try:
            tasks.append(Task.from_dict(data))
        except ValidationError:
            continue
    return tasks


# ----------------------
# FitnessLog CRUD
# ----------------------
def create_fitness_log(log: FitnessLog) -> FitnessLog:
    doc_ref = db.collection(FITNESS_LOGS_COLLECTION).document(log.log_id)
    doc_ref.set(log.to_dict())
    return log


def get_fitness_log(log_id: str) -> Optional[FitnessLog]:
    doc_ref = db.collection(FITNESS_LOGS_COLLECTION).document(log_id)
    doc = doc_ref.get()
    if not doc.exists:
        return None
    data = doc.to_dict() or {}
    try:
        return FitnessLog.from_dict(data)
    except ValidationError as exc:
        raise ValueError(f"Invalid fitness log data for {log_id}: {exc}")


def update_fitness_log(log_id: str, updates: Dict[str, Any]) -> Optional[FitnessLog]:
    doc_ref = db.collection(FITNESS_LOGS_COLLECTION).document(log_id)
    try:
        doc_ref.update(updates)
    except NotFound:
        return None
    return get_fitness_log(log_id)


def delete_fitness_log(log_id: str) -> bool:
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
        except ValidationError:
            continue
    return logs


