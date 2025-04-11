from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId
from pydantic import GetCoreSchemaHandler, ConfigDict
from pydantic_core.core_schema import CoreSchema, ValidationInfo


# Definir PyObjectId compatible con Pydantic V2
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler: GetCoreSchemaHandler) -> CoreSchema:
        return handler(str)

    @classmethod
    def validate(cls, value: str | ObjectId, info: ValidationInfo) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)


# Modelo de usuario
class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: EmailStr
    password: str
    name: str
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
        arbitrary_types_allowed=True
    )


# Respuesta de usuario (sin contraseña)
class UserResponse(BaseModel):
    id: str = Field(alias="_id")
    email: EmailStr
    name: str
    created_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

