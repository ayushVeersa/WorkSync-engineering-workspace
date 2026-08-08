from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from apps.api.auth import router as auth_router
from apps.api.employee import router as employee_router
from apps.api.department import router as department_router
from apps.api.project import router as project_router
from apps.api.employee_project import router as emp_proj_router
from apps.api.issue import router as issue_router
from apps.api.comment import router as comment_router
from apps.api.dashboard import router as dashboard_router
from apps.api.attachment import router as attachment_router


app = FastAPI()

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)

#can add lifespan of fastapi using @asynccontextmanager

app.include_router(auth_router)
app.include_router(employee_router)
app.include_router(department_router)
app.include_router(project_router)
app.include_router(emp_proj_router)
app.include_router(project_router)
app.include_router(issue_router)
app.include_router(comment_router)
app.include_router(dashboard_router)
app.include_router(attachment_router)


@app.get("/health")
def check_health():
    return {"Health":"OK"}
