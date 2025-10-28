#!/usr/bin/env python3
"""
Lighting Retrofit Analysis
Compare baseline (T8 fluorescent) vs LED retrofit
Calculate energy savings, cost savings, and payback period
"""

import subprocess
import shutil
from pathlib import Path
import re

def create_baseline_model():
    """Create baseline model with T8 fluorescent lighting"""

    print("\n" + "="*80)
    print("CREATING BASELINE MODEL - T8 FLUORESCENT LIGHTING")
    print("="*80 + "\n")

    work_dir = Path("/workspace/energyplus-mcp-server/lighting_retrofit")
    work_dir.mkdir(exist_ok=True)

    # Use a simple office building example
    source_idf = Path("/app/software/EnergyPlusV25-1-0/ExampleFiles/RefBldgSmallOfficeNew2004_Chicago.idf")
    baseline_idf = work_dir / "SmallOffice_Baseline.idf"

    if not source_idf.exists():
        # Try alternative
        source_idf = Path("/app/software/EnergyPlusV25-1-0/ExampleFiles/5ZoneAirCooled.idf")

    shutil.copy(source_idf, baseline_idf)

    print(f"✅ Baseline model created: {baseline_idf.name}")
    print(f"   Building: Small Office")
    print(f"   Lighting: T8 Fluorescent (baseline)")
    print(f"   Power Density: ~10.76 W/m² (typical for 2004 code)")

    return baseline_idf

def create_led_retrofit_model(baseline_idf):
    """Create LED retrofit version with reduced lighting power"""

    print("\n" + "="*80)
    print("CREATING LED RETROFIT MODEL")
    print("="*80 + "\n")

    retrofit_idf = baseline_idf.parent / "SmallOffice_LED.idf"

    # Read baseline IDF
    with open(baseline_idf, 'r') as f:
        content = f.read()

    # Find and reduce lighting power density by 50% (typical LED savings)
    # Look for Lights objects and reduce watts per zone floor area

    print("🔧 Modifying lighting power density...")
    print("   T8 Fluorescent → LED")
    print("   Typical savings: 50% lighting power reduction\n")

    # Pattern to find Lights objects with Watts/Area
    # This is a simplified approach - reduces all lighting power by 50%
    modified_content = content

    # Find Lights objects and modify
    lights_pattern = r'(Lights,\s*[^;]+?Watts/Area[^;]+?)(\d+\.?\d*)'

    def reduce_lighting(match):
        """Reduce lighting power by 50%"""
        prefix = match.group(1)
        value = float(match.group(2))
        new_value = value * 0.5  # 50% reduction with LEDs
        print(f"   Found: {value:.2f} W/m² → {new_value:.2f} W/m²")
        return f"{prefix}{new_value:.2f}"

    modified_content = re.sub(lights_pattern, reduce_lighting, modified_content, flags=re.IGNORECASE)

    # Write retrofit model
    with open(retrofit_idf, 'w') as f:
        f.write(modified_content)

    print(f"\n✅ LED retrofit model created: {retrofit_idf.name}")

    return retrofit_idf

def run_annual_simulation(idf_file, output_name):
    """Run annual EnergyPlus simulation"""

    print(f"\n{'='*80}")
    print(f"RUNNING ANNUAL SIMULATION: {output_name}")
    print(f"{'='*80}\n")

    weather_file = Path("/app/software/EnergyPlusV25-1-0/WeatherData/USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")
    output_dir = idf_file.parent / output_name
    output_dir.mkdir(exist_ok=True)

    print(f"📋 Configuration:")
    print(f"   Model: {idf_file.name}")
    print(f"   Weather: Chicago, IL")
    print(f"   Period: Full year (8760 hours)")
    print(f"\n⏳ Running simulation (2-3 minutes)...\n")

    # Run EnergyPlus
    cmd = [
        "energyplus",
        "--annual",
        "-w", str(weather_file),
        "-d", str(output_dir),
        str(idf_file)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"⚠️  Warning: returned code {result.returncode}")
    else:
        print(f"✅ Simulation completed!")

    return output_dir

def extract_energy_results(output_dir):
    """Extract annual energy consumption from results"""

    table_file = output_dir / "eplustbl.htm"

    if not table_file.exists():
        print(f"❌ Results file not found: {table_file}")
        return None

    with open(table_file, 'r') as f:
        content = f.read()

    results = {}

    # Extract total site energy (GJ)
    match = re.search(r'Total Site Energy.*?<td[^>]*>\s*([\d.]+)', content, re.IGNORECASE | re.DOTALL)
    if match:
        results['total_site_energy_gj'] = float(match.group(1))
        results['total_site_energy_kwh'] = results['total_site_energy_gj'] * 277.778  # GJ to kWh

    # Extract lighting energy specifically
    match = re.search(r'Interior Lighting.*?<td[^>]*>\s*([\d.]+)', content, re.IGNORECASE | re.DOTALL)
    if match:
        results['lighting_energy_gj'] = float(match.group(1))
        results['lighting_energy_kwh'] = results['lighting_energy_gj'] * 277.778

    # Extract electricity
    match = re.search(r'Electricity.*?Total Energy.*?<td[^>]*>\s*([\d.]+)', content, re.IGNORECASE | re.DOTALL)
    if match:
        results['electricity_gj'] = float(match.group(1))
        results['electricity_kwh'] = results['electricity_gj'] * 277.778

    return results

def calculate_retrofit_economics(baseline_results, led_results):
    """Calculate ROI, payback period, and cost savings"""

    print("\n" + "="*80)
    print("LIGHTING RETROFIT ECONOMIC ANALYSIS")
    print("="*80 + "\n")

    # Extract values
    baseline_lighting_kwh = baseline_results.get('lighting_energy_kwh', 0)
    led_lighting_kwh = led_results.get('lighting_energy_kwh', 0)

    baseline_total_kwh = baseline_results.get('total_site_energy_kwh', 0)
    led_total_kwh = led_results.get('total_site_energy_kwh', 0)

    # Calculate savings
    lighting_savings_kwh = baseline_lighting_kwh - led_lighting_kwh
    lighting_savings_pct = (lighting_savings_kwh / baseline_lighting_kwh * 100) if baseline_lighting_kwh > 0 else 0

    total_savings_kwh = baseline_total_kwh - led_total_kwh
    total_savings_pct = (total_savings_kwh / baseline_total_kwh * 100) if baseline_total_kwh > 0 else 0

    # Economic parameters
    electricity_rate = 0.12  # $/kWh
    annual_cost_savings = total_savings_kwh * electricity_rate

    # Estimate retrofit cost (typical: $2-4 per square foot)
    # Assume small office ~500 m² = ~5,400 sq ft
    building_area_sqft = 5400
    retrofit_cost_per_sqft = 3.0  # mid-range estimate
    total_retrofit_cost = building_area_sqft * retrofit_cost_per_sqft

    # Calculate payback
    simple_payback_years = total_retrofit_cost / annual_cost_savings if annual_cost_savings > 0 else float('inf')

    # 10-year NPV (assuming 5% discount rate)
    discount_rate = 0.05
    npv = sum([annual_cost_savings / ((1 + discount_rate) ** year) for year in range(1, 11)]) - total_retrofit_cost

    # Print results
    print(f"📊 ENERGY SAVINGS\n")
    print(f"   Lighting Energy:")
    print(f"      Baseline (T8):  {baseline_lighting_kwh:>10,.0f} kWh/year")
    print(f"      LED Retrofit:   {led_lighting_kwh:>10,.0f} kWh/year")
    print(f"      Savings:        {lighting_savings_kwh:>10,.0f} kWh/year ({lighting_savings_pct:.1f}%)")

    print(f"\n   Total Building Energy:")
    print(f"      Baseline:       {baseline_total_kwh:>10,.0f} kWh/year")
    print(f"      LED Retrofit:   {led_total_kwh:>10,.0f} kWh/year")
    print(f"      Savings:        {total_savings_kwh:>10,.0f} kWh/year ({total_savings_pct:.1f}%)")

    print(f"\n💰 FINANCIAL ANALYSIS\n")
    print(f"   Annual Cost Savings:    ${annual_cost_savings:>10,.0f} /year")
    print(f"   (@ ${electricity_rate}/kWh)")

    print(f"\n   Retrofit Investment:")
    print(f"      Building area:       {building_area_sqft:>10,} sq ft")
    print(f"      Cost:                ${retrofit_cost_per_sqft:>10.2f} /sq ft")
    print(f"      Total cost:          ${total_retrofit_cost:>10,.0f}")

    print(f"\n   Return on Investment:")
    print(f"      Simple Payback:      {simple_payback_years:>10.1f} years")
    print(f"      10-Year NPV:         ${npv:>10,.0f}")
    print(f"      10-Year Savings:     ${annual_cost_savings * 10:>10,.0f}")

    # ROI assessment
    print(f"\n✅ RECOMMENDATION:")
    if simple_payback_years < 3:
        print(f"   🌟 EXCELLENT PROJECT - Payback < 3 years")
    elif simple_payback_years < 5:
        print(f"   ✅ GOOD PROJECT - Payback < 5 years")
    elif simple_payback_years < 7:
        print(f"   👍 ACCEPTABLE PROJECT - Payback < 7 years")
    else:
        print(f"   ⚠️  MARGINAL PROJECT - Long payback period")

    if npv > 0:
        print(f"   💰 POSITIVE NPV - Project adds value")

    # Additional benefits
    print(f"\n💡 ADDITIONAL BENEFITS (Not Monetized):")
    print(f"   - Reduced cooling load (less heat from lighting)")
    print(f"   - Longer lamp life (LED: 50,000 hrs vs T8: 20,000 hrs)")
    print(f"   - Lower maintenance costs (fewer replacements)")
    print(f"   - Better light quality")
    print(f"   - Sustainability / carbon reduction")

    return {
        'lighting_savings_kwh': lighting_savings_kwh,
        'total_savings_kwh': total_savings_kwh,
        'annual_cost_savings': annual_cost_savings,
        'retrofit_cost': total_retrofit_cost,
        'payback_years': simple_payback_years,
        'npv': npv
    }

def main():
    """Main execution"""

    print("\n" + "="*80)
    print("LIGHTING RETROFIT ANALYSIS - T8 FLUORESCENT → LED")
    print("Small Office Building, Chicago IL")
    print("="*80)

    # Step 1: Create models
    baseline_idf = create_baseline_model()
    led_idf = create_led_retrofit_model(baseline_idf)

    # Step 2: Run simulations
    print("\n" + "="*80)
    print("RUNNING ANNUAL SIMULATIONS")
    print("="*80)

    baseline_output = run_annual_simulation(baseline_idf, "baseline_results")
    led_output = run_annual_simulation(led_idf, "led_results")

    # Step 3: Extract results
    print("\n" + "="*80)
    print("EXTRACTING RESULTS")
    print("="*80 + "\n")

    baseline_results = extract_energy_results(baseline_output)
    led_results = extract_energy_results(led_output)

    if not baseline_results or not led_results:
        print("❌ Could not extract results from simulations")
        return

    print("✅ Results extracted successfully")

    # Step 4: Economic analysis
    economics = calculate_retrofit_economics(baseline_results, led_results)

    # Summary
    print("\n" + "="*80)
    print("✅ LIGHTING RETROFIT ANALYSIS COMPLETE!")
    print("="*80 + "\n")

    print(f"📁 Output Files:")
    print(f"   Baseline: {baseline_output}/eplustbl.htm")
    print(f"   LED:      {led_output}/eplustbl.htm")

    print(f"\n💻 View detailed results:")
    print(f"   docker cp energyplus-mcp:{baseline_output}/eplustbl.htm ./baseline_lighting.htm")
    print(f"   docker cp energyplus-mcp:{led_output}/eplustbl.htm ./led_lighting.htm")
    print(f"   open baseline_lighting.htm")
    print(f"   open led_lighting.htm")

    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
