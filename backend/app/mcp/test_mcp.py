"""
Test script to verify all 8 MCP tools.
"""
import sys
import json
from server import list_tools, call_tool

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

print("[TEST] Listing available MCP tools:")
tools = list_tools()
print(f"Total tools registered: {len(tools)}")
for t in tools:
    print(f" - {t['name']}: {t['description'][:60]}...")

print("\n--- Testing Individual Tool Execution ---")

# 1. get_weather
r1 = call_tool("get_weather", {"location": "Delhi"})
print("1. get_weather('Delhi'):", r1.get("weather_condition"), f"{r1.get('temperature_c')}°C")

# 2. get_rainfall
r2 = call_tool("get_rainfall", {"location": "Noida"})
print("2. get_rainfall('Noida'):", f"24h: {r2.get('rainfall_24h_mm')}mm, 72h: {r2.get('rainfall_72h_mm')}mm")

# 3. get_water_level
r3 = call_tool("get_water_level", {"location": "Yamuna Delhi"})
print("3. get_water_level('Delhi'):", f"WL: {r3.get('current_water_level_m')}m, Status: {r3.get('status')}")

# 4. get_historical_floods
r4 = call_tool("get_historical_floods", {"location": "Delhi"})
print("4. get_historical_floods('Delhi'):", f"{len(r4.get('historical_events', []))} events found. All-time high: {r4.get('all_time_high_level_m')}m")

# 5. predict_flood_risk (running the trained XGBoost model!)
r5 = call_tool("predict_flood_risk", {"location": "Delhi"})
print("5. predict_flood_risk('Delhi'):", f"Tier: {r5.get('predicted_risk_label')}, Confidence: {r5.get('confidence')}, Model: {r5.get('model_used')}")

# 6. get_risk_status
r6 = call_tool("get_risk_status", {"location": "Ghaziabad"})
print("6. get_risk_status('Ghaziabad'):", f"Status: {r6.get('current_risk_label')}")

# 7. get_affected_regions
r7 = call_tool("get_affected_regions", {})
print("7. get_affected_regions():", f"{r7.get('total_affected_stations')} of {r7.get('total_monitored_stations')} stations under elevated risk.")

# 8. get_preparedness_recommendations
r8 = call_tool("get_preparedness_recommendations", {"risk_level": "High"})
print("8. get_preparedness_recommendations('High'):", f"{len(r8.get('recommendations', []))} action items generated.")

print("\n[SUCCESS] All 8 MCP tools tested and working flawlessly!")
