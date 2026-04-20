from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
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
