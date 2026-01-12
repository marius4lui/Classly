import os
from typing import List, Dict, Any
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.core.config import settings

class EmailService:
    def __init__(self):
        self.config = ConnectionConfig(
            MAIL_USERNAME=settings.SMTP_USER,
            MAIL_PASSWORD=settings.SMTP_PASSWORD,
            MAIL_FROM=settings.SMTP_FROM,
            MAIL_PORT=settings.SMTP_PORT,
            MAIL_SERVER=settings.SMTP_HOST,
            MAIL_STARTTLS=not settings.SMTP_SECURE,
            MAIL_SSL_TLS=settings.SMTP_SECURE,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
            TEMPLATE_FOLDER=None  # We use Jinja2 manually
        )
        self.fastmail = FastMail(self.config)
        self.jinja_env = Environment(
            loader=FileSystemLoader("app/templates/email"),
            autoescape=select_autoescape(['html', 'xml'])
        )

    async def _send(self, to_email: str, subject: str, template_name: str, context: Dict[str, Any]):
        if not settings.SMTP_HOST:
            print("SMTP not configured. Skipping email.")
            return

        template = self.jinja_env.get_template(template_name)
        html_content = template.render(
            app_name=settings.APP_NAME,
            base_url=settings.BASE_URL,
            **context
        )

        message = MessageSchema(
            subject=subject,
            recipients=[to_email],
            body=html_content,
            subtype=MessageType.html
        )

        try:
            await self.fastmail.send_message(message)
            print(f"Email sent to {to_email}: {subject}")
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")

    async def send_magic_link(self, to_email: str, magic_link: str):
        await self._send(
            to_email,
            "Dein Login Link",
            "magic_link.html",
            {"magic_link": magic_link}
        )

    async def send_welcome_email(self, to_email: str, name: str):
        await self._send(
            to_email,
            "Willkommen bei Classly!",
            "welcome.html",
            {"name": name}
        )

    async def send_event_reminder(self, to_email: str, event_title: str, event_date: str, event_time: str, event_link: str):
         await self._send(
            to_email,
            f"Erinnerung: {event_title}",
            "event_reminder.html",
            {
                "event_title": event_title,
                "event_date": event_date,
                "event_time": event_time,
                "event_link": event_link
            }
        )

    async def send_digest(self, to_email: str, events: List[Dict[str, Any]], period: str):
        await self._send(
            to_email,
            f"Dein {period} Digest",
            "digest.html",
            {"events": events, "period": period}
        )

email_service = EmailService()
