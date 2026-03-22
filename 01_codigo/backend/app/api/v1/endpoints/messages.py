from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.message import Message
from app.models.machinery import Machinery
from app.schemas.message import MessageCreate, MessageResponse, ConversationSummary

router = APIRouter(prefix="/messages", tags=["Mensajes"])


def _build_response(msg: Message, sender: User) -> MessageResponse:
    return MessageResponse(
        id=msg.id,
        sender_id=msg.sender_id,
        sender_name=sender.full_name or sender.username,
        receiver_id=msg.receiver_id,
        machinery_id=msg.machinery_id,
        content=msg.content,
        is_read=msg.is_read,
        created_at=msg.created_at,
    )


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes enviarte un mensaje a ti mismo")

    receiver = db.query(User).filter(User.id == data.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    machinery = db.query(Machinery).filter(Machinery.id == data.machinery_id).first()
    if not machinery:
        raise HTTPException(status_code=404, detail="Maquinaria no encontrada")

    msg = Message(
        sender_id=current_user.id,
        receiver_id=data.receiver_id,
        machinery_id=data.machinery_id,
        content=data.content,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return _build_response(msg, current_user)


@router.get("/conversation/{machinery_id}/{other_user_id}", response_model=List[MessageResponse])
def get_conversation(
    machinery_id: int,
    other_user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Marcar mensajes recibidos como leidos
    db.query(Message).filter(
        Message.machinery_id == machinery_id,
        Message.sender_id == other_user_id,
        Message.receiver_id == current_user.id,
        Message.is_read == False,
    ).update({"is_read": True})
    db.commit()

    messages = (
        db.query(Message)
        .filter(
            Message.machinery_id == machinery_id,
            or_(
                and_(Message.sender_id == current_user.id, Message.receiver_id == other_user_id),
                and_(Message.sender_id == other_user_id, Message.receiver_id == current_user.id),
            ),
        )
        .order_by(Message.created_at)
        .all()
    )

    result = []
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        result.append(_build_response(msg, sender))
    return result


@router.get("/inbox", response_model=List[ConversationSummary])
def get_inbox(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    messages = (
        db.query(Message)
        .filter(
            or_(
                Message.sender_id == current_user.id,
                Message.receiver_id == current_user.id,
            )
        )
        .order_by(Message.created_at.desc())
        .all()
    )

    seen = set()
    result = []
    for msg in messages:
        other_id = msg.receiver_id if msg.sender_id == current_user.id else msg.sender_id
        key = (msg.machinery_id, other_id)
        if key in seen:
            continue
        seen.add(key)

        other_user = db.query(User).filter(User.id == other_id).first()
        machinery = db.query(Machinery).filter(Machinery.id == msg.machinery_id).first()
        unread = db.query(Message).filter(
            Message.machinery_id == msg.machinery_id,
            Message.sender_id == other_id,
            Message.receiver_id == current_user.id,
            Message.is_read == False,
        ).count()

        result.append(ConversationSummary(
            other_user_id=other_id,
            other_user_name=other_user.full_name or other_user.username if other_user else "Usuario",
            machinery_id=msg.machinery_id,
            machinery_title=machinery.title if machinery else "Maquinaria",
            last_message=msg.content[:120],
            last_message_at=msg.created_at,
            unread_count=unread,
        ))
    return result


@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = db.query(Message).filter(
        Message.receiver_id == current_user.id,
        Message.is_read == False,
    ).count()
    return {"unread": count}
