from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    # @classmethod
    # def validate(cls, v):
    #     if not ObjectId.is_valid(v):
    #         raise ValueError("Invalid objectid")
    #     return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

    @classmethod
    def __get_pydantic_json_schema__(cls, _schema_generator, _field_schema):
        # Update the schema to specify this is a string
        _field_schema.update(type="string")
        return _field_schema

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)


class Model(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True