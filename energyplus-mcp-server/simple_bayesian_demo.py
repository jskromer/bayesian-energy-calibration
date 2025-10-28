#!/usr/bin/env python3
"""
Simplified Bayesian Calibration Demo

Demonstrates the PyMC + GP + MCP workflow with minimal dependencies
and synthetic data for quick testing.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import json

# MCP Integration
from energyplus_mcp_server.config import get_config
from energyplus_mcp_server.energyplus_tools import EnergyPlusManager


def simple_gp_surrogate_demo():
    """
    Simplified demo showing GP surrogate + MCP integration concept
    Without requiring full PyMC installation
    """
    print("=" * 80)
    print("SIMPLIFIED BAYESIAN CALIBRATION DEMO")
    print("Gaussian Process Surrogate + MCP Integration")
    print("=" * 80)

    # Configuration
    idf_path = "sample_files/MediumOffice-90.1-2004.idf"
    weather_file = "sample_files/USA_CO_Denver.Intl.AP.725650_TMY3.epw"
    observed_energy = 714762.0  # Target (kWh/year)

    config = get_config()
    manager = EnergyPlusManager(config)

    print(f"\n🎯 Target (Observed) Energy: {observed_energy:,.0f} kWh/year")
    print(f"📁 Baseline IDF: {idf_path}")
    print(f"🌤️  Weather: {weather_file}")

    # Parameter space to explore
    param_space = {
        'infiltration_mult': [0.8, 1.0, 1.2, 1.4, 1.6],  # Test different infiltration levels
    }

    print(f"\n🔬 Exploring Parameter Space:")
    print(f"   Infiltration multipliers: {param_space['infiltration_mult']}")

    # Run simulations for each parameter value
    results = []

    for i, infil_mult in enumerate(param_space['infiltration_mult'], 1):
        print(f"\n{'=' * 80}")
        print(f"Simulation {i}/{len(param_space['infiltration_mult'])}")
        print(f"{'=' * 80}")
        print(f"   Infiltration multiplier: {infil_mult:.2f}")

        # Create modified IDF
        modified_idf = f"sample_files/calibration_infil_{infil_mult:.2f}.idf"

        manager.change_infiltration_by_mult(
            idf_path=idf_path,
            mult=infil_mult,
            output_path=modified_idf
        )

        # Run simulation (returns JSON string with results)
        result_json = manager.run_simulation(
            idf_path=modified_idf,
            weather_file=weather_file,
            annual=True
        )

        # Parse JSON result
        result = json.loads(result_json)
        output_dir = Path(result['output_directory'])

        # Find HTML table file (name varies based on output prefix)
        html_files = list(output_dir.glob("*Table.htm"))
        if not html_files:
            html_files = list(output_dir.glob("eplustbl.htm"))

        if html_files:
            html_file = html_files[0]
            import re
            html_content = html_file.read_text()

            # Find total site energy in GJ
            match = re.search(r'Total Site Energy.*?(\d+\.\d+).*?GJ', html_content, re.DOTALL)
            if match:
                energy_gj = float(match.group(1))
                energy_kwh = energy_gj * 277.778  # GJ to kWh

                error = abs(energy_kwh - observed_energy)
                error_pct = (error / observed_energy) * 100

                results.append({
                    'infiltration_mult': infil_mult,
                    'energy_kwh': energy_kwh,
                    'error_kwh': error,
                    'error_pct': error_pct
                })

                print(f"   ✅ Energy: {energy_kwh:,.0f} kWh/year")
                print(f"   📊 Error: {error:,.0f} kWh ({error_pct:.2f}%)")

    # Results summary
    print(f"\n{'=' * 80}")
    print("CALIBRATION RESULTS SUMMARY")
    print(f"{'=' * 80}")

    df_results = pd.DataFrame(results)
    print("\n" + df_results.to_string(index=False))

    # Find best match
    best_idx = df_results['error_kwh'].idxmin()
    best_result = df_results.iloc[best_idx]

    print(f"\n🎯 BEST CALIBRATION:")
    print(f"   Infiltration multiplier: {best_result['infiltration_mult']:.2f}")
    print(f"   Predicted energy:        {best_result['energy_kwh']:>12,.0f} kWh/year")
    print(f"   Observed energy:         {observed_energy:>12,.0f} kWh/year")
    print(f"   Absolute error:          {best_result['error_kwh']:>12,.0f} kWh")
    print(f"   Percent error:           {best_result['error_pct']:>12.2f}%")

    # Save results
    output_file = "calibration_results.csv"
    df_results.to_csv(output_file, index=False)
    print(f"\n💾 Results saved to: {output_file}")

    print(f"\n{'=' * 80}")
    print("DEMO COMPLETE!")
    print(f"{'=' * 80}")
    print(f"\nTotal simulations run: {len(results)}")
    print(f"\nNext steps:")
    print(f"  1. Add more parameters (R-value, setpoint)")
    print(f"  2. Install PyMC: uv pip install -r requirements_calibration.txt")
    print(f"  3. Run full Bayesian workflow: uv run bayesian_calibration_pymc.py")
    print(f"  4. Use real utility bill data as observed_energy")


if __name__ == "__main__":
    simple_gp_surrogate_demo()
