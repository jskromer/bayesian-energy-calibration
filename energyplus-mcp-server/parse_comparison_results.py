#!/usr/bin/env python3
"""
Parse and compare EnergyPlus simulation results
"""

import csv
from pathlib import Path

def parse_meter_annual_total(meter_file):
    """Extract annual totals from meter CSV (last line)"""

    with open(meter_file, 'r') as f:
        lines = f.readlines()

    # Header is first line
    header = lines[0].strip().split(',')

    # Last line has annual totals
    last_line = lines[-1].strip().split(',')

    # Create dictionary of annual values
    annual_data = {}

    # Find key metrics
    for i, col_name in enumerate(header):
        if i < len(last_line):
            # Look for annual totals (columns with Monthly in header that appear at end)
            if '(Monthly)' in col_name and i >= 9:  # Monthly columns start after hourly
                try:
                    value = float(last_line[i])
                    clean_name = col_name.replace(' [J](Monthly)', '').replace(' [m3](Monthly)', '')
                    annual_data[clean_name] = value
                except:
                    pass

    return annual_data

def format_energy(joules):
    """Convert Joules to more readable units"""
    kwh = joules / 3_600_000
    gj = joules / 1_000_000_000
    return {
        'J': joules,
        'kWh': kwh,
        'GJ': gj,
        'MWh': kwh / 1000
    }

def compare_results(baseline_dir, improved_dir):
    """Compare baseline vs improved results"""

    baseline_meter = baseline_dir / "eplusmtr.csv"
    improved_meter = improved_dir / "eplusmtr.csv"

    print("\n" + "="*80)
    print("ENERGYPLUS SIMULATION COMPARISON RESULTS")
    print("="*80)

    baseline_data = parse_meter_annual_total(baseline_meter)
    improved_data = parse_meter_annual_total(improved_meter)

    print(f"\n📊 BASELINE: MediumOffice-90.1-2004 (Standard)")
    print(f"   Location: {baseline_dir}")
    print(f"\n   Annual Energy Consumption:")

    if 'Electricity:Facility' in baseline_data:
        elec = format_energy(baseline_data['Electricity:Facility'])
        print(f"      Electricity: {elec['kWh']:,.0f} kWh ({elec['GJ']:.1f} GJ)")

    if 'NaturalGas:Facility' in baseline_data:
        gas = format_energy(baseline_data['NaturalGas:Facility'])
        print(f"      Natural Gas: {gas['kWh']:,.0f} kWh ({gas['GJ']:.1f} GJ)")

    # Calculate total site energy
    baseline_total = baseline_data.get('Electricity:Facility', 0) + baseline_data.get('NaturalGas:Facility', 0)
    baseline_total_fmt = format_energy(baseline_total)
    print(f"      TOTAL SITE ENERGY: {baseline_total_fmt['kWh']:,.0f} kWh ({baseline_total_fmt['GJ']:.1f} GJ)")

    print(f"\n📊 IMPROVED: MediumOffice with Better Duct Sealing (5% leak)")
    print(f"   Location: {improved_dir}")
    print(f"\n   Annual Energy Consumption:")

    if 'Electricity:Facility' in improved_data:
        elec = format_energy(improved_data['Electricity:Facility'])
        print(f"      Electricity: {elec['kWh']:,.0f} kWh ({elec['GJ']:.1f} GJ)")

    if 'NaturalGas:Facility' in improved_data:
        gas = format_energy(improved_data['NaturalGas:Facility'])
        print(f"      Natural Gas: {gas['kWh']:,.0f} kWh ({gas['GJ']:.1f} GJ)")

    # Calculate total site energy
    improved_total = improved_data.get('Electricity:Facility', 0) + improved_data.get('NaturalGas:Facility', 0)
    improved_total_fmt = format_energy(improved_total)
    print(f"      TOTAL SITE ENERGY: {improved_total_fmt['kWh']:,.0f} kWh ({improved_total_fmt['GJ']:.1f} GJ)")

    # Calculate savings
    print(f"\n💰 ENERGY SAVINGS (Baseline - Improved):")
    print(f"   {'='*60}")

    elec_savings = baseline_data.get('Electricity:Facility', 0) - improved_data.get('Electricity:Facility', 0)
    elec_savings_fmt = format_energy(elec_savings)
    elec_pct = (elec_savings / baseline_data.get('Electricity:Facility', 1)) * 100
    print(f"   Electricity: {elec_savings_fmt['kWh']:,.0f} kWh ({elec_pct:.1f}%)")

    gas_savings = baseline_data.get('NaturalGas:Facility', 0) - improved_data.get('NaturalGas:Facility', 0)
    gas_savings_fmt = format_energy(gas_savings)
    gas_pct = (gas_savings / baseline_data.get('NaturalGas:Facility', 1)) * 100
    print(f"   Natural Gas: {gas_savings_fmt['kWh']:,.0f} kWh ({gas_pct:.1f}%)")

    total_savings = baseline_total - improved_total
    total_savings_fmt = format_energy(total_savings)
    total_pct = (total_savings / baseline_total) * 100

    print(f"\n   🎯 TOTAL SITE ENERGY SAVINGS: {total_savings_fmt['kWh']:,.0f} kWh ({total_pct:.1f}%)")
    print(f"      = {total_savings_fmt['GJ']:.2f} GJ/year")
    print(f"      = {total_savings_fmt['MWh']:.1f} MWh/year")

    # Cost savings (example rates)
    elec_rate = 0.12  # $/kWh
    gas_rate = 0.035  # $/kWh equivalent

    elec_cost_savings = elec_savings_fmt['kWh'] * elec_rate
    gas_cost_savings = gas_savings_fmt['kWh'] * gas_rate
    total_cost_savings = elec_cost_savings + gas_cost_savings

    print(f"\n💵 ESTIMATED ANNUAL COST SAVINGS:")
    print(f"   (Assuming electricity @ ${elec_rate}/kWh, gas @ ${gas_rate}/kWh)")
    print(f"   Electricity: ${elec_cost_savings:,.0f}/year")
    print(f"   Natural Gas: ${gas_cost_savings:,.0f}/year")
    print(f"   TOTAL: ${total_cost_savings:,.0f}/year")

    print(f"\n" + "="*80)
    print("✅ COMPARISON COMPLETE!")
    print("="*80 + "\n")

    # Show what this demonstrates
    print("📝 What This Demonstrates:")
    print("   - Ran two EnergyPlus simulations with different HVAC configurations")
    print("   - Baseline: Standard building with typical duct leakage")
    print("   - Improved: Same building with better duct sealing (5% leak vs baseline)")
    print("   - Quantified energy and cost savings from the improvement")
    print("\n   This is the foundation for FMU co-simulation where you can:")
    print("   - Export each model as an FMU")
    print("   - Co-simulate with control systems, renewable energy, or other tools")
    print("   - Test 'what-if' scenarios in real-time")
    print()

if __name__ == "__main__":
    baseline_dir = Path("/workspace/energyplus-mcp-server/fmu_comparison_results/baseline_90.1")
    improved_dir = Path("/workspace/energyplus-mcp-server/fmu_comparison_results/improved_sealed_ducts")

    compare_results(baseline_dir, improved_dir)
