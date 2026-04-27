from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class State(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True)
    name = Column(String)
    coastline = Column(String)
    primary_body = Column(String, nullable=True)

    regions = relationship("Region", back_populates="state")
    regulations = relationship("LegalRegulation", back_populates="state")


class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    state_id = Column(Integer, ForeignKey("states.id"))
    name = Column(String)
    water_type = Column(String)
    avg_depth_m = Column(Float, nullable=True)
    notes = Column(String, nullable=True)

    state = relationship("State", back_populates="regions")
    creature_associations = relationship("RegionCreature", back_populates="region")


class SeaCreature(Base):
    __tablename__ = "sea_creatures"

    id = Column(Integer, primary_key=True, index=True)
    common_name = Column(String, index=True)
    scientific_name = Column(String)
    category = Column(String)  # fish, shark, shellfish, ray, other
    max_length_cm = Column(Float, nullable=True)
    depth_min_m = Column(Float, nullable=True)
    depth_max_m = Column(Float, nullable=True)
    weight = Column(String, nullable=True)
    diet = Column(String)
    lifespan = Column(String, nullable=True)
    habitat = Column(String, nullable=True)
    migratory = Column(Boolean, default=False)
    image_url = Column(String, nullable=True)
    about = Column(Text, nullable=True)
    legal_notice = Column(Text, nullable=True)
    encounter_tip = Column(Text, nullable=True)

    conservation = relationship("ConservationStatus", back_populates="creature", uselist=False)
    region_associations = relationship("RegionCreature", back_populates="creature")
    regulations = relationship("LegalRegulation", back_populates="creature")


class ConservationStatus(Base):
    __tablename__ = "conservation_status"

    id = Column(Integer, primary_key=True, index=True)
    creature_id = Column(Integer, ForeignKey("sea_creatures.id"), unique=True)
    iucn_level = Column(String)
    population_trend = Column(String)
    threat_score = Column(Integer, nullable=True)
    aware_fact = Column(Text)
    last_assessed = Column(String, nullable=True)
    main_threats = Column(JSON, nullable=True)
    conservation_actions = Column(JSON, nullable=True)

    creature = relationship("SeaCreature", back_populates="conservation")


class RegionCreature(Base):
    __tablename__ = "region_creatures"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"))
    creature_id = Column(Integer, ForeignKey("sea_creatures.id"))
    abundance = Column(String, nullable=True)
    best_season = Column(String, nullable=True)
    depth_notes = Column(String, nullable=True)

    region = relationship("Region", back_populates="creature_associations")
    creature = relationship("SeaCreature", back_populates="region_associations")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")  # "user" | "admin"
    user_type = Column(String, default="enthusiast")  # enthusiast | fisher | marine_biologist
    mb_status = Column(String, nullable=True)  # None | pending | approved | rejected
    mb_credential = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    submissions = relationship(
        "CreatureSubmission",
        foreign_keys="CreatureSubmission.submitted_by",
        back_populates="submitter",
    )


class CreatureSubmission(Base):
    __tablename__ = "creature_submissions"

    id = Column(Integer, primary_key=True, index=True)
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="pending")  # pending | approved | rejected
    review_note = Column(Text, nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    creature_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)

    submitter = relationship("User", foreign_keys=[submitted_by], back_populates="submissions")
    reviewer = relationship("User", foreign_keys=[reviewed_by])


class AdminApplication(Base):
    __tablename__ = "admin_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    motivation = Column(Text, nullable=False)
    experience = Column(Text, nullable=True)
    status = Column(String, default="pending")  # pending | approved | rejected
    review_note = Column(Text, nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)

    applicant = relationship("User", foreign_keys=[user_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])


class LegalRegulation(Base):
    __tablename__ = "legal_regulations"

    id = Column(Integer, primary_key=True, index=True)
    creature_id = Column(Integer, ForeignKey("sea_creatures.id"))
    state_id = Column(Integer, ForeignKey("states.id"))
    harvest_legal = Column(Boolean, default=True)
    min_size_cm = Column(Float, nullable=True)
    bag_limit = Column(Integer, nullable=True)
    season = Column(String, nullable=True)
    permit_required = Column(String, nullable=True)
    authority = Column(String)

    creature = relationship("SeaCreature", back_populates="regulations")
    state = relationship("State", back_populates="regulations")
