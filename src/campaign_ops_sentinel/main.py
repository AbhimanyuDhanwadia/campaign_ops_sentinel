from fastapi import FastAPI, HTTPException

from campaign_ops_sentinel.config import settings
from campaign_ops_sentinel.models import ApprovalDecision, CampaignBrief, CampaignRecommendation
from campaign_ops_sentinel.services.workflow import build_recommendation

app = FastAPI(title="CampaignOps Sentinel", version="0.1.0")
_recommendations: dict[str, CampaignRecommendation] = {}


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {"status": "ok", "shadow_mode": settings.shadow_mode}


@app.post("/v1/campaigns/recommendations", response_model=CampaignRecommendation)
def create_recommendation(brief: CampaignBrief) -> CampaignRecommendation:
    recommendation = build_recommendation(brief)
    _recommendations[brief.brand.lower()] = recommendation
    return recommendation


@app.post("/v1/campaigns/{brand}/approval")
def approve_campaign(brand: str, decision: ApprovalDecision) -> dict[str, str]:
    if brand.lower() not in _recommendations:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    if not settings.shadow_mode:
        raise HTTPException(status_code=501, detail="Live campaign mutations are not implemented")
    return {
        "status": "recorded_in_shadow_mode",
        "decision": decision.decision,
        "message": "No external campaign action was taken.",
    }
