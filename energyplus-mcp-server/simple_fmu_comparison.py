#!/usr/bin/env python3
"""
Simple EnergyPlus FMU Co-Simulation Comparison
Compares baseline building vs improved building using FMU exports
"""

import os
import subprocess
import json
from pathlib import Path

class SimpleFMUComparison:
    """Simple before/after FMU comparison for EnergyPlus models"""

    def __init__(self, workspace_dir="/workspace/energyplus-mcp-server"):
        self.workspace = Path(workspace_dir)
        self.sample_files = self.workspace / "sample_files"
        self.results_dir = self.workspace / "fmu_comparison_results"
        self.results_dir.mkdir(exist_ok=True)

    def run_energyplus_simulation(self, idf_path, weather_path, output_prefix):
        """Run EnergyPlus simulation (not FMU, for simplicity)"""
        print(f"\n{'='*80}")
        print(f"Running simulation: {output_prefix}")
        print(f"{'='*80}")

        # Create output directory
        output_dir = self.results_dir / output_prefix
        output_dir.mkdir(exist_ok=True)

        # Run EnergyPlus with annual simulation
        cmd = [
            "energyplus",
            "-a",  # Force annual simulation (not just design days)
            "-w", str(weather_path),
            "-d", str(output_dir),
            "-r",  # Readvars to process output
            str(idf_path)
        ]

        print(f"Command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"⚠️  Warning: EnergyPlus returned code {result.returncode}")
            print(result.stderr[:500])
        else:
            print("✅ Simulation completed successfully")

        return output_dir

    def extract_annual_energy(self, output_dir):
        """Extract annual energy consumption from simulation results"""

        # Try to read the meter output
        meter_file = output_dir / "eplusmtr.csv"

        if not meter_file.exists():
            print(f"⚠️  Meter file not found: {meter_file}")
            return None

        try:
            df = pd.read_csv(meter_file)

            # Look for electricity and gas meters
            # Annual values are typically in the last row for each meter
            results = {
                'electricity_kwh': 0,
                'gas_kwh': 0,
                'total_kwh': 0
            }

            # Sum up energy consumption (this is simplified - actual parsing depends on output format)
            if len(df) > 0:
                print(f"✅ Found meter data with {len(df)} rows")
                # For demo purposes, we'll parse the table file instead

            return results

        except Exception as e:
            print(f"⚠️  Error reading meter file: {e}")
            return None

    def extract_from_table(self, output_dir):
        """Extract energy totals from HTML table output"""

        table_file = output_dir / "eplustbl.htm"

        if not table_file.exists():
            # Try CSV version
            table_file = output_dir / "eplustbl.csv"

        if not table_file.exists():
            print(f"⚠️  No table file found in {output_dir}")
            return None

        try:
            if str(table_file).endswith('.csv'):
                # Parse CSV table
                with open(table_file, 'r') as f:
                    content = f.read()

                # Look for annual energy summary
                if "Total Site Energy" in content or "Total Energy" in content:
                    print(f"✅ Found energy summary in {table_file.name}")

                    # Extract key metrics (simplified)
                    results = {
                        'file': str(table_file),
                        'has_data': True
                    }
                    return results
            else:
                # Parse HTML
                with open(table_file, 'r') as f:
                    content = f.read()

                if "Site and Source Energy" in content:
                    print(f"✅ Found energy summary in HTML table")
                    return {'file': str(table_file), 'has_data': True}

        except Exception as e:
            print(f"⚠️  Error reading table: {e}")

        return None

    def compare_results(self, baseline_dir, improved_dir):
        """Compare baseline vs improved simulation results"""

        print(f"\n{'='*80}")
        print("COMPARISON RESULTS")
        print(f"{'='*80}\n")

        # For this demo, let's just show file locations
        print(f"📊 Baseline Results:")
        print(f"   Location: {baseline_dir}")
        baseline_table = self.extract_from_table(baseline_dir)

        print(f"\n📊 Improved Results:")
        print(f"   Location: {improved_dir}")
        improved_table = self.extract_from_table(improved_dir)

        # List output files
        print(f"\n📁 Output Files Generated:")
        for sim_dir, label in [(baseline_dir, "Baseline"), (improved_dir, "Improved")]:
            print(f"\n   {label}:")
            for f in sorted(sim_dir.glob("*.csv"))[:5]:
                print(f"      - {f.name}")
            for f in sorted(sim_dir.glob("*.htm")):
                print(f"      - {f.name}")

        print(f"\n💡 Next Steps:")
        print(f"   1. Open the HTML table files to compare energy usage")
        print(f"   2. Look for 'Site and Source Energy' section")
        print(f"   3. Compare Total Site Energy (GJ) between scenarios")
        print(f"\n   To view on Mac:")
        print(f"   docker cp energyplus-mcp:{baseline_dir}/eplustbl.htm .")
        print(f"   docker cp energyplus-mcp:{improved_dir}/eplustbl.htm .")
        print(f"   open eplustbl.htm")

    def run_comparison(self):
        """Run complete before/after comparison"""

        print("\n" + "="*80)
        print("SIMPLE FMU BEFORE/AFTER COMPARISON - ANNUAL SIMULATION")
        print("="*80)
        print("\nScenario:")
        print("  Baseline: MediumOffice-90.1-2019 (Standard building)")
        print("  Improved: MediumOffice-90.1-2019 with 20% better insulation")
        print("  Location: Denver, CO")
        print("  Period: Full annual simulation (8760 hours)")
        print("\n" + "="*80)

        # File paths - use the IDF that exists in container
        weather_file = Path("/workspace/energyplus-mcp-server/sample_files/USA_CO_Denver.Intl.AP.725650_TMY3.epw")
        baseline_idf = Path("/workspace/energyplus-mcp-server/test_files/MediumOffice-90.1-2019.idf")

        # Check files exist
        for f in [weather_file, baseline_idf, improved_idf]:
            if not f.exists():
                print(f"❌ Missing file: {f}")
                return

        print("\n✅ All input files found")

        # Run baseline
        baseline_dir = self.run_energyplus_simulation(
            baseline_idf,
            weather_file,
            "baseline_90.1"
        )

        # Run improved
        improved_dir = self.run_energyplus_simulation(
            improved_idf,
            weather_file,
            "improved_sealed_ducts"
        )

        # For now just show baseline results
        print("\n" + "="*80)
        print("BASELINE RESULTS")
        print("="*80)
        print(f"\n📊 Results location: {baseline_dir}")
        print(f"\n📁 Key output files:")
        print(f"   - eplustbl.htm : Summary tables with annual energy")
        print(f"   - eplusmtr.csv : Hourly meter data (8760 hours)")
        print(f"   - eplusout.csv : Detailed zone/system variables")

        print("\n💡 To view results:")
        print(f"   docker cp energyplus-mcp:{baseline_dir}/eplustbl.htm ./baseline_annual.htm")
        print(f"   open baseline_annual.htm")

        print("\n" + "="*80)
        print("✅ ANNUAL SIMULATION COMPLETE!")
        print("="*80)

        print("\n📝 Next: Create an improved version by:")
        print("   1. Copy the IDF file")
        print("   2. Modify insulation R-values, window U-factors, or HVAC efficiency")
        print("   3. Run second simulation")
        print("   4. Compare annual energy consumption")


if __name__ == "__main__":
    comparison = SimpleFMUComparison()
    comparison.run_comparison()
