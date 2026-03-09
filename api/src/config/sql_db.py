import os
from typing import Generator, Optional
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import QueuePool

Base = declarative_base()

class DatabaseConfig:
    """数据库配置类"""
    
    def __init__(self):
        self.DB_HOST = os.getenv("DB_HOST", "localhost")
        self.DB_PORT = os.getenv("DB_PORT", "5432")
        self.DB_NAME = os.getenv("DB_NAME", "pbl")
        self.DB_USER = os.getenv("DB_USER", "postgres")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
        self.DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
        self.DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        self.DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))
        self.DB_ECHO = os.getenv("DB_ECHO", "False").lower() == "true"
    
    @property
    def connection_url(self) -> str:
        """获取数据库连接URL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    def create_engine(self):
        """创建带连接池的SQLAlchemy引擎"""
        engine = create_engine(
            self.connection_url,
            # 连接池配置
            poolclass=QueuePool,
            pool_size=self.DB_POOL_SIZE,
            max_overflow=self.DB_MAX_OVERFLOW,
            pool_recycle=self.DB_POOL_RECYCLE,
            pool_pre_ping=True,
            pool_use_lifo=True,
            
            # 其他配置
            echo=self.DB_ECHO,
            echo_pool=self.DB_ECHO,
            connect_args={
                "connect_timeout": 10,
                "application_name": "my_app",
                "options": "-c timezone=Asia/Shanghai"
            }
        )
        
        # 添加连接池事件监听
        self._setup_pool_events(engine)
        
        return engine
    
    def _setup_pool_events(self, engine: Engine):
        """设置连接池事件监听"""
        
        @event.listens_for(engine, "connect")
        def connect(dbapi_connection, connection_record):
            """连接创建时的回调"""
            cursor = dbapi_connection.cursor()
            cursor.execute("SET TIME ZONE 'Asia/Shanghai'")
            cursor.close()
        
        @event.listens_for(engine, "checkout")
        def checkout(dbapi_connection, connection_record, connection_proxy):
            """从连接池检出连接时的回调"""
            pass
        
        @event.listens_for(engine, "checkin")
        def checkin(dbapi_connection, connection_record):
            """连接归还到连接池时的回调"""
            pass
        
        @event.listens_for(engine, "close")
        def close(dbapi_connection, connection_record):
            """连接关闭时的回调"""
            pass

class DatabaseManager:
    """数据库管理器（单例模式）"""
    
    _instance: Optional['DatabaseManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.config = DatabaseConfig()
            self.engine = self.config.create_engine()
            self.SessionLocal = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
                class_=Session
            )
            self._initialized = True
    
    def create_tables(self):
        """创建所有表"""
        Base.metadata.create_all(bind=self.engine)
        print("✅ 所有表已创建")
    
    def drop_tables(self):
        """删除所有表"""
        Base.metadata.drop_all(bind=self.engine)
        print("✅ 所有表已删除")
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """上下文管理器获取会话（自动提交和回滚）"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"❌ 操作失败，已回滚: {e}")
            raise
        finally:
            session.close()

    def get_scoped_session(self):
        """获取作用域会话（适合Web应用）"""
        from sqlalchemy.orm import scoped_session
        return scoped_session(self.SessionLocal)
    
    def get_engine_stats(self) -> dict:
        """获取连接池统计信息"""
        pool = self.engine.pool
        return {
            "size": pool.size(),
            "checkedin": pool.checkedin(),
            "checkedout": pool.checkedout(),
            "overflow": pool.overflow(),
            "connections": pool.status()
        }
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            print(f"❌ 数据库健康检查失败: {e}")
            return False

# 创建全局数据库管理器单例
db_manager = DatabaseManager() 