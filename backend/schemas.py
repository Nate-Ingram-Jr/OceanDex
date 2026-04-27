from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


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

class ConservationStatusCreate(BaseModel):
    iucn_level: str
    population_trend: str
    threat_score: Optional[int] = None
    aware_fact: str
    last_assessed: Optional[str] = None
    main_threats: Optional[List[Any]] = None
    conservation_actions: Optional[List[Any]] = None


class ConservationStatusUpdate(BaseModel):
    iucn_level: Optional[str] = None
    population_trend: Optional[str] = None
    threat_score: Optional[int] = None
    aware_fact: Optional[str] = None
    last_assessed: Optional[str] = None
    main_threats: Optional[List[Any]] = None
    conservation_actions: Optional[List[Any]] = None


class SeaCreatureCreate(BaseModel):
    common_name: str
    scientific_name: str
    category: str
    max_length_cm: Optional[float] = None
    depth_min_m: Optional[float] = None
    depth_max_m: Optional[float] = None
    weight: Optional[str] = None
    diet: str
    lifespan: Optional[str] = None
    habitat: Optional[str] = None
    migratory: bool
    image_url: Optional[str] = None
    about: Optional[str] = None
    legal_notice: Optional[str] = None
    encounter_tip: Optional[str] = None
    conservation: Optional[ConservationStatusCreate] = None


class SeaCreatureUpdate(BaseModel):
    common_name: Optional[str] = None
    scientific_name: Optional[str] = None
    category: Optional[str] = None
    max_length_cm: Optional[float] = None
    depth_min_m: Optional[float] = None
    depth_max_m: Optional[float] = None
    weight: Optional[str] = None
    diet: Optional[str] = None
    lifespan: Optional[str] = None
    habitat: Optional[str] = None
    migratory: Optional[bool] = None
    image_url: Optional[str] = None
    about: Optional[str] = None
    legal_notice: Optional[str] = None
    encounter_tip: Optional[str] = None
    conservation: Optional[ConservationStatusUpdate] = None


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: str
    username: str
    password: str = Field(min_length=8, max_length=72)
    user_type: str = "enthusiast"
    mb_credential: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    role: str
    user_type: str
    mb_status: Optional[str]
    mb_credential: Optional[str]

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    user: UserOut


class UserSettingsUpdate(BaseModel):
    user_type: Optional[str] = None
    mb_credential: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = Field(None, min_length=8, max_length=72)


# ── Admin Applications ────────────────────────────────────────────────────────

class AdminApplicationCreate(BaseModel):
    motivation: str
    experience: Optional[str] = None


class AdminApplicationOut(BaseModel):
    id: int
    status: str
    review_note: Optional[str]
    motivation: str
    experience: Optional[str]
    created_at: datetime
    reviewed_at: Optional[datetime]
    applicant: UserOut

    class Config:
        from_attributes = True


# ── Submissions ───────────────────────────────────────────────────────────────

class SubmissionOut(BaseModel):
    id: int
    status: str
    review_note: Optional[str]
    creature_data: dict
    created_at: datetime
    reviewed_at: Optional[datetime]
    submitter: UserOut

    class Config:
        from_attributes = True