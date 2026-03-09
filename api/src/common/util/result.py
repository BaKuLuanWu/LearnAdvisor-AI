from datetime import datetime
from enum import Enum
from typing import Any, Optional, TypeVar, Generic
from dataclasses import dataclass

T = TypeVar('T')  # 成功数据的泛型类型
E = TypeVar('E')  # 错误数据的泛型类型


class ResultCode(Enum):
    """返回码枚举"""
    SUCCESS = ("success", 200, "操作成功")
    ERROR = ("error", 500, "操作失败")
    WARN = ("warn", 400, "操作警告")
    
    def __init__(self, status: str, code: int, message: str):
        self.status = status
        self.code = code
        self.message = message


@dataclass
class Result(Generic[T, E]):
    """结果包装类"""
    status: str
    code: int
    message: str
    data: Optional[T] = None
    error: Optional[E] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    @classmethod
    def ok(cls, data: T = None, message: str = "操作成功") -> 'Result[T, E]':
        """成功结果"""
        return cls(
            status=ResultCode.SUCCESS.status,
            code=ResultCode.SUCCESS.code,
            message=message,
            data=data
        )
    
    @classmethod
    def error(cls, error: E = None, message: str = "操作失败") -> 'Result[T, E]':
        """失败结果"""
        return cls(
            status=ResultCode.ERROR.status,
            code=ResultCode.ERROR.code,
            message=message,
            error=error
        )
    
    @classmethod
    def warn(cls, data: T = None, message: str = "操作警告") -> 'Result[T, E]':
        """警告结果"""
        return cls(
            status=ResultCode.WARN.status,
            code=ResultCode.WARN.code,
            message=message,
            data=data
        )
    
    def is_success(self) -> bool:
        """是否成功"""
        return self.status == ResultCode.SUCCESS.status
    
    def is_error(self) -> bool:
        """是否失败"""
        return self.status == ResultCode.ERROR.status
    
    def is_warn(self) -> bool:
        """是否警告"""
        return self.status == ResultCode.WARN.status
    
    def to_dict(self) -> dict:
        """转换为字典"""
        result = {
            "status": self.status,
            "code": self.code,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }
        
        if self.data is not None:
            result["data"] = self.data
        if self.error is not None:
            result["error"] = self.error
            
        return result