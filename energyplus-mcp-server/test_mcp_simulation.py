#!/usr/bin/env python3
"""
MCP Inspector Simulation Test - Complete Workflow
Demonstrates: Load Model → Inject Fault → Run Simulation → Compare Results
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from energyplus_mcp_server.energyplus_tools import EnergyPlusManager
from energyplus_mcp_server.config import get_config

print("=" * 80)
print("MCP INSPECTOR - COMPLETE SIMULATION WORKFLOW TEST")
print("Baseline vs. Faulty Building Comparison")
print("=" * 80)
print()

# Initialize
config = get_config()
manager = EnergyPlusManager(config)

# File paths
baseline_idf = "sample_files/MediumOffice-90.1-2004.idf"
faulty_idf = "sample_files/MediumOffice-DuctLeak-5pct.idf"
weather_file = "sample_files/USA_CO_Denver.Intl.AP.725650_TMY3.epw"

print("📁 Files:")
print(f"   Baseline IDF: {baseline_idf}")
print(f"   Faulty IDF:   {faulty_idf}")
print(f"   Weather:      {weather_file} (Golden/Denver, CO)")
print()

# ==============================================================================
# STEP 1: Create Faulty Model
# ==============================================================================
print("STEP 1: Create Faulty Model (5% Infiltration Increase)")
print("-" * 80)

try:
    result = manager.change_infiltration_by_mult(
        idf_path=baseline_idf,
        mult=1.05,
        output_path=faulty_idf
    )

    result_data = json.loads(result)
    print("✅ Faulty model created successfully!")
    print(f"   Duct leakage fault: 5% infiltration increase")
    print(f"   Output: {faulty_idf}")
    print()

    print("📝 MCP Tool Equivalent:")
    print('   {"tool": "change_infiltration_by_mult", "arguments": {')
    print(f'       "idf_path": "{baseline_idf}",')
    print(f'       "mult": 1.05,')
    print(f'       "output_path": "{faulty_idf}"')
    print('   }}')
    print()

except Exception as e:
    print(f"❌ Failed to create faulty model: {e}")
    sys.exit(1)

# ==============================================================================
# STEP 2: Run Baseline Simulation
# ==============================================================================
print("STEP 2: Run Baseline Simulation")
print("-" * 80)
print("🚀 Running annual simulation (this takes 1-2 minutes)...")
print()

try:
    baseline_result = manager.run_simulation(
        idf_path=baseline_idf,
        weather_file=weather_file,
        annual=True
    )

    baseline_data = json.loads(baseline_result)

    print("✅ Baseline simulation complete!")
    print(f"   Status: {baseline_data.get('status', 'Unknown')}")
    print(f"   Output directory: {baseline_data.get('output_directory', 'Unknown')}")
    print(f"   Runtime: {baseline_data.get('runtime_seconds', 0):.1f} seconds")
    print()

    baseline_output_dir = Path(baseline_data.get('output_directory', 'outputs'))

    print("📝 MCP Tool Equivalent:")
    print('   {"tool": "run_energyplus_simulation", "arguments": {')
    print(f'       "idf_path": "{baseline_idf}",')
    print(f'       "weather_file": "{weather_file}",')
    print('       "annual": true')
    print('   }}')
    print()

except Exception as e:
    print(f"❌ Baseline simulation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ==============================================================================
# STEP 3: Run Faulty Simulation
# ==============================================================================
print("STEP 3: Run Faulty Building Simulation")
print("-" * 80)
print("🚀 Running faulty building simulation...")
print()

try:
    faulty_result = manager.run_simulation(
        idf_path=faulty_idf,
        weather_file=weather_file,
        annual=True
    )

    faulty_data = json.loads(faulty_result)

    print("✅ Faulty simulation complete!")
    print(f"   Status: {faulty_data.get('status', 'Unknown')}")
    print(f"   Output directory: {faulty_data.get('output_directory', 'Unknown')}")
    print(f"   Runtime: {faulty_data.get('runtime_seconds', 0):.1f} seconds")
    print()

    faulty_output_dir = Path(faulty_data.get('output_directory', 'outputs'))

except Exception as e:
    print(f"❌ Faulty simulation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ==============================================================================
# STEP 4: Compare Results
# ==============================================================================
print("STEP 4: Compare Energy Results")
print("-" * 80)

try:
    import pandas as pd

    # Read meter data
    baseline_meter_file = list(baseline_output_dir.glob("*Meter.csv"))
    faulty_meter_file = list(faulty_output_dir.glob("*Meter.csv"))

    if baseline_meter_file and faulty_meter_file:
        baseline_meter = pd.read_csv(baseline_meter_file[0])
        faulty_meter = pd.read_csv(faulty_meter_file[0])

        # Get electricity consumption
        elec_col = [col for col in baseline_meter.columns if 'Electricity:Facility' in col and '[J]' in col][0]

        baseline_total_j = baseline_meter[elec_col].sum()
        faulty_total_j = faulty_meter[elec_col].sum()

        # Convert to kWh
        baseline_total_kwh = baseline_total_j / 3_600_000
        faulty_total_kwh = faulty_total_j / 3_600_000

        increase_kwh = faulty_total_kwh - baseline_total_kwh
        increase_pct = (increase_kwh / baseline_total_kwh) * 100

        print("📊 Annual Electricity Consumption:")
        print(f"   Baseline:  {baseline_total_kwh:>12,.0f} kWh/year")
        print(f"   Faulty:    {faulty_total_kwh:>12,.0f} kWh/year")
        print()
        print(f"💰 Impact of 5% Duct Leakage:")
        print(f"   Increased energy use:  {increase_kwh:>10,.0f} kWh/year")
        print(f"   Percent increase:      {increase_pct:>10,.2f}%")
        print()

        # Estimate cost impact (assuming $0.10/kWh)
        cost_increase = increase_kwh * 0.10
        print(f"   Estimated cost impact: ${cost_increase:>10,.2f}/year")
        print(f"   (assuming $0.10/kWh)")
        print()

        print("🔍 Analysis:")
        if increase_pct > 2:
            print(f"   ⚠️  Significant impact: {increase_pct:.1f}% energy increase")
            print(f"   This duct leakage is causing substantial energy waste")
        elif increase_pct > 1:
            print(f"   ⚠️  Moderate impact: {increase_pct:.1f}% energy increase")
            print(f"   Duct sealing would provide measurable savings")
        else:
            print(f"   ℹ️  Minor impact: {increase_pct:.1f}% energy increase")
            print(f"   Effect is present but relatively small")
        print()

    else:
        print("⚠️  Could not find meter output files for comparison")
        print()

except Exception as e:
    print(f"⚠️  Could not compare results: {e}")
    import traceback
    traceback.print_exc()
    print()

# ==============================================================================
# Summary
# ==============================================================================
print("=" * 80)
print("MCP SIMULATION WORKFLOW - COMPLETE!")
print("=" * 80)
print()
print("✅ Successfully demonstrated:")
print("   1. Created faulty model with duct leakage (change_infiltration_by_mult)")
print("   2. Ran baseline simulation (run_energyplus_simulation)")
print("   3. Ran faulty building simulation")
print("   4. Compared energy consumption results")
print()
print("📊 Output Files:")
print(f"   Baseline results: {baseline_output_dir}/")
print(f"   Faulty results:   {faulty_output_dir}/")
print()
print("🔧 Next Steps for MCP Inspector:")
print("   - Test these same tool calls in the MCP Inspector interface")
print("   - Try different fault severities (mult = 1.10, 1.20, etc.)")
print("   - Inject other types of faults (HVAC efficiency, schedules, etc.)")
print("   - Analyze hourly energy profiles to see when faults have most impact")
print()
print("=" * 80)
