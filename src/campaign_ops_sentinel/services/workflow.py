from campaign_ops_sentinel.models import CampaignBrief, CampaignRecommendation
from campaign_ops_sentinel.services.inventory import search_inventory
from campaign_ops_sentinel.services.policy import review_campaign


def build_recommendation(brief: CampaignBrief) -> CampaignRecommendation:
    findings = review_campaign(brief)
    blocked = any(finding.severity == "block" for finding in findings)
    inventory = [] if blocked else search_inventory(brief)
    days = max((brief.end_date - brief.start_date).days + 1, 1)
    action = "blocked" if blocked else "shadow_created"
    rationale = (
        "Campaign is blocked by a policy finding."
        if blocked
        else f"Ranked {len(inventory)} eligible synthetic placements; no live mutation was made."
    )
    return CampaignRecommendation(
        id=uuid4(),
        brief=brief,
        policy_findings=findings,
        inventory=inventory,
        proposed_daily_budget_inr=brief.budget_inr // days,
        proposed_action=action,
        rationale=rationale,
    )
from uuid import uuid4
