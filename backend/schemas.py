from pydantic import BaseModel
from typing import Optional, List, Any


class ProtectedStatsOut(BaseModel):
    total_threatened: int
    critically_endangered: int
    pct_declining: int          # % of threatened species with declining population
    pct_sharks_threatened: int  # % of all sharks that are threatened
    pct_rays_threatened: int    # % of all rays that are threatened
    harvest_banned: int         # count of threatened species where harvest is illegal


class ConservationFactOut(BaseModel):
    text: str
    sentiment: str  # "positive" | "negative" | "neutral"


class StateOut(BaseModel):
    id: int
    code: str
    name: str

    class Config:
        from_attributes = True


class RegionOut(BaseModel):
    id: int
    name: str
    water_type: str
    avg_depth_m: Optional[float]
    state: StateOut

    class Config:
        from_attributes = True


class ConservationStatusOut(BaseModel):
    iucn_level: str
    population_trend: str
    threat_score: Optional[int]
    aware_fact: str
    last_assessed: Optional[str]
    main_threats: Optional[List[Any]]
    conservation_actions: Optional[List[Any]]

    class Config:
        from_attributes = True


class RegionCreatureOut(BaseModel):
    abundance: Optional[str]
    best_season: Optional[str]
    depth_notes: Optional[str]
    region: RegionOut

    class Config:
        from_attributes = True


class LegalRegulationOut(BaseModel):
    id: int
    harvest_legal: bool
    min_size_cm: Optional[float]
    bag_limit: Optional[int]
    season: Optional[str]
    permit_required: Optional[str]
    authority: str
    state: StateOut

    class Config:
        from_attributes = True


class SeaCreatureSummary(BaseModel):
    id: int
    common_name: str
    scientific_name: str
    category: str
    max_length_cm: Optional[float]
    image_url: Optional[str]
    conservation: Optional[ConservationStatusOut]
    regulations: List[LegalRegulationOut] = []

    class Config:
        from_attributes = True


class SeaCreatureDetail(BaseModel):
    id: int
    common_name: str
    scientific_name: str
    category: str
    max_length_cm: Optional[float]
    depth_min_m: Optional[float]
    depth_max_m: Optional[float]
    weight: Optional[str]
    diet: str
    lifespan: Optional[str]
    habitat: Optional[str]
    migratory: bool
    image_url: Optional[str]
    about: Optional[str]
    legal_notice: Optional[str]
    encounter_tip: Optional[str]
    conservation: Optional[ConservationStatusOut]
    region_associations: List[RegionCreatureOut] = []
    regulations: List[LegalRegulationOut] = []

    class Config:
        from_attributes = True

class HabitatRangeOut(BaseModel):
    creature_id: int
    common_name: str
    depth_min_m: Optional[float]
    depth_max_m: Optional[float]
    migratory: bool
    habitat: Optional[str]
    regions: List[RegionCreatureOut] = []

    class Config:
        from_attributes = True

class MapCreatureOut(BaseModel):
    id: int
    common_name: str
    scientific_name: str
    category: str
    image_url: Optional[str]
    region_associations: List[RegionCreatureOut] = []

    class Config:
        from_attributes = True

class ScanResult(BaseModel):
    matched: bool
    creature: Optional[SeaCreatureSummary] = None
    inat_name: Optional[str] = None # what iNaturalist identified
    confidence: Optional[int] = None # percentage

class SeaCreatureCreate(BaseModel):
    common_name: str
    scientific_name: str
    category: str
    max_length_cm: Optional[float]
    depth_min_m: Optional[float]
    depth_max_m: Optional[float]
    weight: Optional[str]
    diet: str
    lifespan: Optional[str]
    habitat: Optional[str]
    migratory: bool
    image_url: Optional[str]
    about: Optional[str]
    legal_notice: Optional[str]
    encounter_tip: Optional[str]

class SeaCreatureUpdate(BaseModel):
    common_name: Optional[str]
    scientific_name: Optional[str]
    category: Optional[str]
    max_length_cm: Optional[float]
    depth_min_m: Optional[float]
    depth_max_m: Optional[float]
    weight: Optional[str]
    diet: Optional[str]
    lifespan: Optional[str]
    habitat: Optional[str]
    migratory: Optional[bool]
    image_url: Optional[str]
    about: Optional[str]
    legal_notice: Optional[str]
    encounter_tip: Optional[str]