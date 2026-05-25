from enum import Enum

class RiskLevel(str, Enum):
    READ = "READ"
    DRAFT = "DRAFT"
    INTERNAL_WRITE = "INTERNAL_WRITE"
    EXTERNAL_WRITE = "EXTERNAL_WRITE"
    PUBLISH = "PUBLISH"
    DELETE = "DELETE"
    FINANCIAL = "FINANCIAL"
    PRODUCTION = "PRODUCTION"

class AutonomyLevel(str, Enum):
    STRICT = "STRICT"
    BALANCED = "BALANCED"
    FULL_AUTO = "FULL_AUTO"

# Mock Tool Registry Mapping Tool Names to Risk Levels
TOOL_REGISTRY = {
    "gmail.search": RiskLevel.READ,
    "gmail.create_draft": RiskLevel.DRAFT,
    "gmail.send": RiskLevel.EXTERNAL_WRITE,
    "slack.send_message": RiskLevel.EXTERNAL_WRITE,
    "github.create_issue": RiskLevel.EXTERNAL_WRITE,
    "github.merge_pr": RiskLevel.PRODUCTION,
    "notion.create_page": RiskLevel.INTERNAL_WRITE,
    "notion.delete_page": RiskLevel.DELETE,
    "stripe.refund": RiskLevel.FINANCIAL,
    "instagram.publish": RiskLevel.PUBLISH,
    "e2b.run_code": RiskLevel.PRODUCTION,
}

def get_tool_risk(tool_name: str) -> str:
    return TOOL_REGISTRY.get(tool_name, RiskLevel.PRODUCTION) # Default to highest risk if unknown
