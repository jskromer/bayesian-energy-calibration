#!/usr/bin/env python3
"""
Run Annual EnergyPlus Simulation
Simple script to run a full-year building energy simulation
"""

import subprocess
from pathlib import Path

def run_annual_simulation():
    """Run one annual EnergyPlus simulation"""

    print("\n" + "="*80)
    print("ENERGYPLUS ANNUAL SIMULATION")
    print("="*80)

    # File paths
    idf_file = Path("/workspace/energyplus-mcp-server/test_files/MediumOffice-90.1-2019.idf")
    weather_file = Path("/workspace/energyplus-mcp-server/sample_files/USA_CO_Denver.Intl.AP.725650_TMY3.epw")
    output_dir = Path("/workspace/energyplus-mcp-server/annual_results")

    print(f"\n📋 Configuration:")
    print(f"   Model: {idf_file.name}")
    print(f"   Weather: Denver, CO")
    print(f"   Period: Full year (8760 hours)")
    print(f"   Output: {output_dir}")

    # Check if files exist
    if not idf_file.exists():
        print(f"\n❌ IDF file not found: {idf_file}")
        return False

    if not weather_file.exists():
        print(f"\n❌ Weather file not found: {weather_file}")
        print(f"\n💡 Download weather file:")
        print(f"   cd /workspace/energyplus-mcp-server/sample_files")
        print(f"   curl -o USA_CO_Denver.Intl.AP.725650_TMY3.epw \\")
        print(f"     'https://energyplus-weather.s3.amazonaws.com/north_and_central_america_wmo_region_4/USA/CO/USA_CO_Denver-Centennial-Golden-Nr.Ann.Arbor_TMY3/USA_CO_Denver-Centennial-Golden-Nr.Ann.Arbor_TMY3.epw'")
        return False

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    print(f"\n✅ All files found. Starting simulation...")
    print(f"\n⏳ Running EnergyPlus (this will take 2-5 minutes for annual simulation)...\n")

    # Run EnergyPlus with annual flag
    cmd = [
        "energyplus",
        "-a",  # FORCE ANNUAL SIMULATION (not design days)
        "-w", str(weather_file),
        "-d", str(output_dir),
        "-r",  # Run readvars
        str(idf_file)
    ]

    print(f"Command: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"⚠️  EnergyPlus returned code {result.returncode}")
        print(f"\nStderr output:")
        print(result.stderr[:1000])
        return False

    print("✅ Simulation completed successfully!")

    # Check for output files
    print(f"\n📁 Output Files Generated:")
    for pattern in ["*.htm", "*.csv"]:
        files = list(output_dir.glob(pattern))
        for f in sorted(files)[:10]:
            size_mb = f.stat().st_size / 1024 / 1024
            print(f"   {f.name:30s} ({size_mb:.2f} MB)")

    # Check the meter file for annual data
    meter_file = output_dir / "eplusmtr.csv"
    if meter_file.exists():
        with open(meter_file, 'r') as f:
            lines = f.readlines()

        print(f"\n📊 Simulation Details:")
        print(f"   Timesteps: {len(lines) - 1:,} (should be ~8760 for hourly annual)")

        # Parse annual totals from last line
        if len(lines) > 1:
            header = lines[0].strip().split(',')
            last_line = lines[-1].strip().split(',')

            print(f"\n💡 Annual Energy Summary:")

            # Find electricity and gas
            for i, col in enumerate(header):
                if 'Electricity:Facility [J](Monthly)' in col and i < len(last_line):
                    try:
                        elec_j = float(last_line[i])
                        elec_kwh = elec_j / 3_600_000
                        elec_gj = elec_j / 1_000_000_000
                        print(f"   Electricity: {elec_kwh:,.0f} kWh ({elec_gj:.1f} GJ)")
                    except:
                        pass

                if 'NaturalGas:Facility [J](Monthly)' in col and i < len(last_line):
                    try:
                        gas_j = float(last_line[i])
                        gas_kwh = gas_j / 3_600_000
                        gas_gj = gas_j / 1_000_000_000
                        print(f"   Natural Gas: {gas_kwh:,.0f} kWh ({gas_gj:.1f} GJ)")
                    except:
                        pass

    print(f"\n💻 To view detailed results:")
    print(f"   docker cp energyplus-mcp:{output_dir}/eplustbl.htm ./annual_results.htm")
    print(f"   open annual_results.htm")

    print("\n" + "="*80)
    print("✅ DONE!")
    print("="*80 + "\n")

    return True

if __name__ == "__main__":
    run_annual_simulation()
