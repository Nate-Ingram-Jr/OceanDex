from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
import models
import schemas
import auth
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
    state_id: Optional[int] = Query(None),
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
    if state_id:
        query = (
            query
            .join(models.SeaCreature.region_associations)
            .join(models.RegionCreature.region)
            .filter(models.Region.state_id == state_id)
            .distinct()
        )
    return query.order_by(models.SeaCreature.common_name).all()

@app.get("/states", response_model=List[schemas.StateOut])
def list_states(db: Session = Depends(get_db)):
    return db.query(models.State).order_by(models.State.name).all()

@app.get("/creatures/{creature_id}", response_model=schemas.SeaCreatureDetail)
def get_creature(creature_id: int, db: Session = Depends(get_db)):
    creature = db.query(models.SeaCreature).filter(models.SeaCreature.id == creature_id).first()
    if not creature:
        raise HTTPException(status_code=404, detail="Species not found")
    return creature

@app.post("/creatures", response_model=schemas.SeaCreatureDetail, status_code=201)
def create_creature(body: schemas.SeaCreatureCreate, db: Session = Depends(get_db)):
    conservation_data = body.conservation
    creature = models.SeaCreature(**body.model_dump(exclude={"conservation"}))
    db.add(creature)
    db.flush()
    if conservation_data:
        db.add(models.ConservationStatus(
            creature_id=creature.id,
            **conservation_data.model_dump(),
        ))
    db.commit()
    db.refresh(creature)
    return creature


@app.patch("/creatures/{creature_id}", response_model=schemas.SeaCreatureDetail)
def update_creature(creature_id: int, body: schemas.SeaCreatureUpdate, db: Session = Depends(get_db)):
    creature = db.query(models.SeaCreature).filter(models.SeaCreature.id == creature_id).first()
    if not creature:
        raise HTTPException(status_code=404, detail="Species not found")
    for field, value in body.model_dump(exclude_unset=True, exclude={"conservation"}).items():
        setattr(creature, field, value)
    if body.conservation is not None:
        if creature.conservation:
            for field, value in body.conservation.model_dump(exclude_unset=True).items():
                setattr(creature.conservation, field, value)
        else:
            db.add(models.ConservationStatus(
                creature_id=creature.id,
                **body.conservation.model_dump(exclude_unset=True),
            ))
    db.commit()
    db.refresh(creature)
    return creature


@app.post("/creatures/{creature_id}/conservation", response_model=schemas.ConservationStatusOut, status_code=201)
def create_conservation(creature_id: int, body: schemas.ConservationStatusCreate, db: Session = Depends(get_db)):
    creature = db.query(models.SeaCreature).filter(models.SeaCreature.id == creature_id).first()
    if not creature:
        raise HTTPException(status_code=404, detail="Species not found")
    if creature.conservation:
        raise HTTPException(status_code=409, detail="Conservation record already exists — use PATCH to update")
    conservation = models.ConservationStatus(creature_id=creature_id, **body.model_dump())
    db.add(conservation)
    db.commit()
    db.refresh(conservation)
    return conservation


@app.patch("/creatures/{creature_id}/conservation", response_model=schemas.ConservationStatusOut)
def update_conservation(creature_id: int, body: schemas.ConservationStatusUpdate, db: Session = Depends(get_db)):
    creature = db.query(models.SeaCreature).filter(models.SeaCreature.id == creature_id).first()
    if not creature:
        raise HTTPException(status_code=404, detail="Species not found")
    if not creature.conservation:
        raise HTTPException(status_code=404, detail="No conservation record — use POST to create one")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(creature.conservation, field, value)
    db.commit()
    db.refresh(creature.conservation)
    return creature.conservation

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

# ── Auth ─────────────────────────────────────────────────────────────────────

@app.post("/auth/register", response_model=schemas.TokenOut, status_code=201)
def register(body: schemas.UserRegister, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == body.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    if db.query(models.User).filter(models.User.username == body.username).first():
        raise HTTPException(status_code=409, detail="Username already taken")
    if body.user_type == "marine_biologist" and not (body.mb_credential or "").strip():
        raise HTTPException(status_code=422, detail="Credentials are required for Marine Biologist verification")
    user = models.User(
        email=body.email,
        username=body.username,
        password_hash=auth.hash_password(body.password),
        user_type=body.user_type,
        mb_credential=body.mb_credential.strip() if body.mb_credential else None,
        mb_status="pending" if body.user_type == "marine_biologist" else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"access_token": auth.create_token(user.id), "user": user}


@app.post("/auth/login", response_model=schemas.TokenOut)
def login(body: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == body.email).first()
    if not user or not auth.verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": auth.create_token(user.id), "user": user}


@app.get("/auth/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


@app.patch("/auth/me", response_model=schemas.UserOut)
def update_settings(
    body: schemas.UserSettingsUpdate,
    user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    if body.new_password:
        if not body.current_password or not auth.verify_password(body.current_password, user.password_hash):
            raise HTTPException(status_code=401, detail="Current password is incorrect")
        user.password_hash = auth.hash_password(body.new_password)

    if body.user_type is not None:
        if body.user_type == "marine_biologist":
            if not (body.mb_credential or "").strip():
                raise HTTPException(status_code=422, detail="Credentials are required for Marine Biologist verification")
            user.user_type = "marine_biologist"
            user.mb_credential = body.mb_credential.strip()
            user.mb_status = "pending"
        else:
            user.user_type = body.user_type
            user.mb_status = None
            user.mb_credential = None

    db.commit()
    db.refresh(user)
    return user


@app.get("/admin/mb-requests", response_model=List[schemas.UserOut])
def list_mb_requests(
    admin: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db),
):
    return db.query(models.User).filter(models.User.mb_status == "pending").all()


@app.post("/admin/mb-requests/{user_id}/approve")
def approve_mb(
    user_id: int,
    admin: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db),
):
    target = db.query(models.User).filter(models.User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.mb_status != "pending":
        raise HTTPException(status_code=409, detail="No pending verification for this user")
    target.mb_status = "approved"
    db.commit()
    return {"detail": "Approved"}


@app.post("/admin/mb-requests/{user_id}/reject")
def reject_mb(
    user_id: int,
    admin: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db),
):
    target = db.query(models.User).filter(models.User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.mb_status != "pending":
        raise HTTPException(status_code=409, detail="No pending verification for this user")
    target.mb_status = "rejected"
    target.user_type = "enthusiast"
    db.commit()
    return {"detail": "Rejected"}


# ── Admin Applications ────────────────────────────────────────────────────────

@app.post("/admin-applications", response_model=schemas.AdminApplicationOut, status_code=201)
def submit_admin_application(
    body: schemas.AdminApplicationCreate,
    user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    if user.role == "admin":
        raise HTTPException(status_code=409, detail="You are already an admin")
    existing = (
        db.query(models.AdminApplication)
        .filter(models.AdminApplication.user_id == user.id, models.AdminApplication.status == "pending")
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="You already have a pending application")
    if not body.motivation.strip():
        raise HTTPException(status_code=422, detail="Motivation is required")
    app_obj = models.AdminApplication(
        user_id=user.id,
        motivation=body.motivation.strip(),
        experience=body.experience.strip() if body.experience else None,
    )
    db.add(app_obj)
    db.commit()
    db.refresh(app_obj)
    return app_obj


@app.get("/admin-applications/my", response_model=Optional[schemas.AdminApplicationOut])
def my_admin_application(
    user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.AdminApplication)
        .filter(models.AdminApplication.user_id == user.id)
        .order_by(models.AdminApplication.created_at.desc())
        .first()
    )


@app.get("/admin-applications", response_model=List[schemas.AdminApplicationOut])
def list_admin_applications(
    status: Optional[str] = Query(None),
    admin: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(models.AdminApplication)
    if status:
        query = query.filter(models.AdminApplication.status == status)
    return query.order_by(models.AdminApplication.created_at.desc()).all()


@app.post("/admin-applications/{app_id}/approve", response_model=schemas.AdminApplicationOut)
def approve_admin_application(
    app_id: int,
    admin: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db),
):
    app_obj = db.query(models.AdminApplication).filter(models.AdminApplication.id == app_id).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    if app_obj.status != "pending":
        raise HTTPException(status_code=409, detail=f"Application is already {app_obj.status}")
    app_obj.status = "approved"
    app_obj.reviewed_by = admin.id
    app_obj.reviewed_at = datetime.utcnow()
    applicant = db.query(models.User).filter(models.User.id == app_obj.user_id).first()
    if applicant:
        applicant.role = "admin"
    db.commit()
    db.refresh(app_obj)
    return app_obj


@app.post("/admin-applications/{app_id}/reject", response_model=schemas.AdminApplicationOut)
def reject_admin_application(
    app_id: int,
    note: Optional[str] = Query(None),
    admin: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db),
):
    app_obj = db.query(models.AdminApplication).filter(models.AdminApplication.id == app_id).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    if app_obj.status != "pending":
        raise HTTPException(status_code=409, detail=f"Application is already {app_obj.status}")
    app_obj.status = "rejected"
    app_obj.review_note = note
    app_obj.reviewed_by = admin.id
    app_obj.reviewed_at = datetime.utcnow()
    db.commit()
    db.refresh(app_obj)
    return app_obj


# ── Submissions ───────────────────────────────────────────────────────────────

@app.post("/submissions", response_model=schemas.SubmissionOut, status_code=201)
def create_submission(
    body: schemas.SeaCreatureCreate,
    user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    submission = models.CreatureSubmission(
        submitted_by=user.id,
        creature_data=body.model_dump(),
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


@app.get("/submissions", response_model=List[schemas.SubmissionOut])
def list_submissions(
    status: Optional[str] = Query(None),
    user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(models.CreatureSubmission)
    if user.role != "admin":
        query = query.filter(models.CreatureSubmission.submitted_by == user.id)
    if status:
        query = query.filter(models.CreatureSubmission.status == status)
    return query.order_by(models.CreatureSubmission.created_at.desc()).all()


@app.get("/submissions/{sub_id}", response_model=schemas.SubmissionOut)
def get_submission(
    sub_id: int,
    user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    sub = db.query(models.CreatureSubmission).filter(models.CreatureSubmission.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    if user.role != "admin" and sub.submitted_by != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return sub


@app.post("/submissions/{sub_id}/approve", response_model=schemas.SeaCreatureDetail)
def approve_submission(
    sub_id: int,
    admin: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db),
):
    sub = db.query(models.CreatureSubmission).filter(models.CreatureSubmission.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    if sub.status != "pending":
        raise HTTPException(status_code=409, detail=f"Submission is already {sub.status}")

    creature_data = schemas.SeaCreatureCreate(**sub.creature_data)
    conservation_data = creature_data.conservation
    creature = models.SeaCreature(**creature_data.model_dump(exclude={"conservation"}))
    db.add(creature)
    db.flush()
    if conservation_data:
        db.add(models.ConservationStatus(
            creature_id=creature.id,
            **conservation_data.model_dump(),
        ))

    sub.status = "approved"
    sub.reviewed_by = admin.id
    sub.reviewed_at = datetime.utcnow()
    db.commit()
    db.refresh(creature)
    return creature


@app.post("/submissions/{sub_id}/reject", status_code=200)
def reject_submission(
    sub_id: int,
    note: Optional[str] = Query(None),
    admin: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db),
):
    sub = db.query(models.CreatureSubmission).filter(models.CreatureSubmission.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    if sub.status != "pending":
        raise HTTPException(status_code=409, detail=f"Submission is already {sub.status}")
    sub.status = "rejected"
    sub.review_note = note
    sub.reviewed_by = admin.id
    sub.reviewed_at = datetime.utcnow()
    db.commit()
    return {"detail": "Submission rejected"}


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
