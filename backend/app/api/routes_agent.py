"""
FloodGuard: Agentic AI Assistant Routes
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from ..agent.flood_agent import flood_agent
from ..mcp.server import list_tools

router = APIRouter(prefix="/api/agent", tags=["Agentic AI Assistant"])


class AgentQueryRequest(BaseModel):
    query: str


@router.post("/query")
def query_flood_agent(payload: AgentQueryRequest):
    """
    Executes the multi-step Agentic AI loop (ReAct):
    - Formulates an explicit investigation plan.
    - Dynamically queries MCP tools.
    - Synthesizes an evidence-grounded risk assessment.
    - Applies human-in-the-loop safety guardrails.
    """
    result = flood_agent.run_agentic_workflow(payload.query)
    return result


@router.get("/tools")
def get_available_agent_tools():
    """Returns the registered Model Context Protocol (MCP) tools."""
    return {"tools": list_tools()}
