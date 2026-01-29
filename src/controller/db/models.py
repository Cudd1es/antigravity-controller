"""
SQLAlchemy ORM models for database tables.
"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from controller.db.database import Base
from controller.models.command import CommandStatus, CommandType


class CommandModel(Base):
    """Database model for commands."""

    __tablename__ = "commands"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    type: Mapped[CommandType] = mapped_column(Enum(CommandType), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[CommandStatus] = mapped_column(
        Enum(CommandStatus), default=CommandStatus.PENDING
    )
    metadata_: Mapped[Optional[dict[str, Any]]] = mapped_column(
        "metadata", JSON, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class TaskResultModel(Base):
    """Database model for task results."""

    __tablename__ = "task_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    command_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    success: Mapped[bool] = mapped_column(default=True)
    result: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    execution_time: Mapped[float] = mapped_column(default=0.0)
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
