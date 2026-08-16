import csv
import io
import zipfile
import xml.etree.ElementTree as ET
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from apps.models.employee import Employee
from apps.models.user import User
from apps.models.department import Department
from apps.schemas.role import Role
from apps.schemas.employee import (
    EmployeeUpdate,
    EmployeeRegistrationRequest,
    BulkImportResponse,
    BulkImportRowError,
)
from apps.schemas.user import UserRegister
from apps.core.mail import queue_employee_welcome_email
from apps.services.user_service import create_user
from apps.core.logging import get_logger

logger = get_logger(__name__)


def get_employee(db: Session, employee_id: int) -> Employee:

    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if not employee:
        logger.warning("Employee not found for id=%s", employee_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    logger.info("Fetched employee id=%s", employee_id)
    return employee


def get_employee_by_user_id(
    db: Session,
    user_id: int
) -> Employee:
    employee = (
        db.query(Employee)
        .filter(Employee.user_id == user_id)
        .first()
    )

    if employee is None:
        logger.warning("Employee not found for user_id=%s", user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )
    logger.info("Fetched employee id=%s for user_id=%s", employee.id, user_id)
    return employee


def get_employees(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    department_id: int | None = None,
):
    query = (
        db.query(Employee)
        .filter(Employee.is_active.is_(True))
    )

    if search:
        query = query.join(Employee.user).filter(
            User.name.ilike(f"%{search}%")
            | Employee.designation.ilike(f"%{search}%")
        )

    if department_id is not None:
        query = query.filter(Employee.department_id == department_id)

    employees = (
        query.offset(skip)
        .limit(limit)
        .all()
    )

    logger.info(
        "Fetched employees list, count=%s, skip=%s, limit=%s, search=%s, department_id=%s",
        len(employees),
        skip,
        limit,
        search,
        department_id,
    )
    return employees


def create_employee(
    db: Session,
    payload: EmployeeRegistrationRequest,
) -> Employee:

    # Find/create the backing User
    existing_user = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    if existing_user is None:
        user = create_user(
            UserRegister(
                name=payload.name,
                email=payload.email,
                password=payload.password,
                age=payload.age,
                role=payload.role,
            ),
            db,
        )
    else:
        user = existing_user

    logger.info("Resolved backing user id=%s for employee registration email=%s", user.id, payload.email)

    department = (
        db.query(Department)
        .filter(Department.id == payload.department_id)
        .first()
    )

    if department is None:
        logger.warning("Department not found for id=%s while creating employee", payload.department_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
    )

    existing_employee = (
        db.query(Employee)
        .filter(Employee.user_id == user.id)
        .first()
    )

    if existing_employee:
        logger.warning("Employee already exists for user_id=%s", user.id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee already exists",
        )

    employee = Employee(
        user_id=user.id,
        age=payload.age or 0,
        designation=payload.designation,
        department_id=payload.department_id
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    logger.info("Created employee id=%s for user_id=%s", employee.id, user.id)

    queue_employee_welcome_email(
        recipient=employee.user.email,
        name=employee.user.name,
        designation=employee.designation,
        department=employee.department.name,
    )

    return employee


def update_employee(
    db: Session,
    employee_id: int,
    employee_update: EmployeeUpdate,
) -> Employee:

    employee = get_employee(db, employee_id)

    update_data = employee_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(employee, key, value)

    db.commit()
    db.refresh(employee)

    logger.info("Updated employee id=%s with fields=%s", employee_id, list(update_data.keys()))
    return employee


def delete_employee(db: Session, employee_id: int):

    employee = get_employee(db, employee_id)

    employee.is_active = False

    db.commit()

    logger.info("Soft-deleted employee id=%s", employee_id)
    return {
        "message": "Employee deleted successfully"
    }


def _parse_csv_records(file_content: bytes) -> list[dict[str, str]]:
    text = file_content.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    records = []
    for row in reader:
        records.append({k.strip(): (v.strip() if v else "") for k, v in row.items() if k})
    return records


def _parse_xlsx_records(file_content: bytes) -> list[dict[str, str]]:
    with zipfile.ZipFile(io.BytesIO(file_content)) as z:
        shared_strings = []
        if "xl/sharedStrings.xml" in z.namelist():
            tree = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for elem in tree.iter():
                if elem.tag.endswith("t"):
                    shared_strings.append(elem.text or "")

        sheet_names = [n for n in z.namelist() if n.startswith("xl/worksheets/sheet")]
        if not sheet_names:
            return []

        sheet_tree = ET.fromstring(z.read(sheet_names[0]))
        rows = []
        for row_elem in sheet_tree.iter():
            if row_elem.tag.endswith("row"):
                row_cells = []
                for cell_elem in row_elem.iter():
                    if cell_elem.tag.endswith("c"):
                        val_type = cell_elem.attrib.get("t")
                        val_elem = None
                        for child in cell_elem:
                            if child.tag.endswith("v"):
                                val_elem = child
                                break
                        val = ""
                        if val_elem is not None and val_elem.text is not None:
                            val = val_elem.text
                            if val_type == "s" and val.isdigit():
                                idx = int(val)
                                if idx < len(shared_strings):
                                    val = shared_strings[idx]
                        row_cells.append(val.strip())
                if any(row_cells):
                    rows.append(row_cells)

        if not rows:
            return []
        headers = [str(h).strip() for h in rows[0]]
        records = []
        for row in rows[1:]:
            row_dict = {}
            for i, h in enumerate(headers):
                if h:
                    row_dict[h] = row[i] if i < len(row) else ""
            if any(row_dict.values()):
                records.append(row_dict)
        return records


def bulk_import_employees(
    db: Session,
    file_content: bytes,
    filename: str,
) -> BulkImportResponse:
    if filename.lower().endswith(".xlsx") or file_content.startswith(b"PK"):
        records = _parse_xlsx_records(file_content)
    else:
        records = _parse_csv_records(file_content)

    total_records = len(records)
    imported_emails: list[str] = []
    errors: list[BulkImportRowError] = []

    seen_emails_in_file = set()

    for idx, raw_row in enumerate(records, start=2):
        # Normalize key names
        normalized_row = {}
        for k, v in raw_row.items():
            key_clean = k.lower().replace(" ", "").replace("_", "")
            if key_clean in ["name", "fullname", "employeename", "username", "membername"]:
                normalized_row["name"] = v
            elif key_clean in ["email", "emailaddress", "mail"]:
                normalized_row["email"] = v.lower()
            elif key_clean in ["designation", "jobtitle", "title", "position"]:
                normalized_row["designation"] = v
            elif key_clean in ["department", "departmentid", "dept", "deptid"]:
                normalized_row["department"] = v
            elif key_clean in ["role", "systemrole", "userrole"]:
                normalized_row["role"] = v.upper()
            elif key_clean in ["password", "pass"]:
                normalized_row["password"] = v
            elif key_clean in ["age"]:
                normalized_row["age"] = v

        name = normalized_row.get("name", "").strip()
        email = normalized_row.get("email", "").strip()
        designation = normalized_row.get("designation", "").strip()
        dept_val = normalized_row.get("department", "").strip()
        role_val = normalized_row.get("role", "").strip() or "EMPLOYEE"
        password = normalized_row.get("password", "").strip() or "WorkSync@123"
        age_str = normalized_row.get("age", "").strip()

        # Validate required fields
        if not name:
            errors.append(BulkImportRowError(row=idx, email=email or None, error="Missing required field: Name"))
            continue
        if not email or "@" not in email or "." not in email:
            errors.append(BulkImportRowError(row=idx, email=email or None, error="Invalid email address format"))
            continue
        if not designation:
            errors.append(BulkImportRowError(row=idx, email=email, error="Missing required field: Designation"))
            continue
        if not dept_val:
            errors.append(BulkImportRowError(row=idx, email=email, error="Missing required field: Department"))
            continue

        # Validate role
        if role_val not in Role.__members__:
            errors.append(BulkImportRowError(row=idx, email=email, error=f"Invalid role '{role_val}'. Allowed roles: EMPLOYEE, MANAGER, ADMIN"))
            continue
        role_enum = Role[role_val]

        # Duplicate email check within file
        if email in seen_emails_in_file:
            errors.append(BulkImportRowError(row=idx, email=email, error=f"Duplicate email '{email}' in input file"))
            continue
        seen_emails_in_file.add(email)

        # Department resolution
        department = None
        if dept_val.isdigit():
            department = db.query(Department).filter(Department.id == int(dept_val)).first()
        if not department:
            department = db.query(Department).filter(func.lower(Department.name) == dept_val.lower()).first()

        if not department:
            errors.append(BulkImportRowError(row=idx, email=email, error=f"Department '{dept_val}' not found"))
            continue

        # Parse age
        age = 25
        if age_str:
            try:
                age = int(age_str)
            except ValueError:
                pass

        # Duplicate check in DB
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            existing_emp = db.query(Employee).filter(Employee.user_id == existing_user.id).first()
            if existing_emp:
                errors.append(BulkImportRowError(row=idx, email=email, error=f"Employee already exists for email '{email}'"))
                continue
            # If user exists but employee record does not:
            user = existing_user
        else:
            try:
                user = create_user(
                    UserRegister(
                        name=name,
                        email=email,
                        password=password,
                        age=age,
                        role=role_enum,
                    ),
                    db,
                )
            except Exception as exc:
                errors.append(BulkImportRowError(row=idx, email=email, error=f"Failed to create user account: {str(exc)}"))
                continue

        try:
            employee = Employee(
                user_id=user.id,
                age=age,
                designation=designation,
                department_id=department.id,
            )
            db.add(employee)
            db.commit()
            db.refresh(employee)

            queue_employee_welcome_email(
                recipient=user.email,
                name=user.name,
                designation=employee.designation,
                department=department.name,
            )
            imported_emails.append(email)
            logger.info("Bulk imported employee id=%s email=%s", employee.id, email)
        except Exception as exc:
            db.rollback()
            errors.append(BulkImportRowError(row=idx, email=email, error=f"Database error registering employee: {str(exc)}"))

    return BulkImportResponse(
        total_records=total_records,
        imported_count=len(imported_emails),
        failed_count=len(errors),
        imported_emails=imported_emails,
        errors=errors,
    )

