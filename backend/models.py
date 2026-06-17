"""学生数据模型"""
from pydantic import BaseModel, Field
from typing import Optional


class StudentCreate(BaseModel):
    """创建学生的请求体"""
    name: str = Field(..., min_length=1, max_length=50, description="姓名")
    gender: str = Field(default="男", description="性别")
    age: int = Field(default=20, ge=10, le=50, description="年龄")
    major: str = Field(default="计算机科学与技术", max_length=100, description="专业")
    class_name: str = Field(default="", max_length=100, description="班级")
    phone: str = Field(default="", max_length=20, description="手机号")
    email: str = Field(default="", max_length=100, description="邮箱")


class StudentUpdate(BaseModel):
    """更新学生的请求体"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    gender: Optional[str] = None
    age: Optional[int] = Field(None, ge=10, le=50)
    major: Optional[str] = Field(None, max_length=100)
    class_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)


class StudentResponse(BaseModel):
    """学生响应体"""
    id: int
    name: str
    gender: str
    age: int
    major: str
    class_name: str
    phone: str
    email: str
    created_at: str
