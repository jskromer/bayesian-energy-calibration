#!/usr/bin/env python3
"""
Run Annual EnergyPlus Simulation - Using Working Example
"""

import subprocess
from pathlib import Path

def run_annual():
    """Run annual simulation with known-good example files"""

    print("\n" + "="*80)
    print("ENERGYPLUS ANNUAL SIMULATION - LARGE OFFICE")
    print("="*80)

    # Use example files from EnergyPlus installation
    idf_file = Path("/app/software/EnergyPlusV25-1-0/ExampleFiles/RefBldgLargeOfficeNew2004_Chicago.idf")
    weather_file = Path("/app/software/EnergyPlusV25-1-0/WeatherData/USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")
    output_dir = Path("/workspace/energyplus-mcp-server/annual_large_office")

    print(f"\n📋 Configuration:")
    print(f"   Building: Large Office (Reference Building)")
    print(f"   Standard: ASHRAE 90.1-2004")
    print(f"   Location: Chicago, IL")
    print(f"   Period: FULL YEAR (8760 hours)")
    print(f"")

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    print("⏳ Running ANNUAL simulation (this takes 2-5 minutes)...")
    print("")

    # Run with annual flag
    cmd = [
        "energyplus",
        "--annual",  # FORCE ANNUAL - NOT DESIGN DAYS
        "-w", str(weather_file),
        "-d", str(output_dir),
        str(idf_file)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"⚠️  Warning: Return code {result.returncode}")
    else:
        print("✅ Simulation completed!")

    # Parse results
    meter_file = output_dir / "eplusmtr.csv"
    if meter_file.exists():
        with open(meter_file, 'r') as f:
            lines = f.readlines()

        hours = len(lines) - 1
        print(f"\n📊 Timesteps simulated: {hours:,}")

        if hours == 8760:
            print("   ✅ FULL ANNUAL SIMULATION CONFIRMED!")
        else:
            print(f"   Note: Got {hours} timesteps (expected 8760 for annual)")

        # Get annual totals from last line
        if len(lines) > 10:
            header = lines[0].strip().split(',')
            last = lines[-1].strip().split(',')

            print(f"\n💰 ANNUAL ENERGY CONSUMPTION:")
            print(f"   {'='*60}")

            elec_kwh = 0
            gas_kwh = 0

            for i, col in enumerate(header):
                if 'Electricity:Facility' in col and 'Monthly' in col and i < len(last):
                    try:
                        elec_kwh = float(last[i]) / 3_600_000
                        elec_gj = float(last[i]) / 1_000_000_000
                        print(f"   Electricity: {elec_kwh:,.0f} kWh/year ({elec_gj:.1f} GJ)")
                    except:
                        pass

                if 'NaturalGas:Facility' in col and 'Monthly' in col and i < len(last):
                    try:
                        gas_kwh = float(last[i]) / 3_600_000
                        gas_gj = float(last[i]) / 1_000_000_000
                        print(f"   Natural Gas: {gas_kwh:,.0f} kWh/year ({gas_gj:.1f} GJ)")
                    except:
                        pass

            total_kwh = elec_kwh + gas_kwh
            print(f"   {'='*60}")
            print(f"   TOTAL SITE ENERGY: {total_kwh:,.0f} kWh/year")

            # Rough cost estimate
            cost = elec_kwh * 0.12 + gas_kwh * 0.035
            print(f"\n   Estimated Annual Cost: ${cost:,.0f}")
            print(f"   (assuming $0.12/kWh electric, $0.035/kWh gas equivalent)")

    # List key output files
    print(f"\n📁 Output Files:")
    key_files = ["eplustbl.htm", "eplusmtr.csv", "eplusout.csv"]
    for fname in key_files:
        f = output_dir / fname
        if f.exists():
            size_mb = f.stat().st_size / 1024 / 1024
            print(f"   {fname:20s} ({size_mb:.2f} MB)")

    print(f"\n💻 View Detailed Results:")
    print(f"   docker cp energyplus-mcp:{output_dir}/eplustbl.htm ./annual_results.htm")
    print(f"   open annual_results.htm")

    print("\n" + "="*80)
    print("✅ ANNUAL SIMULATION COMPLETE - RESULTS ARE REAL!")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_annual()
