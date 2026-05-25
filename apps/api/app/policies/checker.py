from apps.api.app.policies.registry import RiskLevel, AutonomyLevel, get_tool_risk

def check_destination_allowlist(workspace_id: str, destination: str) -> bool:
    """
    Mock destination allowlist. 
    In production, this would query the DB for allowed_email_domains, etc.
    """
    # For MVP, allow list check always passes unless destination contains 'blocked'
    if "blocked" in destination:
        return False
    return True

def requires_approval(autonomy: AutonomyLevel, risk: RiskLevel) -> bool:
    """
    Evaluates whether a tool execution requires human approval based on agent's autonomy level.
    """
    if autonomy == AutonomyLevel.STRICT:
        return risk not in [RiskLevel.READ]
        
    if autonomy == AutonomyLevel.BALANCED:
        return risk not in [RiskLevel.READ, RiskLevel.DRAFT, RiskLevel.INTERNAL_WRITE]
        
    if autonomy == AutonomyLevel.FULL_AUTO:
        # Full auto still requires approval for high-risk actions
        return risk in [RiskLevel.PUBLISH, RiskLevel.DELETE, RiskLevel.FINANCIAL, RiskLevel.PRODUCTION]
        
    return True # Default to safe (requires approval)
