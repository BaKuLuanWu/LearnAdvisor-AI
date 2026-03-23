# redis_client.py
import redis
import json
import logging
from typing import Any, Optional, Union

logger = logging.getLogger(__name__)

class RedisClient:
    """Redis客户端封装（单例模式）"""
    _instance = None
    _pool = None

    # 时间常量（类属性，方便直接访问）
    ONE_MINUTE = 60
    FIVE_MINUTES = 300
    TEN_MINUTES = 600
    FIFTEEN_MINUTES = 900
    THIRTY_MINUTES = 1800
    
    ONE_HOUR = 3600
    TWO_HOURS = 7200
    THREE_HOURS = 10800
    SIX_HOURS = 21600
    TWELVE_HOURS = 43200
    
    ONE_DAY = 86400
    TWO_DAYS = 172800
    THREE_DAYS = 259200
    SEVEN_DAYS = 604800
    FIFTEEN_DAYS = 1296000
    THIRTY_DAYS = 2592000
    
    # 常用场景
    SESSION = 7200          # 2小时
    SHORT_CACHE = 600       # 10分钟
    MEDIUM_CACHE = 3600     # 1小时
    LONG_CACHE = 86400      # 1天
    
    VERIFY_CODE = 300       # 5分钟
    RESET_TOKEN = 1800      # 30分钟
    LOGIN_TOKEN = 604800    # 7天
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, host='localhost', port=6379, password=None, db=0):
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        
        # 创建连接池
        self._pool = redis.ConnectionPool(
            host=host,
            port=port,
            password=password,
            db=db,
            decode_responses=True,  # 自动解码字符串
            max_connections=50,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        
        self.client = redis.Redis(connection_pool=self._pool)
        
        # 测试连接
        try:
            self.client.ping()
            logger.info(f"Redis连接成功: {host}:{port}/{db}")
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            raise
    
    def get(self, key: str) -> Optional[str]:
        """获取字符串值"""
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Redis GET失败 [{key}]: {e}")
            return None
    
    def set(self, key: str, value: Any, expire: int = None) -> bool:
        """
        设置值（自动处理JSON序列化）
        
        Args:
            key: 键名
            value: 值（可以是任意类型）
            expire: 过期时间（秒）
        """
        try:
            # 如果不是字符串，自动JSON序列化
            if not isinstance(value, str):
                value = json.dumps(value, ensure_ascii=False)
            
            if expire:
                return self.client.setex(key, expire, value)
            else:
                return self.client.set(key, value)
        except Exception as e:
            logger.error(f"Redis SET失败 [{key}]: {e}")
            return False
    
    def delete(self, *keys) -> int:
        """删除键"""
        try:
            return self.client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis DELETE失败 [{keys}]: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS失败 [{key}]: {e}")
            return False
    
    def expire(self, key: str, seconds: int) -> bool:
        """设置过期时间"""
        try:
            return self.client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis EXPIRE失败 [{key}]: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """获取剩余过期时间"""
        try:
            return self.client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL失败 [{key}]: {e}")
            return -2
    
    def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """自增"""
        try:
            return self.client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Redis INCR失败 [{key}]: {e}")
            return None
    
    # ========== Hash操作 ==========
    def hset(self, key: str, field: str, value: Any) -> bool:
        """设置Hash字段"""
        try:
            if not isinstance(value, str):
                value = json.dumps(value, ensure_ascii=False)
            return self.client.hset(key, field, value) > 0
        except Exception as e:
            logger.error(f"Redis HSET失败 [{key}:{field}]: {e}")
            return False
    
    def hget(self, key: str, field: str) -> Optional[Any]:
        """获取Hash字段（自动反序列化）"""
        try:
            value = self.client.hget(key, field)
            if value and value.startswith(('{', '[')):
                return json.loads(value)
            return value
        except Exception as e:
            logger.error(f"Redis HGET失败 [{key}:{field}]: {e}")
            return None
    
    def hgetall(self, key: str) -> dict:
        """获取所有Hash字段"""
        try:
            data = self.client.hgetall(key)
            # 尝试反序列化JSON值
            for k, v in data.items():
                if v and v.startswith(('{', '[')):
                    try:
                        data[k] = json.loads(v)
                    except:
                        pass
            return data
        except Exception as e:
            logger.error(f"Redis HGETALL失败 [{key}]: {e}")
            return {}
    
    # ========== List操作 ==========
    def lpush(self, key: str, *values) -> int:
        """左侧推入"""
        try:
            return self.client.lpush(key, *values)
        except Exception as e:
            logger.error(f"Redis LPUSH失败 [{key}]: {e}")
            return 0
    
    def rpush(self, key: str, *values) -> int:
        """右侧推入"""
        try:
            return self.client.rpush(key, *values)
        except Exception as e:
            logger.error(f"Redis RPUSH失败 [{key}]: {e}")
            return 0
    
    def lpop(self, key: str) -> Optional[str]:
        """左侧弹出"""
        try:
            return self.client.lpop(key)
        except Exception as e:
            logger.error(f"Redis LPOP失败 [{key}]: {e}")
            return None
    
    def brpop(self, key: str, timeout: int = 0) -> Optional[tuple]:
        """阻塞右侧弹出"""
        try:
            return self.client.brpop(key, timeout)
        except Exception as e:
            logger.error(f"Redis BRPOP失败 [{key}]: {e}")
            return None
    
    # ========== 高级功能 ==========
    def cache(self, expire: int = 300):
        """
        装饰器：自动缓存函数返回值
        
        用法:
            @redis_client.cache(expire=60)
            def get_user(user_id):
                return {"id": user_id, "name": "张三"}
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                # 生成缓存key
                key = f"cache:{func.__name__}:{args}:{kwargs}"
                
                # 尝试从缓存获取
                cached = self.get(key)
                if cached is not None:
                    return cached
                
                # 执行函数
                result = func(*args, **kwargs)
                
                # 存入缓存
                if result is not None:
                    self.set(key, result, expire)
                
                return result
            return wrapper
        return decorator

# 创建全局单例
redis_client = RedisClient(
    host='localhost',
    port=6379,
    password=None,  # 如果有密码就填
    db=0
)