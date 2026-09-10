"""
FloodGuard: MCP Server Definition & Registry
============================================
Exposes tools according to the Model Context Protocol (MCP) standard,
allowing an Agentic LLM to inspect tool schemas and execute them safely.
"""

from typing import Dict, Any, List
import json
try:
    from . import tools
except ImportError:
    import tools

MCP_TOOL_REGISTRY = [
    {
        "name": "get_weather",
        "description": "Retrieves temperature, humidity, atmospheric condition, and soil moisture for a station or river reach.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Station ID, river name, or region (e.g. 'Delhi', 'Noida', 'Yamuna', 'Hindon')"},
                "time_range": {"type": "string", "description": "Time range for weather data, e.g. 'current', '24h'", "default": "current"}
            },
            "required": ["location"]
        }
    },
    {
        "name": "get_rainfall",
        "description": "Retrieves 1-hour, 24-hour, 72-hour, and 7-day cumulative precipitation and rainfall intensity for a location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Location name, river, or station ID (e.g. 'Okhla', 'Delhi', 'Haridwar')"},
                "time_range": {"type": "string", "description": "Time interval, e.g. '24h', '72h'", "default": "24h"}
            },
            "required": ["location"]
        }
    },
    {
        "name": "get_water_level",
        "description": "Retrieves current river gauge height, rate-of-rise, and status relative to warning and danger marks.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Station ID or river location (e.g. 'Delhi', 'Noida 135', 'Ghaziabad')"},
                "time_range": {"type": "string", "description": "Time window", "default": "current"}
            },
            "required": ["location"]
        }
    },
    {
        "name": "get_historical_floods",
        "description": "Returns historical peak flood events, all-time high water marks, and breach records for the given location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Location or station name (e.g. 'Delhi', 'Haridwar', 'Prayagraj')"}
            },
            "required": ["location"]
        }
    },
    {
        "name": "predict_flood_risk",
        "description": "Runs the trained XGBoost supervised machine learning model to estimate flood risk tier (Low, Medium, High, Critical), class probabilities, and top risk factors.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Monitoring station or region name"},
                "feature_override": {"type": "object", "description": "Optional dictionary of simulated features to test what-if scenarios"}
            }
        }
    },
    {
        "name": "get_risk_status",
        "description": "Returns a rapid consolidated health check of risk status, current water level, rainfall, and key risk drivers.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Monitoring station or location to inspect"}
            },
            "required": ["location"]
        }
    },
    {
        "name": "get_affected_regions",
        "description": "Surveys all monitored river stations and returns a list of regions currently under elevated risk (Medium, High, or Critical).",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_preparedness_recommendations",
        "description": "Generates non-binding emergency preparedness, flood mitigation, and resource prioritization recommendations.",
        "parameters": {
            "type": "object",
            "properties": {
                "risk_level": {"type": "string", "description": "Risk level category: 'Low', 'Medium', 'High', or 'Critical'"}
            },
            "required": ["risk_level"]
        }
    }
]

TOOL_FUNCTION_MAP = {
    "get_weather": tools.get_weather,
    "get_rainfall": tools.get_rainfall,
    "get_water_level": tools.get_water_level,
    "get_historical_floods": tools.get_historical_floods,
    "predict_flood_risk": tools.predict_flood_risk,
    "get_risk_status": tools.get_risk_status,
    "get_affected_regions": tools.get_affected_regions,
    "get_preparedness_recommendations": tools.get_preparedness_recommendations,
}


def list_tools() -> List[Dict[str, Any]]:
    """Returns the schemas of all available MCP tools."""
    return MCP_TOOL_REGISTRY


def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Executes a requested MCP tool with given arguments."""
    if name not in TOOL_FUNCTION_MAP:
        return {"error": f"Tool '{name}' is not recognized in FloodGuard MCP registry."}
    try:
        func = TOOL_FUNCTION_MAP[name]
        return func(**arguments)
    except Exception as e:
        return {"error": f"Error executing tool '{name}': {str(e)}"}
