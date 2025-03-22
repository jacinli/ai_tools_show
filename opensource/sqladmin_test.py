from sqlalchemy import Column, Integer, String, create_engine,Enum as SAEnum,JSON
from sqladmin.authentication import AuthenticationBackend
import json
import hashlib
from sqlalchemy import event

from sqlalchemy.orm import declarative_base
from enum import Enum
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()
engine = create_engine(
    "sqlite:///example.db",
    connect_args={"check_same_thread": False},
)

# 定义枚举类型
class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    gender = Column(SAEnum(GenderEnum), nullable=False, comment="性别")
    password = Column("password", String, nullable=False)  # 真实存储加密后的密码






    

class JsonConfig(Base):
    __tablename__ = "json_config"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    config = Column(JSON)

Base.metadata.create_all(engine)  # Create tables，后面改了字段需要删除


from fastapi import FastAPI
from sqladmin import Admin, ModelView
from fastapi import Request

app = FastAPI()


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        # Validate username/password credentials
        # And update session
        if username == "admin" and password == "123456":
            request.session.update({"sqladmin_token": "..."})
            return True
        else:
            return False
        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("sqladmin_token")

        if not token:
            return False

        # Check the token in depth
        return True

authentication_backend = AdminAuth(secret_key="secret_key")


admin = Admin(app, engine,base_url="/super",authentication_backend=authentication_backend)


class UserAdmin(ModelView, model=User):
    self_md5_salt = "123456"
    column_list = [User.id, User.name,User.gender,User.password]

    # 自定义列标签（让 SQLAdmin UI 显示中文）
    column_labels = {
        "id": "用户 ID",
        "name": "姓名",
        "gender": "性别",
        "password": "密码",
    }
    async def insert_model(self, request: Request, data: dict):
        """拦截插入逻辑，确保 `password` 经过 MD5 加密"""
        raw_password = data.pop("password", None)
        if raw_password:
            data["password"] = hashlib.md5((raw_password+self.self_md5_salt).encode()).hexdigest()
        return await super().insert_model(request, data)

    async def update_model(self, request: Request, pk: str, data: dict):
        """拦截更新逻辑，确保 `password` 经过 MD5 加密"""
        raw_password = data.pop("password", None)
        if raw_password:
            data["password"] = hashlib.md5((raw_password+self.self_md5_salt).encode()).hexdigest()
        return await super().update_model(request, pk, data)

class JsonConfigAdmin(ModelView, model=JsonConfig): 
    column_list = [JsonConfig.id, JsonConfig.name,JsonConfig.config]
    # 前端页面插入的时候 只能使用双引号的json 不能使用单引号的json



admin.add_view(UserAdmin)
admin.add_view(JsonConfigAdmin)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
# uvicorn test_sqladmin:app --host 127.0.0.1 --port 8000 --reload
# 后台地址： http://127.0.0.1:8000/super

# pip install itsdangerous  sqladmin 