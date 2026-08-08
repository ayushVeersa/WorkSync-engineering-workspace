from sqlalchemy import Column, String, Integer, Text, DateTime, func
from sqlalchemy.orm import relationship

from apps.db.database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False, unique=True)

    description = Column(Text)

    employees = relationship(
        "Employee",
        back_populates="department"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
