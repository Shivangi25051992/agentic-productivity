"""
Redis Client Service - Singleton Pattern
Provides centralized Redis connection management with automatic fallback
"""

import os
import json
import logging
from typing import Optional, Any
from datetime import timedelta
import redis
from redis.exceptions import RedisError, ConnectionError

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Singleton Redis client with automatic fallback to in-memory cache
    
    Features:
    - Connection pooling
    - Automatic reconnection
    - Graceful degradation (falls back to no-cache if Redis unavailable)
    - JSON serialization/deserialization
    - TTL support
    """
    
    _instance: Optional['RedisClient'] = None
    _redis_client: Optional[redis.Redis] = None
    _enabled: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Redis connection (only once)"""
        if self._redis_client is None:
            self._initialize_connection()
    
    def _initialize_connection(self):
        """
        Initialize Redis connection with environment variables
        
        Environment Variables:
        - REDIS_HOST: Redis host (default: localhost)
        - REDIS_PORT: Redis port (default: 6379)
        - REDIS_PASSWORD: Redis password (optional)
        - REDIS_DB: Redis database number (default: 0)
        - REDIS_ENABLED: Enable/disable Redis (default: true)
        """
        try:
            # Check if Redis is enabled
            redis_enabled = os.getenv('REDIS_ENABLED', 'true').lower() == 'true'
            
            if not redis_enabled:
                logger.info("🔴 Redis disabled via REDIS_ENABLED=false")
                self._enabled = False
                return
            
            # Get Redis configuration from environment
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', '6379'))
            redis_password = os.getenv('REDIS_PASSWORD', None)
            redis_db = int(os.getenv('REDIS_DB', '0'))
            
            # Create connection pool
            pool = redis.ConnectionPool(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                db=redis_db,
                decode_responses=True,  # Auto-decode bytes to strings
                max_connections=10,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
            )
            
            # Create Redis client
            self._redis_client = redis.Redis(connection_pool=pool)
            
            # Test connection
            self._redis_client.ping()
            self._enabled = True
            
            logger.info(f"✅ Redis connected: {redis_host}:{redis_port} (db={redis_db})")
            
        except (RedisError, ConnectionError) as e:
            logger.warning(f"⚠️  Redis connection failed: {e}. Falling back to no-cache mode.")
            self._redis_client = None
            self._enabled = False
        except Exception as e:
            logger.error(f"❌ Redis initialization error: {e}")
            self._redis_client = None
            self._enabled = False
    
    @property
    def is_enabled(self) -> bool:
        """Check if Redis is enabled and connected"""
        return self._enabled and self._redis_client is not None
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from Redis cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value (deserialized from JSON) or None if not found/error
        """
        if not self.is_enabled:
            return None
        
        try:
            value = self._redis_client.get(key)
            if value is None:
                return None
            
            # Deserialize JSON
            return json.loads(value)
            
        except (RedisError, json.JSONDecodeError) as e:
            logger.warning(f"⚠️  Redis GET error for key '{key}': {e}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in Redis cache
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON-serialized)
            ttl: Time-to-live in seconds (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled:
            return False
        
        try:
            # Serialize to JSON
            serialized = json.dumps(value, default=str)
            
            # Set with optional TTL
            if ttl:
                self._redis_client.setex(key, ttl, serialized)
            else:
                self._redis_client.set(key, serialized)
            
            return True
            
        except (RedisError, TypeError, json.JSONEncodeError) as e:
            logger.warning(f"⚠️  Redis SET error for key '{key}': {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from Redis cache
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled:
            return False
        
        try:
            self._redis_client.delete(key)
            return True
        except RedisError as e:
            logger.warning(f"⚠️  Redis DELETE error for key '{key}': {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern
        
        Args:
            pattern: Pattern to match (e.g., "user:123:*")
            
        Returns:
            Number of keys deleted
        """
        if not self.is_enabled:
            return 0
        
        try:
            keys = self._redis_client.keys(pattern)
            if keys:
                return self._redis_client.delete(*keys)
            return 0
        except RedisError as e:
            logger.warning(f"⚠️  Redis DELETE_PATTERN error for pattern '{pattern}': {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in Redis cache
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists, False otherwise
        """
        if not self.is_enabled:
            return False
        
        try:
            return self._redis_client.exists(key) > 0
        except RedisError as e:
            logger.warning(f"⚠️  Redis EXISTS error for key '{key}': {e}")
            return False
    
    def flush_all(self) -> bool:
        """
        Flush all keys from current database (USE WITH CAUTION!)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled:
            return False
        
        try:
            self._redis_client.flushdb()
            logger.warning("⚠️  Redis database flushed!")
            return True
        except RedisError as e:
            logger.error(f"❌ Redis FLUSH error: {e}")
            return False
    
    def get_stats(self) -> dict:
        """
        Get Redis connection stats
        
        Returns:
            Dictionary with connection stats
        """
        if not self.is_enabled:
            return {
                "enabled": False,
                "connected": False,
                "error": "Redis not enabled or not connected"
            }
        
        try:
            info = self._redis_client.info()
            return {
                "enabled": True,
                "connected": True,
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0),
            }
        except RedisError as e:
            return {
                "enabled": True,
                "connected": False,
                "error": str(e)
            }


# Global singleton instance
redis_client = RedisClient()

