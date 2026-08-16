from pydantic import BaseModel, ConfigDict, EmailStr

from apps.schemas.role import Role

class EmployeeBase(BaseModel):
    age: int
    designation: str


class EmployeeCreate(EmployeeBase):
    # employee is backed by a User record (unique by user_id)
    user_id: int


class EmployeeRegistrationRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    designation: str
    department_id: int
    role: Role
    age: int | None = None

    model_config = ConfigDict(extra="forbid")


class EmployeeUpdate(BaseModel):
    age: int | None = None
    designation: str | None = None

    model_config = {"extra": "forbid"}

class UserSummary(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: Role
    profile_image: str | None = None


class DepartmentSummary(BaseModel):
    id: int
    name: str
    description: str


class EmployeeResponse(EmployeeBase):
    id: int
    user: UserSummary
    age: int
    designation: str
    department: DepartmentSummary
    is_active: bool

    model_config = {
        "from_attributes": True
    }


class BulkImportRowError(BaseModel):
    row: int
    email: str | None = None
    error: str


class BulkImportResponse(BaseModel):
    total_records: int
    imported_count: int
    failed_count: int
    imported_emails: list[str]
    errors: list[BulkImportRowError]
