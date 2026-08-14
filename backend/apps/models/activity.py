from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from apps.db.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)

    actor_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=True,  # None for automated system actions
        index=True,
    )

    action = Column(
        String(100),
        nullable=False,
        index=True,
    )

    entity_type = Column(
        String(50),
        nullable=False,
        index=True,
    )

    entity_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    metadata_json = Column(
        Text,
        nullable=True,
    )

    actor = relationship(
        "Employee",
        foreign_keys=[actor_id],
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
        nullable=False,
    )
