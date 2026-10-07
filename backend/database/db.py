"""
Database session management and persistence utilities.
"""

import os
from pathlib import Path
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

from backend.database.models import Base, Farmer, DiseaseScan, SoilRecord
from backend.utils.constants import BASE_DIR
from backend.utils.helpers import get_logger

load_dotenv()
logger = get_logger("Database")

DB_PATH = BASE_DIR / "smart_agri_partner.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initializes SQLite database and tables if they do not exist."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schemas verified/created successfully.")
        
        # Seed default farmer if none exists
        with get_db() as db:
            existing = db.query(Farmer).first()
            if not existing:
                default_farmer = Farmer(
                    name="Shri Basavaraj Gowda",
                    phone="9845012345",
                    state="Karnataka",
                    district="Kolar",
                    village="Vokkaleri",
                    land_area=3.5,
                    primary_crop="Tomato",
                    soil_type="Red Loam",
                    language="kn"
                )
                db.add(default_farmer)
                db.commit()
                logger.info("Seeded initial demo farmer profile.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")


@contextmanager
def get_db():
    """Provide a transactional scope around a series of operations."""
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_current_farmer() -> Farmer:
    """Retrieves current or default active farmer profile."""
    with get_db() as db:
        farmer = db.query(Farmer).order_by(Farmer.id.desc()).first()
        if not farmer:
            init_db()
            farmer = db.query(Farmer).first()
        # Return detached clone for session safety
        return {
            "id": farmer.id,
            "name": farmer.name,
            "phone": farmer.phone,
            "state": farmer.state,
            "district": farmer.district,
            "village": farmer.village,
            "land_area": farmer.land_area,
            "primary_crop": farmer.primary_crop,
            "soil_type": farmer.soil_type,
            "language": farmer.language
        }


def save_farmer_profile(profile_data: dict) -> bool:
    """Updates or creates the active farmer profile."""
    try:
        with get_db() as db:
            farmer = db.query(Farmer).first()
            if not farmer:
                farmer = Farmer()
                db.add(farmer)
            
            farmer.name = profile_data.get("name", farmer.name)
            farmer.phone = profile_data.get("phone", farmer.phone)
            farmer.state = profile_data.get("state", farmer.state)
            farmer.district = profile_data.get("district", farmer.district)
            farmer.village = profile_data.get("village", farmer.village)
            farmer.land_area = float(profile_data.get("land_area", farmer.land_area))
            farmer.primary_crop = profile_data.get("primary_crop", farmer.primary_crop)
            farmer.soil_type = profile_data.get("soil_type", farmer.soil_type)
            farmer.language = profile_data.get("language", farmer.language)
            db.commit()
            return True
    except Exception as e:
        logger.error(f"Failed to save profile: {e}")
        return False


def log_disease_scan(scan_dict: dict, farmer_id: int = 1) -> bool:
    """Persists a new leaf disease diagnosis scan record."""
    try:
        with get_db() as db:
            scan = DiseaseScan(
                farmer_id=farmer_id,
                image_path=scan_dict.get("image_path", ""),
                crop=scan_dict.get("crop", "Unknown"),
                disease=scan_dict.get("disease", "Unknown"),
                confidence=float(scan_dict.get("confidence", 0.0)),
                confidence_level=scan_dict.get("confidence_level", "Moderate"),
                status=scan_dict.get("status", "diseased")
            )
            db.add(scan)
            db.commit()
            return True
    except Exception as e:
        logger.error(f"Failed to log disease scan: {e}")
        return False


def get_recent_scans(limit: int = 5, farmer_id: int = None) -> list:
    """Fetches recent scan records."""
    try:
        with get_db() as db:
            query = db.query(DiseaseScan)
            if farmer_id:
                query = query.filter(DiseaseScan.farmer_id == farmer_id)
            scans = query.order_by(DiseaseScan.id.desc()).limit(limit).all()
            return [{
                "id": s.id,
                "crop": s.crop,
                "disease": s.disease,
                "confidence": s.confidence,
                "confidence_level": s.confidence_level or "High",
                "status": s.status,
                "created_at": s.created_at.strftime("%d %b %Y, %I:%M %p") if s.created_at else ""
            } for s in scans]
    except Exception as e:
        logger.error(f"Error fetching scans: {e}")
        return []


def get_all_test_reports(farmer_id: int = None) -> list:
    """Fetches all disease diagnosis test records for reports viewing."""
    try:
        with get_db() as db:
            query = db.query(DiseaseScan)
            if farmer_id:
                query = query.filter(DiseaseScan.farmer_id == farmer_id)
            scans = query.order_by(DiseaseScan.id.desc()).all()
            return [{
                "id": s.id,
                "crop": s.crop,
                "disease": s.disease,
                "confidence": s.confidence,
                "confidence_level": s.confidence_level or "High",
                "status": s.status,
                "image_path": s.image_path,
                "created_at": s.created_at.strftime("%d %b %Y, %I:%M %p") if s.created_at else "Recent"
            } for s in scans]
    except Exception as e:
        logger.error(f"Error fetching test reports: {e}")
        return []


