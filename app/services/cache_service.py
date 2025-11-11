"""
Cache Service - High-level caching abstraction
Provides domain-specific caching for Timeline, Dashboard, and other features
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from .redis_client import redis_client

logger = logging.getLogger(__name__)


class CacheService:
    """
    High-level cache service with domain-specific methods
    
    Features:
    - Timeline caching (per user)
    - Dashboard stats caching (per user, per date)
    - Chat history caching
    - Automatic key generation
    - TTL management
    """
    
    # Default TTLs (in seconds)
    TIMELINE_TTL = 300  # 5 minutes
    DASHBOARD_TTL = 300  # 5 minutes
    CHAT_HISTORY_TTL = 600  # 10 minutes
    USER_PROFILE_TTL = 1800  # 30 minutes
    
    @staticmethod
    def _generate_key(prefix: str, *args) -> str:
        """
        Generate cache key with prefix and arguments
        
        Example:
            _generate_key("timeline", "user123", "meal,workout")
            -> "timeline:user123:meal,workout"
        """
        parts = [prefix] + [str(arg) for arg in args]
        return ":".join(parts)
    
    # ========== TIMELINE CACHING ==========
    
    @staticmethod
    def get_timeline(
        user_id: str,
        types: str = "meal,workout,task,water,supplement",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached timeline data
        
        Args:
            user_id: User ID
            types: Comma-separated activity types
            start_date: Start date filter (ISO format)
            end_date: End date filter (ISO format)
            
        Returns:
            Cached timeline data or None if not found
        """
        key = CacheService._generate_key(
            "timeline",
            user_id,
            types,
            start_date or "all",
            end_date or "all"
        )
        
        cached = redis_client.get(key)
        if cached:
            logger.info(f"⚡ Cache HIT: Timeline for user {user_id}")
        else:
            logger.info(f"💨 Cache MISS: Timeline for user {user_id}")
        
        return cached
    
    @staticmethod
    def set_timeline(
        user_id: str,
        data: Dict[str, Any],
        types: str = "meal,workout,task,water,supplement",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Cache timeline data
        
        Args:
            user_id: User ID
            data: Timeline data to cache
            types: Comma-separated activity types
            start_date: Start date filter (ISO format)
            end_date: End date filter (ISO format)
            ttl: Time-to-live in seconds (default: TIMELINE_TTL)
            
        Returns:
            True if successful, False otherwise
        """
        key = CacheService._generate_key(
            "timeline",
            user_id,
            types,
            start_date or "all",
            end_date or "all"
        )
        
        success = redis_client.set(key, data, ttl or CacheService.TIMELINE_TTL)
        
        if success:
            logger.info(f"✅ Cached timeline for user {user_id} (TTL: {ttl or CacheService.TIMELINE_TTL}s)")
        
        return success
    
    @staticmethod
    def invalidate_timeline(user_id: str) -> int:
        """
        Invalidate all timeline cache entries for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Number of cache entries deleted
        """
        pattern = CacheService._generate_key("timeline", user_id, "*")
        deleted = redis_client.delete_pattern(pattern)
        
        if deleted > 0:
            logger.info(f"🗑️  Invalidated {deleted} timeline cache entries for user {user_id}")
        
        return deleted
    
    # ========== DASHBOARD CACHING ==========
    
    @staticmethod
    def get_dashboard(
        user_id: str,
        date: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached dashboard stats
        
        Args:
            user_id: User ID
            date: Date in YYYY-MM-DD format (default: today)
            
        Returns:
            Cached dashboard data or None if not found
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        key = CacheService._generate_key("dashboard", user_id, date)
        
        cached = redis_client.get(key)
        if cached:
            logger.info(f"⚡ Cache HIT: Dashboard for user {user_id} on {date}")
        else:
            logger.info(f"💨 Cache MISS: Dashboard for user {user_id} on {date}")
        
        return cached
    
    @staticmethod
    def set_dashboard(
        user_id: str,
        data: Dict[str, Any],
        date: Optional[str] = None,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Cache dashboard stats
        
        Args:
            user_id: User ID
            data: Dashboard data to cache
            date: Date in YYYY-MM-DD format (default: today)
            ttl: Time-to-live in seconds (default: DASHBOARD_TTL)
            
        Returns:
            True if successful, False otherwise
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        key = CacheService._generate_key("dashboard", user_id, date)
        
        success = redis_client.set(key, data, ttl or CacheService.DASHBOARD_TTL)
        
        if success:
            logger.info(f"✅ Cached dashboard for user {user_id} on {date} (TTL: {ttl or CacheService.DASHBOARD_TTL}s)")
        
        return success
    
    @staticmethod
    def invalidate_dashboard(user_id: str, date: Optional[str] = None) -> int:
        """
        Invalidate dashboard cache for a user
        
        Args:
            user_id: User ID
            date: Specific date to invalidate (default: all dates)
            
        Returns:
            Number of cache entries deleted
        """
        if date:
            key = CacheService._generate_key("dashboard", user_id, date)
            deleted = 1 if redis_client.delete(key) else 0
        else:
            pattern = CacheService._generate_key("dashboard", user_id, "*")
            deleted = redis_client.delete_pattern(pattern)
        
        if deleted > 0:
            logger.info(f"🗑️  Invalidated {deleted} dashboard cache entries for user {user_id}")
        
        return deleted
    
    # ========== CHAT HISTORY CACHING ==========
    
    @staticmethod
    def get_chat_history(
        user_id: str,
        limit: int = 20,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached chat history
        
        Args:
            user_id: User ID
            limit: Number of messages to retrieve
            
        Returns:
            Cached chat history or None if not found
        """
        key = CacheService._generate_key("chat_history", user_id, limit)
        
        cached = redis_client.get(key)
        if cached:
            logger.info(f"⚡ Cache HIT: Chat history for user {user_id}")
        else:
            logger.info(f"💨 Cache MISS: Chat history for user {user_id}")
        
        return cached
    
    @staticmethod
    def set_chat_history(
        user_id: str,
        messages: List[Dict[str, Any]],
        limit: int = 20,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Cache chat history
        
        Args:
            user_id: User ID
            messages: Chat messages to cache
            limit: Number of messages
            ttl: Time-to-live in seconds (default: CHAT_HISTORY_TTL)
            
        Returns:
            True if successful, False otherwise
        """
        key = CacheService._generate_key("chat_history", user_id, limit)
        
        success = redis_client.set(key, messages, ttl or CacheService.CHAT_HISTORY_TTL)
        
        if success:
            logger.info(f"✅ Cached chat history for user {user_id} (TTL: {ttl or CacheService.CHAT_HISTORY_TTL}s)")
        
        return success
    
    @staticmethod
    def invalidate_chat_history(user_id: str) -> int:
        """
        Invalidate all chat history cache entries for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Number of cache entries deleted
        """
        pattern = CacheService._generate_key("chat_history", user_id, "*")
        deleted = redis_client.delete_pattern(pattern)
        
        if deleted > 0:
            logger.info(f"🗑️  Invalidated {deleted} chat history cache entries for user {user_id}")
        
        return deleted
    
    # ========== USER PROFILE CACHING ==========
    
    @staticmethod
    def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached user profile
        
        Args:
            user_id: User ID
            
        Returns:
            Cached user profile or None if not found
        """
        key = CacheService._generate_key("user_profile", user_id)
        
        cached = redis_client.get(key)
        if cached:
            logger.info(f"⚡ Cache HIT: User profile for {user_id}")
        else:
            logger.info(f"💨 Cache MISS: User profile for {user_id}")
        
        return cached
    
    @staticmethod
    def set_user_profile(
        user_id: str,
        profile: Dict[str, Any],
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Cache user profile
        
        Args:
            user_id: User ID
            profile: User profile data to cache
            ttl: Time-to-live in seconds (default: USER_PROFILE_TTL)
            
        Returns:
            True if successful, False otherwise
        """
        key = CacheService._generate_key("user_profile", user_id)
        
        success = redis_client.set(key, profile, ttl or CacheService.USER_PROFILE_TTL)
        
        if success:
            logger.info(f"✅ Cached user profile for {user_id} (TTL: {ttl or CacheService.USER_PROFILE_TTL}s)")
        
        return success
    
    @staticmethod
    def invalidate_user_profile(user_id: str) -> bool:
        """
        Invalidate user profile cache
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        key = CacheService._generate_key("user_profile", user_id)
        deleted = redis_client.delete(key)
        
        if deleted:
            logger.info(f"🗑️  Invalidated user profile cache for {user_id}")
        
        return deleted
    
    # ========== UTILITY METHODS ==========
    
    @staticmethod
    def invalidate_all_user_caches(user_id: str) -> int:
        """
        Invalidate ALL cache entries for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Total number of cache entries deleted
        """
        total_deleted = 0
        
        total_deleted += CacheService.invalidate_timeline(user_id)
        total_deleted += CacheService.invalidate_dashboard(user_id)
        total_deleted += CacheService.invalidate_chat_history(user_id)
        total_deleted += (1 if CacheService.invalidate_user_profile(user_id) else 0)
        
        logger.info(f"🗑️  Invalidated {total_deleted} total cache entries for user {user_id}")
        
        return total_deleted
    
    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        return redis_client.get_stats()


# Global singleton instance
cache_service = CacheService()

