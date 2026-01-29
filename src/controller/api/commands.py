"""
Commands API endpoints.
"""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from controller.db import CommandModel, get_session
from controller.models import (
    Command,
    CommandCreate,
    CommandResponse,
    CommandStatus,
)
from controller.websocket.manager import connection_manager

router = APIRouter()


@router.post("/commands", response_model=CommandResponse, status_code=201)
async def create_command(
    command: CommandCreate,
    session: AsyncSession = Depends(get_session),
) -> CommandResponse:
    """Create a new command to be executed by the agent."""
    command_id = str(uuid.uuid4())

    db_command = CommandModel(
        id=command_id,
        type=command.type,
        content=command.content,
        priority=command.priority,
        metadata_=command.metadata,
        status=CommandStatus.PENDING,
    )

    session.add(db_command)
    await session.flush()

    # Broadcast new command to connected clients
    await connection_manager.broadcast_command_created(command_id, command.type.value)

    return CommandResponse(
        id=command_id,
        status=CommandStatus.PENDING,
        message="Command created successfully",
    )


@router.get("/commands/{command_id}", response_model=Command)
async def get_command(
    command_id: str,
    session: AsyncSession = Depends(get_session),
) -> Command:
    """Get command by ID."""
    result = await session.execute(
        select(CommandModel).where(CommandModel.id == command_id)
    )
    db_command = result.scalar_one_or_none()

    if not db_command:
        raise HTTPException(status_code=404, detail="Command not found")

    return Command(
        id=db_command.id,
        type=db_command.type,
        content=db_command.content,
        priority=db_command.priority,
        status=db_command.status,
        metadata=db_command.metadata_,
        created_at=db_command.created_at,
        updated_at=db_command.updated_at,
        completed_at=db_command.completed_at,
    )


@router.get("/commands", response_model=list[Command])
async def list_commands(
    status: Optional[CommandStatus] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    session: AsyncSession = Depends(get_session),
) -> list[Command]:
    """List commands with optional filtering."""
    query = select(CommandModel).order_by(CommandModel.created_at.desc())

    if status:
        query = query.where(CommandModel.status == status)

    query = query.limit(limit).offset(offset)
    result = await session.execute(query)
    db_commands = result.scalars().all()

    return [
        Command(
            id=cmd.id,
            type=cmd.type,
            content=cmd.content,
            priority=cmd.priority,
            status=cmd.status,
            metadata=cmd.metadata_,
            created_at=cmd.created_at,
            updated_at=cmd.updated_at,
            completed_at=cmd.completed_at,
        )
        for cmd in db_commands
    ]


@router.patch("/commands/{command_id}/cancel", response_model=CommandResponse)
async def cancel_command(
    command_id: str,
    session: AsyncSession = Depends(get_session),
) -> CommandResponse:
    """Cancel a pending command."""
    result = await session.execute(
        select(CommandModel).where(CommandModel.id == command_id)
    )
    db_command = result.scalar_one_or_none()

    if not db_command:
        raise HTTPException(status_code=404, detail="Command not found")

    if db_command.status not in [CommandStatus.PENDING, CommandStatus.PROCESSING]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel command with status: {db_command.status}",
        )

    db_command.status = CommandStatus.FAILED
    db_command.updated_at = datetime.utcnow()
    await session.flush()

    return CommandResponse(
        id=command_id,
        status=CommandStatus.FAILED,
        message="Command cancelled",
    )
