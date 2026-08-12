import logging
from contextlib import asynccontextmanager
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from campaign_ops_sentinel.config import settings
from campaign_ops_sentinel.database import Base, engine, get_db
from campaign_ops_sentinel.models import (
    ApprovalDecision,
    ApprovalReceipt,
    CampaignBrief,
    CampaignRecommendation,
)
from campaign_ops_sentinel.repository import (
    get_recommendation,
    list_audit_events,
    record_approval,
    save_recommendation,
)
from campaign_ops_sentinel.security import verify_api_key
from campaign_ops_sentinel.services.workflow import build_recommendation

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.app_env != "production":
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="CampaignOps Sentinel", version="0.2.0", lifespan=lifespan)


@app.middleware("http")
async def attach_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    response: Response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_complete path=%s status=%s request_id=%s",
        request.url.path,
        response.status_code,
        request_id,
    )
    return response


@app.get("/health", tags=["operations"])
def health() -> dict[str, str | bool]:
    return {"status": "ok", "shadow_mode": settings.shadow_mode}


@app.get("/ready", tags=["operations"])
def readiness(db: Session = Depends(get_db)) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ready"}


@app.post(
    "/v1/campaigns/recommendations",
    response_model=CampaignRecommendation,
    dependencies=[Depends(verify_api_key)],
)
def create_recommendation(
    brief: CampaignBrief, request: Request, db: Session = Depends(get_db)
) -> CampaignRecommendation:
    recommendation = build_recommendation(brief)
    return save_recommendation(db, recommendation, request.headers.get("X-Request-ID", "unknown"))


@app.get(
    "/v1/campaigns/recommendations/{recommendation_id}",
    response_model=CampaignRecommendation,
    dependencies=[Depends(verify_api_key)],
)
def read_recommendation(recommendation_id: UUID, db: Session = Depends(get_db)) -> CampaignRecommendation:
    recommendation = get_recommendation(db, recommendation_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return recommendation


@app.post(
    "/v1/campaigns/recommendations/{recommendation_id}/approval",
    response_model=ApprovalReceipt,
    dependencies=[Depends(verify_api_key)],
)
def approve_campaign(
    recommendation_id: UUID,
    decision: ApprovalDecision,
    request: Request,
    db: Session = Depends(get_db),
) -> ApprovalReceipt:
    if not record_approval(db, recommendation_id, decision, request.headers.get("X-Request-ID", "unknown")):
        raise HTTPException(status_code=404, detail="Recommendation not found")
    if not settings.shadow_mode:
        raise HTTPException(status_code=501, detail="Live campaign mutations are not implemented")
    return ApprovalReceipt(
        recommendation_id=recommendation_id,
        status="recorded_in_shadow_mode",
        decision=decision.decision,
        message="No external campaign action was taken.",
    )


@app.get(
    "/v1/campaigns/recommendations/{recommendation_id}/audit",
    dependencies=[Depends(verify_api_key)],
)
def get_audit_log(recommendation_id: UUID, db: Session = Depends(get_db)) -> list[dict]:
    if not get_recommendation(db, recommendation_id):
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return [
        {
            "event_type": event.event_type,
            "actor": event.actor,
            "request_id": event.request_id,
            "payload": event.payload,
            "created_at": event.created_at,
        }
        for event in list_audit_events(db, recommendation_id)
    ]
