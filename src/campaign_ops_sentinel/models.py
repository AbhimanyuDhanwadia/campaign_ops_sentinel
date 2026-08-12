from datetime import date
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


class Objective(StrEnum):
    ATTENTION = "attention"
    VIDEO_COMPLETION = "video_completion"
    ENGAGEMENT = "engagement"


class CampaignBrief(BaseModel):
    brand: str = Field(min_length=2, max_length=80)
    budget_inr: int = Field(gt=0, le=10_000_000)
    markets: list[str] = Field(min_length=1)
    audience: str = Field(min_length=3, max_length=300)
    objective: Objective
    start_date: date
    end_date: date
    formats: list[Literal["display", "video", "playable"]] = Field(min_length=1)
    destination_url: HttpUrl

    @field_validator("end_date")
    @classmethod
    def end_must_not_precede_start(cls, end_date: date, info):
        start_date = info.data.get("start_date")
        if start_date and end_date < start_date:
            raise ValueError("end_date must be on or after start_date")
        return end_date


class PolicyFinding(BaseModel):
    rule_id: str
    severity: Literal["block", "review", "info"]
    explanation: str


class InventoryOption(BaseModel):
    placement_id: str
    game_title: str
    market: str
    format: str
    attention_score: float
    estimated_cpm_inr: int


class CampaignRecommendation(BaseModel):
    brief: CampaignBrief
    policy_findings: list[PolicyFinding]
    inventory: list[InventoryOption]
    proposed_daily_budget_inr: int
    proposed_action: Literal["shadow_created", "blocked"]
    approval_required: bool = True
    rationale: str


class ApprovalDecision(BaseModel):
    decision: Literal["approve", "reject"]
    reviewer: str = Field(min_length=2, max_length=80)
    note: str | None = Field(default=None, max_length=500)
