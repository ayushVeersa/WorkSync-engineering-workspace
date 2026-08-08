from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    BigInteger,
    func,
)
from sqlalchemy.orm import relationship

from apps.db.database import Base


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)

    original_name = Column(String(255), nullable=False)

    stored_name = Column(String(255), nullable=False, unique=True)

    file_path = Column(String(500), nullable=False)

    content_type = Column(String(100), nullable=False)

    file_size = Column(BigInteger, nullable=False)

    issue_id = Column(
        Integer,
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
    )

    uploaded_by = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    issue = relationship(
        "Issue",
        back_populates="attachments",
    )

    employee = relationship(
        "Employee",
    )