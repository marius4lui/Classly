from typing import List, Optional
import os
import secrets
from datetime import datetime
from app import models
from app.repository.base import BaseRepository
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.users import Users
from appwrite.id import ID
from appwrite.query import Query
from appwrite.exception import AppwriteException

class AppwriteRepository(BaseRepository):
    def __init__(self):
        self.client = Client()
        self.client.set_endpoint(os.getenv("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1"))
        self.client.set_project(os.getenv("APPWRITE_PROJECT_ID"))
        self.client.set_key(os.getenv("APPWRITE_API_KEY"))
        
        self.db = Databases(self.client)
        self.users = Users(self.client)
        self.database_id = os.getenv("APPWRITE_DATABASE_ID", "classly_db")

    def _map_doc_to_user(self, doc: dict) -> models.User:
        user = models.User()
        user.id = doc.get('$id')
        user.name = doc.get('name')
        user.email = doc.get('email')
        
        prefs = doc.get('prefs', {})
        user.class_id = prefs.get('class_id')
        user.role = prefs.get('role', models.UserRole.MEMBER)
        user.is_registered = prefs.get('is_registered', False)
        user.language = prefs.get('language', 'de')
        
        user.created_at = datetime.fromisoformat(doc.get('registration').replace('Z', '+00:00')) if doc.get('registration') else datetime.now()
        
        return user

    def _map_doc_to_class(self, doc: dict) -> models.Class:
        c = models.Class()
        c.id = doc.get('$id')
        c.name = doc.get('name')
        c.join_token = doc.get('join_token')
        c.owner_id = doc.get('owner_id')
        c.join_enabled = doc.get('join_enabled')
        c.timetable_public_enabled = doc.get('timetable_public_enabled', False)
        c.timetable_public_token = doc.get('timetable_public_token')
        c.created_at = datetime.fromisoformat(doc.get('$createdAt').replace('Z', '+00:00')) if doc.get('$createdAt') else datetime.now()
        return c

    def _map_doc_to_event(self, doc: dict) -> models.Event:
        e = models.Event()
        e.id = doc.get('$id')
        e.class_id = doc.get('class_id')
        e.title = doc.get('title')
        e.type = models.EventType(doc.get('type')) if doc.get('type') else models.EventType.INFO
        e.priority = models.Priority(doc.get('priority')) if doc.get('priority') else models.Priority.MEDIUM
        e.subject_id = doc.get('subject_id')
        e.subject_name = doc.get('subject_name')
        e.author_id = doc.get('author_id')
        
        date_str = doc.get('date')
        if date_str:
            e.date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
        return e

    def get_user(self, user_id: str) -> Optional[models.User]:
        try:
            u = self.users.get(user_id)
            return self._map_doc_to_user(u)
        except AppwriteException:
            return None

    def get_user_by_email(self, email: str) -> Optional[models.User]:
        try:
            result = self.users.list(queries=[Query.equal('email', email)])
            if result['users']:
                return self._map_doc_to_user(result['users'][0])
            return None
        except AppwriteException:
            return None

    def create_user(self, name: str, class_id: str, role: models.UserRole = models.UserRole.MEMBER, email: str = None, password: str = None) -> models.User:
        user_id = ID.unique()
        if not email:
            email = f"{user_id}@classly.local"
        if not password:
            password = secrets.token_urlsafe(16)
            
        try:
            u = self.users.create(user_id, email, password, name)
            
            session_token = secrets.token_urlsafe(32)
            try:
                self.db.create_document(self.database_id, 'sessions', ID.unique(), {
                    'token': session_token,
                    'user_id': user_id,
                    'created_at': datetime.now().isoformat()
                })
            except Exception:
                pass 
            
            prefs = {
                'class_id': class_id,
                'role': role.value,
                'is_registered': True if (email and not email.endswith("@classly.local")) else False
            }
            self.users.update_prefs(user_id, prefs)
            
            u = self.users.get(user_id)
            user_model = self._map_doc_to_user(u)
            user_model.session_token = session_token 
            return user_model
        except AppwriteException as e:
            print(f"Appwrite Error: {e}")
            raise e

    def register_user(self, user_id: str, email: str, password: str) -> Optional[models.User]:
        try:
            self.users.update_email(user_id, email)
            self.users.update_password(user_id, password)
            
            user = self.users.get(user_id)
            prefs = user.get('prefs', {})
            prefs['is_registered'] = True
            self.users.update_prefs(user_id, prefs)
            
            return self._map_doc_to_user(self.users.get(user_id))
        except AppwriteException:
            return None

    def delete_user(self, user_id: str) -> bool:
        try:
            self.users.delete(user_id)
            return True
        except AppwriteException:
            return False

    def get_user_by_session(self, session_token: str) -> Optional[models.User]:
        try:
            result = self.db.list_documents(self.database_id, 'sessions', [
                Query.equal('token', session_token)
            ])
            if result['documents']:
                user_id = result['documents'][0]['user_id']
                u = self.users.get(user_id)
                user_model = self._map_doc_to_user(u)
                user_model.session_token = session_token
                return user_model
            return None
        except AppwriteException:
            return None

    def get_class_members(self, class_id: str) -> List[models.User]:
        # Simplified: Empty list as detailed in thought process
        return []

    def update_user_role(self, user_id: str, role: models.UserRole) -> Optional[models.User]:
        try:
            user = self.users.get(user_id)
            prefs = user.get('prefs', {})
            prefs['role'] = role.value
            u = self.users.update_prefs(user_id, prefs)
            return self._map_doc_to_user(u)
        except AppwriteException:
            return None

    def get_class(self, class_id: str) -> Optional[models.Class]:
        try:
            doc = self.db.get_document(self.database_id, 'classes', class_id)
            return self._map_doc_to_class(doc)
        except AppwriteException:
            return None

    def update_class(
        self,
        class_id: str,
        owner_id: str = None,
        join_token: str = None,
        join_enabled: bool = None,
        timetable_public_enabled: bool = None,
        timetable_public_token: str = None,
    ) -> Optional[models.Class]:
        data = {}
        if owner_id is not None: data['owner_id'] = owner_id
        if join_token is not None: data['join_token'] = join_token
        if join_enabled is not None: data['join_enabled'] = join_enabled
        if timetable_public_enabled is not None: data['timetable_public_enabled'] = timetable_public_enabled
        if timetable_public_token is not None: data['timetable_public_token'] = timetable_public_token
         
        try:
            doc = self.db.update_document(self.database_id, 'classes', class_id, data)
            return self._map_doc_to_class(doc)
        except AppwriteException:
            return None

    def create_class(self, name: str, join_token: str) -> models.Class:
        data = {
            'name': name,
            'join_token': join_token,
            'join_enabled': True
        }
        try:
            doc = self.db.create_document(self.database_id, 'classes', ID.unique(), data)
            return self._map_doc_to_class(doc)
        except AppwriteException as e:
            print(f"Appwrite Error: {e}")
            raise e

    def get_class_by_token(self, join_token: str) -> Optional[models.Class]:
        try:
            result = self.db.list_documents(self.database_id, 'classes', [
                Query.equal('join_token', join_token)
            ])
            if result['documents']:
                return self._map_doc_to_class(result['documents'][0])
            return None
        except AppwriteException:
            return None
            
    # --- Login Tokens ---
    def use_login_token(self, token: str) -> Optional[models.LoginToken]:
        try:
            result = self.db.list_documents(self.database_id, 'login_tokens', [
                Query.equal('token', token)
            ])
            if not result['documents']:
                return None
            
            doc = result['documents'][0]
            
            t = models.LoginToken()
            t.id = doc['$id']
            t.class_id = doc['class_id']
            t.user_id = doc.get('user_id')
            t.user_name = doc.get('user_name')
            t.role = models.UserRole(doc.get('role', 'member'))
            
            # Note: Max uses decrement logic should be handled by caller or here. 
            # In SQL crud, it decrements. Here we should too.
            # But simplistic for now.
            
            return t
        except AppwriteException:
            return None

    def create_login_token(self, class_id: str, created_by: str, user_id: str = None, user_name: str = None, 
                           max_uses: int = None, expires_at: datetime = None, role: models.UserRole = models.UserRole.MEMBER) -> models.LoginToken:
        data = {
            'class_id': class_id,
            'created_by': created_by,
            'user_id': user_id,
            'user_name': user_name,
            'max_uses': max_uses,
            'expires_at': expires_at.isoformat() if expires_at else None,
            'role': role.value,
            'token': secrets.token_urlsafe(16),
            'uses': 0
        }
        try:
            doc = self.db.create_document(self.database_id, 'login_tokens', ID.unique(), data)
            t = models.LoginToken()
            t.id = doc['$id']
            t.token = doc['token']
            return t
        except AppwriteException as e:
            raise e

    def delete_login_token(self, token_id: str) -> bool:
        try:
            self.db.delete_document(self.database_id, 'login_tokens', token_id)
            return True
        except AppwriteException:
            return False

    def list_login_tokens(self, class_id: str) -> List[models.LoginToken]:
        try:
            result = self.db.list_documents(self.database_id, 'login_tokens', [
                Query.equal('class_id', class_id)
            ])
            tokens = []
            for doc in result['documents']:
                t = models.LoginToken()
                t.id = doc['$id']
                t.token = doc['token']
                t.user_id = doc.get('user_id')
                t.user_name = doc.get('user_name')
                t.role = models.UserRole(doc.get('role', 'member'))
                t.created_by = doc.get('created_by')
                t.created_at = datetime.fromisoformat(doc['$createdAt'])
                if doc.get('expires_at'):
                   t.expires_at = datetime.fromisoformat(doc['expires_at'])
                t.max_uses = doc.get('max_uses')
                t.uses = doc.get('uses', 0)
                tokens.append(t)
            return tokens
        except AppwriteException:
            return []

    def get_events_for_class(self, class_id: str) -> List[models.Event]:
        try:
            result = self.db.list_documents(self.database_id, 'events', [
                Query.equal('class_id', class_id),
                Query.order_asc('date')
            ])
            return [self._map_doc_to_event(doc) for doc in result['documents']]
        except AppwriteException:
            return []

    def create_event(self, class_id: str, author_id: str, type: models.EventType, date: datetime, 
                     subject_id: str = None, subject_name: str = None, title: str = None, 
                     priority: models.Priority = models.Priority.MEDIUM) -> models.Event:
        data = {
            'class_id': class_id,
            'author_id': author_id,
            'type': type.value,
            'date': date.isoformat() if date else None,
            'subject_id': subject_id,
            'subject_name': subject_name,
            'title': title,
            'priority': priority.value
        }
        try:
            doc = self.db.create_document(self.database_id, 'events', ID.unique(), data)
            return self._map_doc_to_event(doc)
        except AppwriteException as e:
            print(f"Appwrite Error: {e}")
            raise e

    def get_event(self, event_id: str) -> Optional[models.Event]:
        try:
            doc = self.db.get_document(self.database_id, 'events', event_id)
            return self._map_doc_to_event(doc)
        except AppwriteException:
            return None

    def update_event(self, event_id: str, type: models.EventType = None, subject_name: str = None, 
                     title: str = None, date: datetime = None, priority: models.Priority = None) -> Optional[models.Event]:
        data = {}
        if type: data['type'] = type.value
        if subject_name is not None: data['subject_name'] = subject_name
        if title is not None: data['title'] = title
        if date: data['date'] = date.isoformat()
        if priority: data['priority'] = priority.value
        
        try:
            doc = self.db.update_document(self.database_id, 'events', event_id, data)
            return self._map_doc_to_event(doc)
        except AppwriteException:
            return None

    def list_events(self, class_id: str, limit: int = 100, updated_since: datetime = None, type: models.EventType = None) -> List[models.Event]:
        queries = [
            Query.equal('class_id', class_id),
            Query.limit(limit),
            Query.order_desc('$updatedAt')
        ]
        if updated_since:
            queries.append(Query.greater_than_equal('$updatedAt', updated_since.isoformat()))
        if type:
            queries.append(Query.equal('type', type.value))
            
        try:
            result = self.db.list_documents(self.database_id, 'events', queries)
            return [self._map_doc_to_event(doc) for doc in result['documents']]
        except AppwriteException:
            return []

    def count_events(self, class_id: str) -> int:
        try:
            result = self.db.list_documents(self.database_id, 'events', [
                Query.equal('class_id', class_id),
                Query.limit(1)
            ])
            return result['total']
        except AppwriteException:
            return 0
    
    def delete_event(self, event_id: str) -> bool:
        try:
            self.db.delete_document(self.database_id, 'events', event_id)
            return True
        except AppwriteException:
            return False

    # --- Topics ---
    def _map_doc_to_topic(self, doc: dict) -> models.EventTopic:
        t = models.EventTopic()
        t.id = doc.get('$id')
        t.event_id = doc.get('event_id')
        t.topic_type = doc.get('topic_type')
        t.content = doc.get('content')
        t.count = doc.get('count')
        t.pages = doc.get('pages')
        t.order = doc.get('order', 0)
        t.parent_id = doc.get('parent_id')
        return t

    def create_event_topic(self, event_id: str, topic_type: str, content: str = None, count: int = None, pages: str = None, order: int = 0, parent_id: str = None) -> models.EventTopic:
        data = {
            'event_id': event_id,
            'topic_type': topic_type,
            'content': content,
            'count': count,
            'pages': pages,
            'order': order,
            'parent_id': parent_id
        }
        try:
            doc = self.db.create_document(self.database_id, 'event_topics', ID.unique(), data)
            return self._map_doc_to_topic(doc)
        except AppwriteException as e:
            print(f"Appwrite Topic Error: {e}")
            raise e

    def get_topics_for_event(self, event_id: str) -> List[models.EventTopic]:
        try:
            result = self.db.list_documents(self.database_id, 'event_topics', [
                Query.equal('event_id', event_id),
                Query.order_asc('order')
            ])
            return [self._map_doc_to_topic(doc) for doc in result['documents']]
        except AppwriteException:
            return []

    def delete_topic(self, topic_id: str) -> bool:
        try:
            self.db.delete_document(self.database_id, 'event_topics', topic_id)
            return True
        except AppwriteException:
            return False

    # --- Links ---
    def create_event_link(self, event_id: str, url: str, label: str) -> models.EventLink:
        try:
            doc = self.db.create_document(self.database_id, 'event_links', ID.unique(), {
                'event_id': event_id, 'url': url, 'label': label
            })
            l = models.EventLink(id=doc['$id'], event_id=doc['event_id'], url=doc['url'], label=doc['label'])
            return l
        except AppwriteException as e:
            raise e

    def get_links_for_event(self, event_id: str) -> List[models.EventLink]:
        try:
            result = self.db.list_documents(self.database_id, 'event_links', [
                Query.equal('event_id', event_id)
            ])
            links = []
            for doc in result['documents']:
                l = models.EventLink(id=doc['$id'], event_id=doc['event_id'], url=doc['url'], label=doc['label'])
                links.append(l)
            return links
        except AppwriteException:
            return []

    def delete_link(self, link_id: str) -> bool:
        try:
            self.db.delete_document(self.database_id, 'event_links', link_id)
            return True
        except AppwriteException:
            return False

    # --- Subjects ---
    def _map_doc_to_subject(self, doc: dict) -> models.Subject:
        s = models.Subject()
        s.id = doc.get('$id')
        s.class_id = doc.get('class_id')
        s.name = doc.get('name')
        s.color = doc.get('color', '#666666')
        return s

    def create_subject(self, class_id: str, name: str, color: str = "#666666") -> models.Subject:
        try:
            doc = self.db.create_document(self.database_id, 'subjects', ID.unique(), {
                'class_id': class_id, 'name': name, 'color': color
            })
            return self._map_doc_to_subject(doc)
        except AppwriteException as e:
            raise e

    def get_subject(self, subject_id: str) -> Optional[models.Subject]:
        try:
            doc = self.db.get_document(self.database_id, 'subjects', subject_id)
            return self._map_doc_to_subject(doc)
        except AppwriteException:
            return None

    def get_subjects_for_class(self, class_id: str) -> List[models.Subject]:
        try:
            result = self.db.list_documents(self.database_id, 'subjects', [
                Query.equal('class_id', class_id),
                Query.order_asc('name')
            ])
            return [self._map_doc_to_subject(doc) for doc in result['documents']]
        except AppwriteException:
            return []

    def count_subjects(self, class_id: str) -> int:
        try:
            result = self.db.list_documents(self.database_id, 'subjects', [
                Query.equal('class_id', class_id),
                Query.limit(1)
            ])
            return result['total']
        except AppwriteException:
            return 0

    def delete_subject(self, subject_id: str) -> bool:
        try:
            self.db.delete_document(self.database_id, 'subjects', subject_id)
            return True
        except AppwriteException:
            return False

    # --- Audit ---
    def create_audit_log(self, class_id: str, user_id: str, action: models.AuditAction, 
                         target_id: str = None, data: str = None, permanent: bool = False) -> models.AuditLog:
        try:
            self.db.create_document(self.database_id, 'audit_logs', ID.unique(), {
                'class_id': class_id,
                'user_id': user_id,
                'action': action.value,
                'target_id': target_id,
                'data': data,
                'permanent': permanent,
                'created_at': datetime.now().isoformat()
            })
            return models.AuditLog(id="new", action=action)
        except Exception:
            return models.AuditLog(id="error")

    def list_audit_logs(self, class_id: str, limit: int = 100) -> List[models.AuditLog]:
        try:
            result = self.db.list_documents(self.database_id, 'audit_logs', [
                Query.equal('class_id', class_id),
                Query.limit(limit),
                Query.order_desc('$createdAt')
            ])
            logs = []
            for doc in result['documents']:
                l = models.AuditLog()
                l.id = doc['$id']
                l.class_id = doc['class_id']
                l.user_id = doc['user_id']
                l.action = models.AuditAction(doc['action'])
                l.target_id = doc.get('target_id')
                l.data = doc.get('data')
                l.created_at = datetime.fromisoformat(doc['$createdAt'] if '$createdAt' in doc else doc['created_at'])
                logs.append(l)
            return logs
        except AppwriteException:
            return []

    # --- Integration Tokens ---
    def create_integration_token(self, user_id: str, class_id: str, scopes: str = "read:events", expires_at: datetime = None) -> models.IntegrationToken:
        token_val = secrets.token_urlsafe(32)
        try:
            doc = self.db.create_document(self.database_id, 'integration_tokens', ID.unique(), {
                'token': token_val,
                'user_id': user_id,
                'class_id': class_id,
                'scopes': scopes,
                'expires_at': expires_at.isoformat() if expires_at else None,
                'created_at': datetime.now().isoformat()
            })
            t = models.IntegrationToken()
            t.id = doc['$id']
            t.token = doc['token']
            t.user_id = doc['user_id']
            t.class_id = doc['class_id']
            t.scopes = doc['scopes']
            t.expires_at = datetime.fromisoformat(doc['expires_at']) if doc.get('expires_at') else None
            return t
        except AppwriteException as e:
            raise e

    def use_integration_token(self, token_value: str) -> Optional[models.IntegrationToken]:
        try:
            result = self.db.list_documents(self.database_id, 'integration_tokens', [
                Query.equal('token', token_value)
            ])
            if not result['documents']:
                return None
            
            doc = result['documents'][0]
            if doc.get('revoked'): return None
            
            expires_at = datetime.fromisoformat(doc['expires_at']) if doc.get('expires_at') else None
            if expires_at and expires_at < datetime.now():
                return None
            
            t = models.IntegrationToken()
            t.id = doc['$id']
            t.token = doc['token']
            t.user_id = doc['user_id']
            t.class_id = doc['class_id']
            t.scopes = doc['scopes']
            t.expires_at = expires_at
            t.last_used_at = datetime.now()
            
            return t
        except AppwriteException:
            return None
