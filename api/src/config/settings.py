from dataclasses import dataclass
import logging


@dataclass
class VectorStoreConfig:
    dimension: int = 384
    index_type: str = "Flat"
    distance_metric: str = "L2"


@dataclass
class LoggingConfig:
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "seachat.log"


def setup_logging(config: LoggingConfig = None):
    """配置全局日志"""
    if config is None:
        config = LoggingConfig()

    # 如果
    """logging.basicConfig(
        level=getattr(logging, config.level.upper()),
        format=config.format,
        filename=config.file_path if config.file_path else None,
        filemode='a'
    )"""

    # 配置
    logging.basicConfig(
        level=getattr(logging, config.level.upper()), format=config.format
    )

    logger = logging.getLogger(__name__)

    return logger


from fastapi import FastAPI, HTTPException, requests
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


vector_store_config = VectorStoreConfig()
