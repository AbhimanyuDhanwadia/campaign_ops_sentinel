from campaign_ops_sentinel.models import CampaignBrief, PolicyFinding

MAX_SHADOW_BUDGET_INR = 2_000_000


def review_campaign(brief: CampaignBrief) -> list[PolicyFinding]:
    findings: list[PolicyFinding] = []
    if brief.budget_inr > MAX_SHADOW_BUDGET_INR:
        findings.append(
            PolicyFinding(
                rule_id="BUDGET-001",
                severity="review",
                explanation=(
                    f"Budget exceeds the {MAX_SHADOW_BUDGET_INR:,} INR automatic planning threshold."
                ),
            )
        )
    if "http://" in str(brief.destination_url):
        findings.append(
            PolicyFinding(
                rule_id="URL-001",
                severity="block",
                explanation="Destination URLs must use HTTPS.",
            )
        )
    return findings
