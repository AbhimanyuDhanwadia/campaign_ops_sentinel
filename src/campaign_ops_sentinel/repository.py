from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from campaign_ops_sentinel.database import AuditEvent, CampaignRun
from campaign_ops_sentinel.models import ApprovalDecision, CampaignRecommendation


def save_recommendation(
    db: Session, recommendation: CampaignRecommendation, request_id: str
) -> CampaignRecommendation:
    payload = recommendation.model_dump(mode="json")
    db.add(
        CampaignRun(
            id=str(recommendation.id),
            brand=recommendation.brief.brand,
            status=recommendation.proposed_action,
            recommendation=payload,
        )
    )
    db.add(
        AuditEvent(
            recommendation_id=str(recommendation.id),
            event_type="recommendation.created",
            actor="system",
            request_id=request_id,
            payload={"status": recommendation.proposed_action},
        )
    )
    db.commit()
    return recommendation


def get_recommendation(db: Session, recommendation_id: UUID) -> CampaignRecommendation | None:
    run = db.get(CampaignRun, str(recommendation_id))
    return CampaignRecommendation.model_validate(run.recommendation) if run else None


def record_approval(
    db: Session, recommendation_id: UUID, decision: ApprovalDecision, request_id: str
) -> bool:
    run = db.get(CampaignRun, str(recommendation_id))
    if not run:
        return False
    run.status = f"approval_{decision.decision}"
    db.add(
        AuditEvent(
            recommendation_id=str(recommendation_id),
            event_type=f"approval.{decision.decision}",
            actor=decision.reviewer,
            request_id=request_id,
            payload={"note": decision.note},
        )
    )
    db.commit()
    return True


def list_audit_events(db: Session, recommendation_id: UUID) -> list[AuditEvent]:
    statement = (
        select(AuditEvent)
        .where(AuditEvent.recommendation_id == str(recommendation_id))
        .order_by(AuditEvent.id)
    )
    return list(db.scalars(statement))
