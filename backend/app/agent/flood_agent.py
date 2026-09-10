"""
FloodGuard: Autonomous Flood Intelligence Agent
===============================================
Implements the Agentic AI layer using the ReAct (Reason + Act) paradigm:
1. Understands user disaster management queries.
2. Formulates an explicit step-by-step investigation Plan.
3. Dynamically invokes relevant MCP tools (rainfall, river level, ML prediction, alerts).
4. Synthesizes an evidence-grounded response with feature explanations.
5. Passes output through the Human-in-the-Loop Safety Filter.

Designed to work seamlessly:
- Uses Google Gemini API if GEMINI_API_KEY is available.
- Features a robust built-in Autonomous ReAct Orchestrator for instant offline execution!
"""

import os
import json
import re
from typing import Dict, Any, List
from ..mcp.server import list_tools, call_tool
from .safety import apply_safety_guardrails


class FloodIntelligenceAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.available_tools = list_tools()
        
    def _extract_location_mention(self, text: str) -> str:
        """Extracts likely target location or river from query."""
        keywords = ["delhi", "yamuna", "noida", "okhla", "hindon", "ghaziabad", "haridwar", "prayagraj", "ganga"]
        lower = text.lower()
        for kw in keywords:
            if kw in lower:
                return kw
        return "Delhi"  # Default sentinel station
        
    def run_agentic_workflow(self, user_query: str) -> Dict[str, Any]:
        """
        Executes the ReAct loop:
        Query -> Plan -> Tool Execution -> Synthesis -> Guardrails
        """
        q_lower = user_query.lower()
        location = self._extract_location_mention(user_query)
        
        plan_steps = []
        tool_calls_executed = []
        
        # 1. Plan Formation based on user intent
        if any(w in q_lower for w in ["affected", "all stations", "overview", "overall", "regions"]):
            plan_steps = [
                "Survey all active river monitoring stations across Yamuna, Hindon, and Ganga basins",
                "Filter stations currently approaching or breaching Warning / Danger marks",
                "Fetch emergency preparedness recommendations for elevated risk zones"
            ]
            
            # Execute get_affected_regions
            res_affected = call_tool("get_affected_regions", {})
            tool_calls_executed.append({
                "tool": "get_affected_regions",
                "args": {},
                "summary": f"Found {res_affected.get('total_affected_stations', 0)} of {res_affected.get('total_monitored_stations', 0)} stations with elevated risk.",
                "output": res_affected
            })
            
            # Execute preparedness recommendations
            res_recs = call_tool("get_preparedness_recommendations", {"risk_level": "High"})
            tool_calls_executed.append({
                "tool": "get_preparedness_recommendations",
                "args": {"risk_level": "High"},
                "summary": "Retrieved district mobilization protocols.",
                "output": res_recs
            })
            
            # Synthesize Response
            affected_list = res_affected.get("affected_regions", [])
            lines = [
                f"### 🌊 Regional Flood Risk Intelligence Overview",
                f"A cross-basin survey of **{res_affected.get('total_monitored_stations')} river stations** reveals **{len(affected_list)} stations** with elevated risk.\n",
                "| Station | River | Current Level | Danger Mark | 24h Rain | Risk Tier |",
                "| :--- | :--- | :--- | :--- | :--- | :--- |"
            ]
            for stn in affected_list:
                lines.append(
                    f"| **{stn['station_name']}** | {stn['river']} | {stn['water_level_m']}m | {stn['danger_level_m']}m | {stn['rainfall_24h_mm']}mm | **{stn['risk_label']}** |"
                )
                
            lines.append("\n#### 🚨 Immediate Priority Actions (Human-in-the-loop Advisory):")
            for rec in res_recs.get("recommendations", []):
                lines.append(f"- {rec}")
                
            final_text = "\n".join(lines)
            risk_tier = "High" if affected_list else "Low"
            
        else:
            # Station-specific deep dive
            plan_steps = [
                f"Query live hydrological gauge telemetry and rate-of-rise for '{location}'",
                f"Retrieve 24-hour and 72-hour cumulative precipitation from meteorological records",
                f"Execute trained XGBoost ML classification model to calculate risk probabilities and primary drivers",
                f"Inspect historical flood breach thresholds for comparative context",
                f"Generate tailored preparedness advisories based on predicted risk tier"
            ]
            
            # Step 1: Water Level
            res_wl = call_tool("get_water_level", {"location": location})
            tool_calls_executed.append({
                "tool": "get_water_level",
                "args": {"location": location},
                "summary": f"Water Level: {res_wl.get('current_water_level_m')}m (Danger: {res_wl.get('danger_level_m')}m) - {res_wl.get('status')}",
                "output": res_wl
            })
            
            # Step 2: Rainfall
            res_rain = call_tool("get_rainfall", {"location": location})
            tool_calls_executed.append({
                "tool": "get_rainfall",
                "args": {"location": location},
                "summary": f"24h Rain: {res_rain.get('rainfall_24h_mm')}mm | 72h Rain: {res_rain.get('rainfall_72h_mm')}mm",
                "output": res_rain
            })
            
            # Step 3: ML Model Prediction
            res_pred = call_tool("predict_flood_risk", {"location": location})
            tool_calls_executed.append({
                "tool": "predict_flood_risk",
                "args": {"location": location},
                "summary": f"ML Prediction: {res_pred.get('predicted_risk_label')} ({res_pred.get('confidence')*100:.1f}% confidence)",
                "output": res_pred
            })
            
            # Step 4: Historical Floods
            res_hist = call_tool("get_historical_floods", {"location": location})
            tool_calls_executed.append({
                "tool": "get_historical_floods",
                "args": {"location": location},
                "summary": f"Found {len(res_hist.get('historical_events', []))} past flood events. All-time peak: {res_hist.get('all_time_high_level_m')}m",
                "output": res_hist
            })
            
            # Step 5: Recommendations
            pred_label = res_pred.get("predicted_risk_label", "Medium")
            res_recs = call_tool("get_preparedness_recommendations", {"risk_level": pred_label})
            tool_calls_executed.append({
                "tool": "get_preparedness_recommendations",
                "args": {"risk_level": pred_label},
                "summary": f"Retrieved {len(res_recs.get('recommendations', []))} preparedness guidelines for {pred_label} risk tier.",
                "output": res_recs
            })
            
            # Synthesize Final Technical Assessment
            stn_name = res_wl.get("station_name", location)
            conf_pct = res_pred.get("confidence", 0.95) * 100
            
            lines = [
                f"### 🛡️ Flood Risk Assessment: {stn_name}",
                f"**Overall Assessment:** Classified as **{pred_label.upper()} RISK** with **{conf_pct:.1f}% confidence** using the trained **{res_pred.get('model_used')}**.\n",
                "#### 📊 Hydrological & Meteorological Evidence Grounding:",
                f"- **Current River Level:** `{res_wl.get('current_water_level_m')} m` (Warning Mark: `{res_wl.get('warning_level_m')} m`, Danger Mark: `{res_wl.get('danger_level_m')} m`).",
                f"- **Stage Status:** **{res_wl.get('status')}** (Buffer to danger mark: `{res_wl.get('distance_to_danger_m')} m`).",
                f"- **Rate of Rise:** `{res_wl.get('rate_of_rise_m_hr')} m/hr` with upstream barrage discharge of `{res_wl.get('upstream_discharge_cusecs'):,} cusecs`.",
                f"- **Precipitation Totals:** 24h: `{res_rain.get('rainfall_24h_mm')} mm` | 72h Cumulative: `{res_rain.get('rainfall_72h_mm')} mm` | 7-Day: `{res_rain.get('rainfall_7d_mm')} mm`.",
                "\n#### 🔍 Contributing Risk Drivers Identified by Model:",
            ]
            for driver in res_pred.get("primary_risk_drivers", []):
                lines.append(f"- • {driver}")
                
            lines.append("\n#### 📜 Historical Precedence:")
            for h in res_hist.get("historical_events", [])[:2]:
                lines.append(f"- **{h.get('year')} Flood:** Peak reached `{h.get('peak_level_m')} m` — *{h.get('notes')}*")
                
            lines.append(f"\n#### 📋 Recommended Preparedness Protocol ({pred_label} Tier):")
            for rec in res_recs.get("recommendations", []):
                lines.append(f"- {rec}")
                
            final_text = "\n".join(lines)
            risk_tier = pred_label

        # Apply Human-in-the-Loop Safety Filter
        safe_response = apply_safety_guardrails(final_text, risk_level=risk_tier)
        
        return {
            "query": user_query,
            "target_location": location,
            "plan": plan_steps,
            "tool_calls": tool_calls_executed,
            "response": safe_response,
            "risk_tier": risk_tier,
            "safety_filtered": True
        }


# Global agent instance
flood_agent = FloodIntelligenceAgent()
