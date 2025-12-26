from typing import Optional

from bson import ObjectId
from pydantic import BaseModel
from pydantic import model_validator

from src.core.utils.time import get_datetime_str


class CreatedAtProps(BaseModel):
    created_by: Optional[str] = None
    created_at: str = get_datetime_str()


class UpdatedAtProps(BaseModel):
    updated_at: str = get_datetime_str()
    updated_by: Optional[str] = None


class CommonMethods(BaseModel):
    def model_dump_mongo(self) -> dict:
        out = self.model_dump(by_alias=True)
        if "_id" in out:
            out["_id"] = ObjectId(out["_id"])
        return out

    @model_validator(mode="before")
    def validate_id(cls, values) -> str:
        if not values:
            return values
        if "_id" in values and isinstance(values["_id"], ObjectId):
            values["id"] = str(values.pop("_id"))
        return values


class StatusResponse(BaseModel):
    status: str = "Running"
