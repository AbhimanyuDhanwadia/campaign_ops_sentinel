from campaign_ops_sentinel.models import CampaignBrief, InventoryOption

SYNTHETIC_INVENTORY = [
    InventoryOption(
        placement_id="inv_001",
        game_title="Metro Drift",
        market="IN",
        format="video",
        attention_score=0.92,
        estimated_cpm_inr=180,
    ),
    InventoryOption(
        placement_id="inv_002",
        game_title="Puzzle Planet",
        market="IN",
        format="playable",
        attention_score=0.88,
        estimated_cpm_inr=210,
    ),
    InventoryOption(
        placement_id="inv_003",
        game_title="Arena Rush",
        market="IN",
        format="display",
        attention_score=0.79,
        estimated_cpm_inr=120,
    ),
    InventoryOption(
        placement_id="inv_004",
        game_title="Sky Builders",
        market="GB",
        format="video",
        attention_score=0.86,
        estimated_cpm_inr=260,
    ),
]


def search_inventory(brief: CampaignBrief) -> list[InventoryOption]:
    matches = [
        item
        for item in SYNTHETIC_INVENTORY
        if item.market in brief.markets and item.format in brief.formats
    ]
    return sorted(matches, key=lambda item: item.attention_score, reverse=True)
