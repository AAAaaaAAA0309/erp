from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import ChatRequest, ChatResponse
from ..auth import get_current_user
from ..models import ChatMessage
from ..ai.orchestrator import process_message

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # 1. Сохраняем сообщение пользователя в базу
    db.add(ChatMessage(user_id=user.id, role="user", content=req.message))
    db.commit()

    # 2. Достаем последние 6 сообщений (чтобы ИИ помнил контекст)
    history = db.query(ChatMessage).filter(ChatMessage.user_id == user.id).order_by(ChatMessage.id.desc()).limit(6).all()
    history.reverse() # Разворачиваем в правильном порядке (от старых к новым)

    # 3. Отправляем историю в оркестратор
    result = process_message(history, db, user)

    # 4. Сохраняем ответ ИИ
    db.add(ChatMessage(user_id=user.id, role="assistant", content=result["reply"]))
    db.commit()
    return result