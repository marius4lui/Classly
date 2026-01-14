from typing import List, Optional
from sqlalchemy.orm import Session
from app import models, crud
from app.repository.base import BaseRepository
import datetime

class SqlAlchemyRepository(BaseRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: str) -> Optional[models.User]:
        return crud.get_user(self.db, user_id)

    def get_user_by_email(self, email: str) -> Optional[models.User]:
        return crud.get_user_by_email(self.db, email)

    def create_user(self, name: str, class_id: str, role: models.UserRole = models.UserRole.MEMBER, email: str = None, password: str = None) -> models.User:
        return crud.create_user(self.db, name, class_id, role, email, password)

    def register_user(self, user_id: str, email: str, password: str) -> Optional[models.User]:
        return crud.register_user(self.db, user_id, email, password)

    def delete_user(self, user_id: str) -> bool:
        return crud.delete_user(self.db, user_id)

    def get_user_by_session(self, session_token: str) -> Optional[models.User]:
        return crud.get_user_by_session(self.db, session_token)

    def get_class_members(self, class_id: str) -> List[models.User]:
        return crud.get_class_members(self.db, class_id)

    def update_user_role(self, user_id: str, role: models.UserRole) -> Optional[models.User]:
        return crud.update_user_role(self.db, user_id, role)

    def get_class(self, class_id: str) -> Optional[models.Class]:
        return crud.get_class(self.db, class_id)

    def update_class(self, class_id: str, owner_id: str = None, join_token: str = None, join_enabled: bool = None) -> Optional[models.Class]:
        c = crud.get_class(self.db, class_id)
        if c:
            if owner_id is not None: c.owner_id = owner_id
            if join_token is not None: c.join_token = join_token
            if join_enabled is not None: c.join_enabled = join_enabled
            self.db.commit()
            self.db.refresh(c)
        return c

    def create_class(self, name: str, join_token: str) -> models.Class:
        return crud.create_class(self.db, name, join_token)

    def get_class_by_token(self, join_token: str) -> Optional[models.Class]:
        return crud.get_class_by_token(self.db, join_token)
    
    def use_login_token(self, token: str) -> Optional[models.LoginToken]:
        return crud.use_login_token(self.db, token)

    def create_login_token(self, class_id: str, created_by: str, user_id: str = None, user_name: str = None, 
                           max_uses: int = None, expires_at: datetime.datetime = None, role: models.UserRole = models.UserRole.MEMBER) -> models.LoginToken:
        return crud.create_login_token(self.db, class_id, created_by, user_id, user_name, max_uses, expires_at, role)

    def delete_login_token(self, token_id: str) -> bool:
        return crud.delete_login_token(self.db, token_id)

    def list_login_tokens(self, class_id: str) -> List[models.LoginToken]:
        return self.db.query(models.LoginToken).filter(models.LoginToken.class_id == class_id).all()

    def get_events_for_class(self, class_id: str) -> List[models.Event]:
        return crud.get_events_for_class(self.db, class_id)

    def create_event(self, class_id: str, author_id: str, type: models.EventType, date: datetime.datetime, 
                     subject_id: str = None, subject_name: str = None, title: str = None, 
                     priority: models.Priority = models.Priority.MEDIUM) -> models.Event:
        return crud.create_event(self.db, class_id, author_id, type, date, subject_id, subject_name, title, priority)

    def get_event(self, event_id: str) -> Optional[models.Event]:
        return crud.get_event(self.db, event_id)

    def update_event(self, event_id: str, type: models.EventType = None, subject_name: str = None, 
                     title: str = None, date: datetime.datetime = None, priority: models.Priority = None) -> Optional[models.Event]:
        return crud.update_event(self.db, event_id, type, subject_name, title, date, priority)

    def delete_event(self, event_id: str) -> bool:
        return crud.delete_event(self.db, event_id)

    def list_events(self, class_id: str, limit: int = 100, updated_since: datetime.datetime = None, type: models.EventType = None) -> List[models.Event]:
        query = self.db.query(models.Event).filter(models.Event.class_id == class_id)
        if updated_since:
            query = query.filter(models.Event.updated_at >= updated_since)
        if type:
            query = query.filter(models.Event.type == type)
        return query.order_by(models.Event.updated_at.desc()).limit(limit).all()

    def count_events(self, class_id: str) -> int:
        return self.db.query(models.Event).filter(models.Event.class_id == class_id).count()

    def create_event_topic(self, event_id: str, topic_type: str, content: str = None, count: int = None, pages: str = None, order: int = 0, parent_id: str = None) -> models.EventTopic:
        return crud.create_event_topic(self.db, event_id, topic_type, content, count, pages, order, parent_id)

    def get_topics_for_event(self, event_id: str) -> List[models.EventTopic]:
        return crud.get_topics_for_event(self.db, event_id)

    def delete_topic(self, topic_id: str) -> bool:
        return crud.delete_topic(self.db, topic_id)

    def create_event_link(self, event_id: str, url: str, label: str) -> models.EventLink:
        return crud.create_event_link(self.db, event_id, url, label)

    def get_links_for_event(self, event_id: str) -> List[models.EventLink]:
        return self.db.query(models.EventLink).filter(models.EventLink.event_id == event_id).all()

    def delete_link(self, link_id: str) -> bool:
        return crud.delete_link(self.db, link_id)

    def create_subject(self, class_id: str, name: str, color: str = "#666666") -> models.Subject:
        return crud.create_subject(self.db, class_id, name, color)

    def get_subject(self, subject_id: str) -> Optional[models.Subject]:
        return crud.get_subject(self.db, subject_id)

    def get_subjects_for_class(self, class_id: str) -> List[models.Subject]:
        return crud.get_subjects_for_class(self.db, class_id)

    def count_subjects(self, class_id: str) -> int:
        return self.db.query(models.Subject).filter(models.Subject.class_id == class_id).count()

    def delete_subject(self, subject_id: str) -> bool:
        return crud.delete_subject(self.db, subject_id)

    def create_audit_log(self, class_id: str, user_id: str, action: models.AuditAction, 
                         target_id: str = None, data: str = None, permanent: bool = False) -> models.AuditLog:
        return crud.create_audit_log(self.db, class_id, user_id, action, target_id, data, permanent)

    def list_audit_logs(self, class_id: str, limit: int = 100) -> List[models.AuditLog]:
        return self.db.query(models.AuditLog).filter(models.AuditLog.class_id == class_id).order_by(models.AuditLog.created_at.desc()).limit(limit).all()

    def create_integration_token(self, user_id: str, class_id: str, scopes: str = "read:events", expires_at: datetime.datetime = None) -> models.IntegrationToken:
        return crud.create_integration_token(self.db, user_id, class_id, scopes, expires_at)
    
    def use_integration_token(self, token_value: str) -> Optional[models.IntegrationToken]:
        return crud.use_integration_token(self.db, token_value)
