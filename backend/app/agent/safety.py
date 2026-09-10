"""
FloodGuard: Human-in-the-Loop Safety & Policy Filter
====================================================
Ensures compliance with Section 15 of the JIIT Project Synopsis:
- "The agent will not be permitted to autonomously issue evacuation orders, 
   control physical infrastructure or represent its recommendations as official 
   emergency instructions."
- "The interface will communicate that model predictions contain uncertainty and 
   that emergency decisions require qualified human authorities."
"""

DISCLAIMER_TEXT = (
    "\n\n---\n"
    "⚠️ **Decision Support & Safety Notice**:\n"
    "FloodGuard AI outputs represent statistical estimates and predictive guidance "
    "designed to assist emergency managers. These predictions contain inherent meteorological "
    "and hydrological uncertainty. This system does NOT autonomously issue legally binding "
    "evacuation orders. All emergency response directives must be verified and authorized "
    "by competent district administration, Central Water Commission (CWC), or National Disaster "
    "Management Authority (NDMA) personnel."
)


def apply_safety_guardrails(response_text: str, risk_level: str = "Low") -> str:
    """
    Enforces non-binding wording and appends safety disclaimers.
    """
    # Replace dangerous directive phrases with decision-support phrasing
    sanitized = response_text
    replacements = {
        "you must evacuate": "recommended consideration for planned evacuation under administrative oversight",
        "evacuate immediately": "advisable to prepare for evacuation under local authority guidance",
        "i am ordering": "the model indicates elevated risk recommending",
        "open the dam gates": "consult barrage engineering staff for discharge regulation",
        "close the flood gates": "alert municipal drainage personnel to inspect floodgates"
    }
    
    for forbidden, safe in replacements.items():
        sanitized = sanitized.replace(forbidden, safe)
        sanitized = sanitized.replace(forbidden.capitalize(), safe.capitalize())
        
    if "Decision Support & Safety Notice" not in sanitized:
        sanitized += DISCLAIMER_TEXT
        
    return sanitized
