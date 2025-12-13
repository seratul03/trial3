"""
APScheduler configuration for announcement scheduling
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def publish_announcement_job(db_session_factory, announcement_id: int):
    """Job to publish a scheduled announcement"""
    from app.models import Announcement
    
    db = db_session_factory()
    try:
        announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
        
        if announcement and not announcement.is_active:
            announcement.published_at = datetime.utcnow()
            announcement.is_active = True
            db.commit()
            logger.info(f"Published announcement {announcement_id}: {announcement.title}")
        
    except Exception as e:
        logger.error(f"Error publishing announcement {announcement_id}: {e}")
        db.rollback()
    finally:
        db.close()


def schedule_announcement(db: Session, announcement_id: int, scheduled_time: datetime):
    """Schedule an announcement for future publication"""
    from app.database import SessionLocal
    
    try:
        scheduler.add_job(
            publish_announcement_job,
            trigger=DateTrigger(run_date=scheduled_time),
            args=[SessionLocal, announcement_id],
            id=f"announcement_{announcement_id}",
            replace_existing=True
        )
        logger.info(f"Scheduled announcement {announcement_id} for {scheduled_time}")
    except Exception as e:
        logger.error(f"Error scheduling announcement {announcement_id}: {e}")


def start_scheduler():
    """Start the background scheduler"""
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started successfully")


def shutdown_scheduler():
    """Shutdown the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shut down")
