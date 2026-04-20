from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
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


@app.get("/protected", response_model=List[schemas.SeaCreatureSummary])
def protected_list(
    iucn: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = (
        db.query(models.SeaCreature)
        .join(models.ConservationStatus)
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
