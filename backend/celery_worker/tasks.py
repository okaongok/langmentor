from celery_worker.config import celery_app
from shared.models.base import SessionLocal, ChatSession, ChatMessage


@celery_app.task(bind=True, max_retries=3)
def persist_chat_session(self, session_id: str, messages: list):
    db = SessionLocal()
    try:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            first_user_msg = next(
                (m for m in messages if m.get("role") == "user"),
                None
            )
            title = (first_user_msg.get("content", "")[:30] + "...") if first_user_msg else "新会话"
            session = ChatSession(id=session_id, title=title)
            db.add(session)
            db.commit()

        db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()

        for idx, msg in enumerate(messages):
            chat_msg = ChatMessage(
                session_id=session_id,
                role=msg.get("role", "unknown"),
                content=msg.get("content", ""),
                sequence=idx
            )
            db.add(chat_msg)

        db.commit()
        return {"status": "success", "session_id": session_id, "message_count": len(messages)}
    except Exception as e:
        db.rollback()
        self.retry(countdown=2, exc=e)
    finally:
        db.close()
