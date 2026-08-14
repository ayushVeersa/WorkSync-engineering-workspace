import pytest
from apps.models.user import User
from apps.models.department import Department
from apps.models.employee import Employee
from apps.schemas.role import Role
from apps.services.activity import record_activity, get_activities


def test_record_and_get_activities(db):
    dept = Department(name="QA", description="QA")
    db.add(dept)
    db.commit()

    u = User(name="Alice QA", email="aliceqa@test.com", password_hash="hash", age=26, role=Role.EMPLOYEE)
    db.add(u)
    db.commit()

    emp = Employee(user_id=u.id, department_id=dept.id, designation="Tester", age=26)
    db.add(emp)
    db.commit()

    # Record system activity
    log1 = record_activity(
        db=db,
        action="TASK_CREATED",
        entity_type="issue",
        entity_id=101,
        actor_id=emp.id,
        metadata={"title": "Fix bug in login"},
    )

    log2 = record_activity(
        db=db,
        action="TASK_STATUS_CHANGED",
        entity_type="issue",
        entity_id=101,
        actor_id=emp.id,
        metadata={"old_status": "TODO", "new_status": "IN_PROGRESS"},
    )

    assert log1.id is not None
    assert log2.id is not None

    logs = get_activities(db, entity_type="issue", entity_id=101)
    assert len(logs) == 2
    assert logs[0].action == "TASK_STATUS_CHANGED"  # Latest first
    assert logs[0].actor_name == "Alice QA"
    assert logs[1].action == "TASK_CREATED"
