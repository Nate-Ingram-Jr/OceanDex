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
