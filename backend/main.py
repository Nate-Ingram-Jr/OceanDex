from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="OceanDex API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/creatures", response_model=List[schemas.SeaCreatureSummary])
def list_creatures(
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(models.SeaCreature)
    if q:
        query = query.filter(
            models.SeaCreature.common_name.ilike(f"%{q}%")
            | models.SeaCreature.scientific_name.ilike(f"%{q}%")
        )
    if category:
        query = query.filter(models.SeaCreature.category == category)
    return query.order_by(models.SeaCreature.common_name).all()


@app.get("/creatures/{creature_id}", response_model=schemas.SeaCreatureDetail)
def get_creature(creature_id: int, db: Session = Depends(get_db)):
    creature = db.query(models.SeaCreature).filter(models.SeaCreature.id == creature_id).first()
    if not creature:
        raise HTTPException(status_code=404, detail="Species not found")
    return creature

@app.post("/creatures", response_model=schemas.SeaCreatureDetail, status_code=201)
def create_creature(body: schemas.SeaCreatureCreate, db: Session = Depends(get_db)):
        creature = models.SeaCreature(**body.model_dump())
        db.add(creature)
        db.commit()
        db.refresh(creature)
        return creature

@app.patch("/creatures/{creature_id}", response_model=schemas.SeaCreatureDetail)
def update_creature(creature_id: int, body: schemas.SeaCreatureUpdate, db: Session = Depends(get_db)):
    creature = db.query(models.SeaCreature).filter(models.SeaCreature.id == creature_id).first()
    if not creature:
        raise HTTPException(status_code=404, detail="Species not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(creature, field, value)
    db.commit()
    db.refresh(creature)
    return creature

@app.get("/creatures/{creature_id}/related", response_model=List[schemas.SeaCreatureSummary])
def related_creatures(creature_id: int, db: Session = Depends(get_db)):
    creature = db.query(models.SeaCreature).filter(models.SeaCreature.id == creature_id).first()
    if not creature:
        raise HTTPException(status_code=404, detail="Species not found")
    return (
        db.query(models.SeaCreature)
        .filter(
            models.SeaCreature.category == creature.category,
            models.SeaCreature.id != creature_id,
        )
        .limit(3)
        .all()
    )

@app.get("/creatures/{creature_id}/habitat", response_model=schemas.HabitatRangeOut)
def get_habitat(creature_id: int, db: Session = Depends(get_db)):
    creature = (
        db.query(models.SeaCreature)
        .options(
            joinedload(models.SeaCreature.region_associations)
            .joinedload(models.RegionCreature.region)
            .joinedload(models.Region.state)
        )
        .filter(models.SeaCreature.id == creature_id)
        .first()
    )
    if not creature:
        raise HTTPException(status_code=404, detail="Species not found")
    return creature


@app.get("/map-data", response_model=List[schemas.MapCreatureOut])
def get_map_data(db: Session = Depends(get_db)):
    return (
        db.query(models.SeaCreature)
        .options(
            joinedload(models.SeaCreature.region_associations)
            .joinedload(models.RegionCreature.region)
            .joinedload(models.Region.state)
        )
        .order_by(models.SeaCreature.common_name)
        .all()
    )
_POSITIVE_KEYWORDS = {
    "recover", "recovered", "recovery", "successful", "success", "restored",
    "restoration", "resilient", "thriving", "model for", "record high",
    "measurable", "improved", "filling", "right call",
}
_NEGATIVE_KEYWORDS = {
    "decline", "declined", "declining", "collapse", "collapsed", "endangered",
    "critically", "threatened", "reduced", "catastrophic", "crisis", "near zero",
    "near-collapse", "wiped out", "drop", "dropped", "decrease", "lost",
    "devastating", "depleted", "disappear", "extinct",
}


def _classify(text: str) -> str:
    lower = text.lower()
    pos = any(k in lower for k in _POSITIVE_KEYWORDS)
    neg = any(k in lower for k in _NEGATIVE_KEYWORDS)
    if pos and not neg:
        return "positive"
    if neg and not pos:
        return "negative"
    return "neutral"


def _first_sentence(text: str) -> str:
    for sep in (". ", "— ", " — "):
        idx = text.find(sep)
        if idx != -1 and idx > 20:
            return text[: idx + 1].strip()
    return text[:120].rstrip() + ("…" if len(text) > 120 else "")


@app.get("/conservation-facts", response_model=List[schemas.ConservationFactOut])
def conservation_facts(db: Session = Depends(get_db)):
    rows = (
        db.query(models.ConservationStatus.aware_fact)
        .filter(models.ConservationStatus.aware_fact.isnot(None))
        .all()
    )
    return [
        {"text": _first_sentence(r.aware_fact), "sentiment": _classify(r.aware_fact)}
        for r in rows
    ]


@app.get("/protected-stats", response_model=schemas.ProtectedStatsOut)
def protected_stats(db: Session = Depends(get_db)):
    THREATENED = ["Vulnerable", "Endangered", "Critically Endangered"]

    # All threatened creatures with their conservation + category info
    threatened = (
        db.query(models.SeaCreature)
        .join(models.ConservationStatus)
        .filter(models.ConservationStatus.iucn_level.in_(THREATENED))
        .options(joinedload(models.SeaCreature.conservation),
                 joinedload(models.SeaCreature.regulations))
        .all()
    )

    total = len(threatened)
    critically_endangered = sum(
        1 for c in threatened if c.conservation.iucn_level == "Critically Endangered"
    )
    declining = sum(
        1 for c in threatened
        if c.conservation.population_trend and "decreas" in c.conservation.population_trend.lower()
    )
    pct_declining = round(declining * 100 / total) if total else 0

    # % of sharks that are threatened
    all_sharks = db.query(models.SeaCreature).filter(models.SeaCreature.category == "shark").count()
    threatened_sharks = sum(1 for c in threatened if str(c.category) == "shark")
    pct_sharks = round(threatened_sharks * 100 / all_sharks) if all_sharks else 0

    # % of rays that are threatened
    all_rays = db.query(models.SeaCreature).filter(models.SeaCreature.category == "ray").count()
    threatened_rays = sum(1 for c in threatened if str(c.category) == "ray")
    pct_rays = round(threatened_rays * 100 / all_rays) if all_rays else 0

    # count threatened species with at least one regulation where harvest is banned
    harvest_banned = sum(
        1 for c in threatened
        if any(not r.harvest_legal for r in c.regulations)
    )

    return {
        "total_threatened": total,
        "critically_endangered": critically_endangered,
        "pct_declining": pct_declining,
        "pct_sharks_threatened": pct_sharks,
        "pct_rays_threatened": pct_rays,
        "harvest_banned": harvest_banned,
    }


@app.get("/protected", response_model=List[schemas.SeaCreatureSummary])
def protected_list(
    iucn: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = (
        db.query(models.SeaCreature)
        .join(models.ConservationStatus)
        .options(
            joinedload(models.SeaCreature.regulations).joinedload(models.LegalRegulation.state)
        )
        .filter(
            models.ConservationStatus.iucn_level.in_(
                ["Vulnerable", "Endangered", "Critically Endangered"]
            )
        )
    )
    if iucn:
        query = query.filter(models.ConservationStatus.iucn_level == iucn)
    if category:
        query = query.filter(models.SeaCreature.category == category)
    return query.order_by(models.SeaCreature.common_name).all()

    # --- iNaturalist implementation (requires account 2+ months old with 10+ IDs) ---
    # @app.post("/scan", response_model=schemas.ScanResult)
    # async def scan_creature(image: UploadFile = File(...), db: Session = Depends(get_db)):
    #     image_bytes = await image.read()
    #     async with httpx.AsyncClient() as client:
    #         response = await client.post(
    #             "https://api.inaturalist.org/v1/computervision/score_image",
    #             files={"image": (image.filename, image_bytes, image.content_type)},
    #             headers={"Authorization": f"Bearer {os.getenv('INAT_TOKEN')}"},
    #             timeout=15.0,
    #         )
    #     if response.status_code != 200:
    #         raise HTTPException(status_code=502, detail=f"iNaturalist error {response.status_code}: {response.text}")
    #     results = response.json().get("results", [])
    #     if not results:
    #         return {"matched": False}
    #     top = results[0]
    #     scientific_name = top.get("taxon", {}).get("name")
    #     confidence = round(top.get("combined_score", 0) * 100)
    #     creature = (
    #         db.query(models.SeaCreature)
    #         .filter(models.SeaCreature.scientific_name.ilike(scientific_name))
    #         .first()
    #     )
    #     if creature:
    #         return {"matched": True, "creature": creature, "confidence": confidence}
    #     return {"matched": False, "inat_name": scientific_name, "confidence": confidence}
    # --- end iNaturalist ---
