from abc import ABC, abstractmethod
from typing import List, Optional
from app import models
import datetime

class BaseRepository(ABC):
    @abstractmethod
    def get_user(self, user_id: str) -> Optional[models.User]:
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[models.User]:
        pass

    @abstractmethod
    def create_user(self, name: str, class_id: str, role: models.UserRole = models.UserRole.MEMBER, email: str = None, password: str = None) -> models.User:
        pass
        
    @abstractmethod
    def register_user(self, user_id: str, email: str, password: str) -> Optional[models.User]:
        pass

    @abstractmethod
    def delete_user(self, user_id: str) -> bool:
        pass
    
    @abstractmethod
    def get_user_by_session(self, session_token: str) -> Optional[models.User]:
        pass
    
    @abstractmethod
    def get_class_members(self, class_id: str) -> List[models.User]:
        pass

    @abstractmethod
    def update_user_role(self, user_id: str, role: models.UserRole) -> Optional[models.User]:
        pass

    @abstractmethod
    def get_class(self, class_id: str) -> Optional[models.Class]:
        pass

    @abstractmethod
    def update_class(
        self,
        class_id: str,
        owner_id: str = None,
        join_token: str = None,
        join_enabled: bool = None,
        timetable_public_enabled: bool = None,
        timetable_public_token: str = None,
    ) -> Optional[models.Class]:
        pass

    @abstractmethod
    def create_class(self, name: str, join_token: str) -> models.Class:
        pass

    @abstractmethod
    def get_class_by_token(self, join_token: str) -> Optional[models.Class]:
        pass
    
    @abstractmethod
    def use_login_token(self, token: str) -> Optional[models.LoginToken]:
        pass

    @abstractmethod
    def create_login_token(self, class_id: str, created_by: str, user_id: str = None, user_name: str = None, 
                           max_uses: int = None, expires_at: datetime.datetime = None, role: models.UserRole = models.UserRole.MEMBER) -> models.LoginToken:
        pass

    @abstractmethod
    def delete_login_token(self, token_id: str) -> bool:
        pass

    @abstractmethod
    def list_login_tokens(self, class_id: str) -> List[models.LoginToken]:
        pass

    # --- Events ---
    @abstractmethod
    def get_events_for_class(self, class_id: str) -> List[models.Event]:
        pass

    @abstractmethod
    def create_event(self, class_id: str, author_id: str, type: models.EventType, date: datetime.datetime, 
                     subject_id: str = None, subject_name: str = None, title: str = None, 
                     priority: models.Priority = models.Priority.MEDIUM) -> models.Event:
        pass

    @abstractmethod
    def get_event(self, event_id: str) -> Optional[models.Event]:
        pass

    @abstractmethod
    def update_event(self, event_id: str, type: models.EventType = None, subject_name: str = None, 
                     title: str = None, date: datetime.datetime = None, priority: models.Priority = None) -> Optional[models.Event]:
        pass

    @abstractmethod
    def delete_event(self, event_id: str) -> bool:
        pass
        
    @abstractmethod
    def list_events(self, class_id: str, limit: int = 100, updated_since: datetime.datetime = None, type: models.EventType = None) -> List[models.Event]:
        pass

    @abstractmethod
    def count_events(self, class_id: str) -> int:
        pass

    # --- Topics ---
    @abstractmethod
    def create_event_topic(self, event_id: str, topic_type: str, content: str = None, count: int = None, pages: str = None, order: int = 0, parent_id: str = None) -> models.EventTopic:
        pass

    @abstractmethod
    def get_topics_for_event(self, event_id: str) -> List[models.EventTopic]:
        pass

    @abstractmethod
    def delete_topic(self, topic_id: str) -> bool:
        pass

    # --- Links ---
    @abstractmethod
    def create_event_link(self, event_id: str, url: str, label: str) -> models.EventLink:
        pass

    @abstractmethod
    def get_links_for_event(self, event_id: str) -> List[models.EventLink]:
        pass

    @abstractmethod
    def delete_link(self, link_id: str) -> bool:
        pass

    # --- Subjects ---
    @abstractmethod
    def create_subject(self, class_id: str, name: str, color: str = "#666666") -> models.Subject:
        pass

    @abstractmethod
    def get_subject(self, subject_id: str) -> Optional[models.Subject]:
        pass
        
    @abstractmethod
    def get_subjects_for_class(self, class_id: str) -> List[models.Subject]:
        pass

    @abstractmethod
    def count_subjects(self, class_id: str) -> int:
        pass

    @abstractmethod
    def delete_subject(self, subject_id: str) -> bool:
        pass

    # --- Audit ---
    @abstractmethod
    def create_audit_log(self, class_id: str, user_id: str, action: models.AuditAction, 
                         target_id: str = None, data: str = None, permanent: bool = False) -> models.AuditLog:
        pass

    @abstractmethod
    def list_audit_logs(self, class_id: str, limit: int = 100) -> List[models.AuditLog]:
        pass

    # --- Integration Tokens ---
    @abstractmethod
    def create_integration_token(self, user_id: str, class_id: str, scopes: str = "read:events", expires_at: datetime.datetime = None) -> models.IntegrationToken:
        pass
    
    @abstractmethod
    def use_integration_token(self, token_value: str) -> Optional[models.IntegrationToken]:
        pass
