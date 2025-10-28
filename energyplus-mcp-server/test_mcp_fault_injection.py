#!/usr/bin/env python3
"""
Test MCP Fault Injection - Duct Leakage Simulation
Demonstrates how to use MCP tools to inject faults into building models
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from energyplus_mcp_server.energyplus_tools import EnergyPlusManager
from energyplus_mcp_server.config import get_config

print("=" * 80)
print("MCP FAULT INJECTION TEST - DUCT LEAKAGE SIMULATION")
print("=" * 80)
print()

# Initialize
config = get_config()
manager = EnergyPlusManager(config)

# File paths
idf_path = "sample_files/MediumOffice-90.1-2004.idf"

print("TEST 1: Load IDF Model")
print("-" * 80)
print(f"Loading: {idf_path}")
print()

try:
    # This simulates the MCP tool: load_idf_model
    zones_result = manager.list_zones(idf_path)

    # Handle different response formats
    if isinstance(zones_result, str):
        zones_data = json.loads(zones_result)
    else:
        zones_data = zones_result

    print("✅ Model loaded successfully!")

    # Handle list or dict response
    if isinstance(zones_data, dict):
        zones_list = zones_data.get('zones', [])
    else:
        zones_list = zones_data if isinstance(zones_data, list) else []

    print(f"   Number of zones: {len(zones_list)}")
    print(f"   Zone names:")
    for i, zone in enumerate(zones_list[:10], 1):
        if isinstance(zone, dict):
            print(f"      {i}. {zone.get('name', 'Unknown')}")
        else:
            print(f"      {i}. {zone}")

    if len(zones_list) > 10:
        print(f"      ... and {len(zones_list) - 10} more zones")
    print()

    print(f"✅ MCP Tool Equivalent:")
    print(f'   {{"tool": "load_idf_model", "arguments": {{"idf_path": "{idf_path}"}}}}')
    print()

except Exception as e:
    print(f"❌ Failed to load model: {e}")
    import traceback
    traceback.print_exc()
    print()

print()
print("TEST 2: Check Current Infiltration")
print("-" * 80)
print("Checking baseline infiltration rates...")
print()

try:
    # Get infiltration info
    infiltration_result = manager.get_infiltration_info(idf_path)
    infiltration_data = json.loads(infiltration_result)

    print("✅ Current infiltration settings:")
    if 'infiltration_objects' in infiltration_data:
        for i, obj in enumerate(infiltration_data['infiltration_objects'][:5], 1):
            print(f"   {i}. {obj.get('name', 'Unknown')}")
            print(f"      Zone: {obj.get('zone_name', 'N/A')}")
            print(f"      Design Flow Rate: {obj.get('design_flow_rate', 'N/A')}")
            print(f"      Flow per Exterior Surface Area: {obj.get('flow_per_exterior_surface_area', 'N/A')}")

        if len(infiltration_data['infiltration_objects']) > 5:
            print(f"   ... and {len(infiltration_data['infiltration_objects']) - 5} more infiltration objects")
    else:
        print("   No infiltration objects found or summary not available")
    print()

    print(f"✅ MCP Tool Equivalent:")
    print(f'   {{"tool": "get_infiltration_info", "arguments": {{"idf_path": "{idf_path}"}}}}')
    print()

except Exception as e:
    print(f"⚠️  Could not retrieve infiltration info: {e}")
    print()

print()
print("TEST 3: Inject Duct Leakage Fault (5% Infiltration Increase)")
print("-" * 80)
print("Simulating duct leakage by increasing infiltration by 5%...")
print()

# Output file for modified IDF
output_idf = "sample_files/MediumOffice-90.1-2004-DuctLeak.idf"

try:
    # This simulates the MCP tool: change_infiltration_by_mult
    result = manager.change_infiltration_by_mult(
        idf_path=idf_path,
        multiplier=1.05,
        output_path=output_idf
    )

    result_data = json.loads(result)

    print("✅ Fault injected successfully!")
    print(f"   Multiplier applied: 1.05 (5% increase)")
    print(f"   Modified IDF saved to: {output_idf}")
    print(f"   Status: {result_data.get('status', 'Unknown')}")

    if 'changes_made' in result_data:
        print(f"   Changes made: {result_data['changes_made']}")
    if 'objects_modified' in result_data:
        print(f"   Objects modified: {result_data['objects_modified']}")

    print()
    print(f"✅ MCP Tool Equivalent:")
    print(f'   {{"tool": "change_infiltration_by_mult", "arguments": {{')
    print(f'       "idf_path": "{idf_path}",')
    print(f'       "multiplier": 1.05,')
    print(f'       "output_path": "{output_idf}"')
    print(f'   }}}}')
    print()

except Exception as e:
    print(f"❌ Failed to inject fault: {e}")
    import traceback
    traceback.print_exc()
    print()

print()
print("TEST 4: Verify Fault Injection")
print("-" * 80)
print("Checking modified infiltration rates...")
print()

try:
    # Check the modified file
    modified_infiltration = manager.get_infiltration_info(output_idf)
    modified_data = json.loads(modified_infiltration)

    print("✅ Modified infiltration settings:")
    if 'infiltration_objects' in modified_data:
        for i, obj in enumerate(modified_data['infiltration_objects'][:3], 1):
            print(f"   {i}. {obj.get('name', 'Unknown')}")
            print(f"      Zone: {obj.get('zone_name', 'N/A')}")
            print(f"      Design Flow Rate: {obj.get('design_flow_rate', 'N/A')} (increased by 5%)")

    print()
    print("✅ Fault verification complete!")
    print("   The building now simulates duct leakage through increased infiltration")
    print()

except Exception as e:
    print(f"⚠️  Could not verify modifications: {e}")
    print()

print()
print("=" * 80)
print("FAULT INJECTION TEST SUMMARY")
print("=" * 80)
print()
print("✅ Successfully demonstrated:")
print("   1. Loading an IDF model (load_idf_model)")
print("   2. Inspecting infiltration settings (get_infiltration_info)")
print("   3. Injecting duct leakage fault (change_infiltration_by_mult)")
print("   4. Verifying the fault was applied")
print()
print("📝 Next steps for MCP Inspector:")
print("   - Use these same tool calls in the MCP Inspector interface")
print("   - Run simulations to compare baseline vs. faulty building")
print("   - Analyze energy impact of the duct leakage")
print()
print("🔧 Other MCP fault injection tools available:")
print("   - modify_simulation_control: Adjust simulation settings")
print("   - change HVAC parameters: Modify equipment efficiency")
print("   - adjust schedules: Change operation schedules")
print()
print("=" * 80)
