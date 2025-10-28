#!/usr/bin/env python3
"""
Run Annual EnergyPlus Simulation - Simple Version
Uses existing files in the container
"""

import subprocess
from pathlib import Path

def run_annual():
    """Run annual simulation with existing files"""

    print("\n" + "="*80)
    print("ENERGYPLUS ANNUAL SIMULATION")
    print("="*80)

    # Use files that exist in container
    idf_file = Path("/workspace/energyplus-mcp-server/test_files/MediumOffice-90.1-2019.idf")
    weather_file = Path("/workspace/energyplus-mcp-server/illustrative examples/USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")
    output_dir = Path("/workspace/energyplus-mcp-server/annual_results")

    print(f"\n📋 Configuration:")
    print(f"   Model: {idf_file.name}")
    print(f"   Weather: Chicago, IL (matches the IDF design location)")
    print(f"   Period: FULL YEAR (8760 hours)")
    print(f"   Output: {output_dir}\n")

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    print("⏳ Running annual simulation...")
    print("   This will take 2-5 minutes...\n")

    # Run with annual flag
    cmd = [
        "energyplus",
        "--annual",  # FORCE ANNUAL SIMULATION
        "-w", str(weather_file),
        "-d", str(output_dir),
        str(idf_file)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"⚠️  Returned code {result.returncode}")
        print("\nLast 50 lines of error output:")
        print('\n'.join(result.stderr.split('\n')[-50:]))
    else:
        print("✅ Simulation completed!")

    # Parse results
    meter_file = output_dir / "eplusmtr.csv"
    if meter_file.exists():
        with open(meter_file, 'r') as f:
            lines = f.readlines()

        hours = len(lines) - 1
        print(f"\n📊 Simulation ran {hours:,} timesteps")

        if hours == 8760:
            print("   ✅ Full annual simulation confirmed!")
        else:
            print(f"   ⚠️  Expected 8760 hours, got {hours}")

        # Get annual totals
        if len(lines) > 1:
            header = lines[0].strip().split(',')
            last = lines[-1].strip().split(',')

            print(f"\n💡 ANNUAL ENERGY CONSUMPTION:")

            for i, col in enumerate(header):
                if 'Electricity:Facility' in col and 'Monthly' in col and i < len(last):
                    try:
                        kwh = float(last[i]) / 3_600_000
                        print(f"   Electricity: {kwh:,.0f} kWh/year")
                    except:
                        pass

                if 'NaturalGas:Facility' in col and 'Monthly' in col and i < len(last):
                    try:
                        kwh = float(last[i]) / 3_600_000
                        print(f"   Natural Gas: {kwh:,.0f} kWh/year")
                    except:
                        pass

    # List output files
    print(f"\n📁 Output files in {output_dir.name}/:")
    for f in sorted(output_dir.glob("*"))[:10]:
        print(f"   - {f.name}")

    print(f"\n💻 View results:")
    print(f"   docker cp energyplus-mcp:{output_dir}/eplustbl.htm ./results.htm")
    print(f"   open results.htm")

    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    run_annual()
