"""
SQLAlchemy ORM Data Models for Smart Agri-Partner.
Defines schemas for farmers, leaf disease scans, soil logs, and market benchmarks.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, default="Farmer")
    phone = Column(String(20), nullable=True)
    state = Column(String(50), nullable=False, default="Karnataka")
    district = Column(String(50), nullable=False, default="Bengaluru")
    village = Column(String(100), nullable=True)
    land_area = Column(Float, nullable=False, default=2.0)  # acres
    primary_crop = Column(String(50), nullable=True, default="Tomato")
    soil_type = Column(String(50), nullable=True, default="Red Loam")
    language = Column(String(10), nullable=False, default="en")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    disease_scans = relationship("DiseaseScan", back_populates="farmer", cascade="all, delete-orphan")
    soil_records = relationship("SoilRecord", back_populates="farmer", cascade="all, delete-orphan")


class DiseaseScan(Base):
    __tablename__ = "disease_scans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=True)
    image_path = Column(String(255), nullable=True)
    crop = Column(String(50), nullable=False)
    disease = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    confidence_level = Column(String(20), nullable=True)
    status = Column(String(20), nullable=False, default="diseased")
    created_at = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="disease_scans")


class SoilRecord(Base):
    __tablename__ = "soil_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=True)
    ph = Column(Float, nullable=False)
    nitrogen = Column(Float, nullable=False)
    phosphorus = Column(Float, nullable=False)
    potassium = Column(Float, nullable=False)
    organic_carbon = Column(Float, nullable=True, default=0.6)
    moisture = Column(Float, nullable=True, default=50.0)
    score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    farmer = relationship("Farmer", back_populates="soil_records")


class MarketPrice(Base):
    __tablename__ = "market_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    state = Column(String(50), nullable=False)
    district = Column(String(50), nullable=False)
    market = Column(String(100), nullable=False)
    commodity = Column(String(50), nullable=False)
    variety = Column(String(50), nullable=True)
    min_price = Column(Float, nullable=False)
    max_price = Column(Float, nullable=False)
    modal_price = Column(Float, nullable=False)
    arrival_date = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

