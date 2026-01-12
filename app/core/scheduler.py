import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, crud
from app.core.email import email_service
from app.core.config import settings

scheduler = AsyncIOScheduler()

async def check_event_reminders():
    """Checks for events starting tomorrow and sends reminders"""
    if not settings.EMAIL_NOTIFICATIONS_ENABLED:
        return

    db = SessionLocal()
    try:
        # Get events for tomorrow (simplified logic)
        # Real logic would be more precise with timezones
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        start_of_day = datetime.datetime.combine(tomorrow, datetime.time.min)
        end_of_day = datetime.datetime.combine(tomorrow, datetime.time.max)

        events = db.query(models.Event).filter(
            models.Event.date >= start_of_day,
            models.Event.date <= end_of_day
        ).all()

        for event in events:
            # Find users in the class who enabled notifications
            # This is tricky because we need to query users of the class
            # and their preferences.

            # 1. Get all users in the class
            users = db.query(models.User).filter(
                models.User.class_id == event.class_id,
                models.User.email.isnot(None) # Only users with email
            ).all()

            for user in users:
                # Check preferences
                prefs = db.query(models.UserPreferences).filter(
                    models.UserPreferences.user_id == user.id
                ).first()

                if not prefs or prefs.email_notifications_enabled:
                    # Send email
                    event_link = f"{settings.BASE_URL}/?event={event.id}"
                    await email_service.send_event_reminder(
                        user.email,
                        event.title or event.type,
                        event.date.strftime("%d.%m.%Y"),
                        event.date.strftime("%H:%M") if event.date else None,
                        event_link
                    )

    finally:
        db.close()

async def send_weekly_digests():
    """Sends weekly digests to subscribed users"""
    if not settings.EMAIL_DIGEST_ENABLED:
        # Global switch, but also per user
        # If globally disabled, no one gets it?
        # The prompt implies ENV variable control, so yes.
        return

    db = SessionLocal()
    try:
        # Get all users with email and digest enabled
        users = db.query(models.User).join(models.UserPreferences).filter(
            models.User.email.isnot(None),
            models.UserPreferences.email_digest_enabled == True,
            models.UserPreferences.email_digest_schedule == "weekly"
        ).all()

        # Determine period (next 7 days)
        today = datetime.date.today()
        next_week = today + datetime.timedelta(days=7)

        for user in users:
            # Get events for this user's class for next 7 days
            events = db.query(models.Event).filter(
                models.Event.class_id == user.class_id,
                models.Event.date >= today,
                models.Event.date <= next_week
            ).order_by(models.Event.date).all()

            if events:
                event_list = []
                for e in events:
                    event_list.append({
                        "title": e.title or e.type,
                        "date": e.date.strftime("%d.%m.%Y %H:%M"),
                        "type": e.type,
                        "subject": e.subject_name
                    })

                await email_service.send_digest(user.email, event_list, "Wöchentlicher")

    finally:
        db.close()

def start_scheduler():
    # Add jobs
    # Reminders check every hour (to be safe, but logic sends for "tomorrow")
    # To avoid duplicate emails, we should mark them as sent or just run once a day.
    # For simplicity here: Run once a day at 18:00
    scheduler.add_job(check_event_reminders, 'cron', hour=18, minute=0)

    # Digest: Every Sunday at 19:00
    scheduler.add_job(send_weekly_digests, 'cron', day_of_week='sun', hour=19, minute=0)

    scheduler.start()
