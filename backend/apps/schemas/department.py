from pydantic import BaseModel


class DepartmentBase(BaseModel):
    id: int
    name: str
    description: str


class DepartmentRequest(BaseModel):
    name: str
    description: str

    model_config = {
        "extra": "forbid"
    }


class DepartmentResponse(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

    model_config = {
        "extra": "forbid"
    }
