from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query

from app.database import get_database
from app.schemas.response import Response, ErrorCode
from app.schemas.session import (
    Session, SessionCreate, SessionUpdate, SessionListItem, SessionListResponse,
    SessionFilesUpdate
)
from app.schemas.message import MessageCreate
from app.schemas.session import Message

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("", response_model=Response[Session])
async def create_session(body: SessionCreate):
    db = get_database()
    now = datetime.utcnow()
    session = Session(
        id=str(uuid4()),
        title=body.title,
        componentLib=body.componentLib,
        messages=[],
        createdAt=now,
        updatedAt=now
    )
    await db.sessions.insert_one(session.model_dump())
    return Response(data=session)


@router.get("", response_model=Response[SessionListResponse])
async def get_sessions(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100)
):
    db = get_database()
    skip = (page - 1) * pageSize
    
    total = await db.sessions.count_documents({})
    cursor = db.sessions.find({}).sort("updatedAt", -1).skip(skip).limit(pageSize)
    docs = await cursor.to_list(length=pageSize)
    
    items = [SessionListItem(**doc) for doc in docs]
    return Response(data=SessionListResponse(total=total, list=items))


@router.get("/{sessionId}", response_model=Response[Session])
async def get_session(sessionId: str):
    db = get_database()
    doc = await db.sessions.find_one({"id": sessionId})
    if not doc:
        raise HTTPException(
            status_code=404,
            detail=Response(code=ErrorCode.SESSION_NOT_FOUND, message="会话不存在").model_dump()
        )
    return Response(data=Session(**doc))


@router.delete("/{sessionId}", response_model=Response)
async def delete_session(sessionId: str):
    db = get_database()
    result = await db.sessions.delete_one({"id": sessionId})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail=Response(code=ErrorCode.SESSION_NOT_FOUND, message="会话不存在").model_dump()
        )
    return Response(message="删除成功")


@router.patch("/{sessionId}", response_model=Response)
async def update_session(sessionId: str, body: SessionUpdate):
    db = get_database()
    result = await db.sessions.update_one(
        {"id": sessionId},
        {"$set": {"title": body.title, "updatedAt": datetime.utcnow()}}
    )
    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail=Response(code=ErrorCode.SESSION_NOT_FOUND, message="会话不存在").model_dump()
        )
    return Response(message="更新成功")


@router.post("/{sessionId}/messages", response_model=Response[Message])
async def add_message(sessionId: str, body: MessageCreate):
    db = get_database()
    now = datetime.utcnow()
    message = Message(
        id=str(uuid4()),
        role=body.role,
        content=body.content,
        attachments=body.attachments,
        timestamp=now
    )
    
    result = await db.sessions.update_one(
        {"id": sessionId},
        {
            "$push": {"messages": message.model_dump()},
            "$set": {"updatedAt": now}
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail=Response(code=ErrorCode.SESSION_NOT_FOUND, message="会话不存在").model_dump()
        )
    
    return Response(data=message)


@router.delete("/{sessionId}/messages/{messageId}", response_model=Response)
async def delete_message(sessionId: str, messageId: str):
    db = get_database()
    result = await db.sessions.update_one(
        {"id": sessionId},
        {
            "$pull": {"messages": {"id": messageId}},
            "$set": {"updatedAt": datetime.utcnow()}
        }
    )
    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail=Response(code=ErrorCode.SESSION_NOT_FOUND, message="会话不存在").model_dump()
        )
    return Response(message="删除成功")


@router.patch("/{sessionId}/files", response_model=Response)
async def update_session_files(sessionId: str, body: SessionFilesUpdate):
    db = get_database()
    result = await db.sessions.update_one(
        {"id": sessionId},
        {"$set": {"files": [f.model_dump() for f in body.files], "updatedAt": datetime.utcnow()}}
    )
    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail=Response(code=ErrorCode.SESSION_NOT_FOUND, message="会话不存在").model_dump()
        )
    return Response(message="更新成功")
