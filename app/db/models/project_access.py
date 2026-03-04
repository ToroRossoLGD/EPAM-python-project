from datetime import datetime
from typing import Literal

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

Role = Literal["owner", "participant"]


class ProjectAccess(Base):
    __tablename__ = "project_access"

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    role: Mapped[str] = mapped_column(String(20), nullable=False)  
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    project = relationship("Project", back_populates="accesses")