#!/usr/bin/env python3
"""
FMU Export and Co-Simulation - Using Working Example
Uses pre-configured IDF from EnergyPlusToFMU examples
"""

import subprocess
import os
import shutil
from pathlib import Path

def export_fmu_from_example():
    """Export FMU using pre-configured example IDF"""

    print("\n" + "="*80)
    print("STEP 1: EXPORT ENERGYPLUS MODEL AS FMU")
    print("="*80 + "\n")

    # Setup
    work_dir = Path("/workspace/energyplus-mcp-server/fmu_working")
    work_dir.mkdir(exist_ok=True)
    os.chdir(work_dir)

    # Use example IDF that's already configured for FMU export
    source_idf = Path("/workspace/EnergyPlusToFMU/Examples/Variable/_fmu-export-variable.idf")
    local_idf = work_dir / "Building.idf"
    shutil.copy(source_idf, local_idf)

    idd_file = Path("/app/software/EnergyPlusV25-1-0/Energy+.idd")
    weather_file = Path("/app/software/EnergyPlusV25-1-0/WeatherData/USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")

    print(f"📋 Configuration:")
    print(f"   Model: Pre-configured FMU export example")
    print(f"   Type: Building with external interface")
    print(f"   Weather: Chicago, IL")
    print(f"   FMI Version: 2.0\n")

    print(f"⏳ Exporting FMU (takes 2-4 minutes)...")
    print(f"   Compiling C code and packaging FMU...\n")

    # Export command
    cmd = [
        "python",
        "/workspace/EnergyPlusToFMU/Scripts/EnergyPlusToFMU.py",
        "-i", str(idd_file),
        "-w", str(weather_file),
        "-a", "2",
        str(local_idf)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Show output
    print(result.stdout)

    if result.returncode != 0:
        print(f"\n⚠️  Export returned code {result.returncode}")
        if "ERROR" in result.stdout or "ERROR" in result.stderr:
            print(f"\nError details:")
            print(result.stderr[-500:])
        return False

    # Check for FMU
    fmu_file = work_dir / "Building.fmu"

    if fmu_file.exists():
        size_mb = fmu_file.stat().st_size / 1024 / 1024
        print(f"\n✅ FMU CREATED SUCCESSFULLY!")
        print(f"   📦 File: {fmu_file.name}")
        print(f"   📊 Size: {size_mb:.2f} MB")
        return fmu_file
    else:
        print(f"\n❌ FMU file not found")
        print(f"Files created:")
        for f in sorted(work_dir.glob("*"))[:20]:
            print(f"   - {f.name}")
        return False

def simulate_fmu(fmu_file):
    """Run FMU co-simulation"""

    print("\n" + "="*80)
    print("STEP 2: CO-SIMULATE FMU")
    print("="*80 + "\n")

    try:
        from fmpy import simulate_fmu, read_model_description
        import numpy as np
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        return False

    print(f"📊 Reading FMU model description...")

    # Read model info
    model_desc = read_model_description(fmu_file)

    print(f"\n📋 FMU Information:")
    print(f"   Model: {model_desc.modelName}")
    print(f"   FMI Version: {model_desc.fmiVersion}")
    print(f"   Platform: {model_desc.defaultExperiment}")

    # List some variables
    print(f"\n   Variables (first 15):")
    for i, var in enumerate(list(model_desc.modelVariables)[:15]):
        print(f"      {i+1}. {var.name} [{var.causality}]")

    print(f"\n⏳ Running 2-day co-simulation...\n")

    # Run simulation
    try:
        result = simulate_fmu(
            str(fmu_file),
            start_time=0,
            stop_time=2 * 24 * 3600,  # 2 days in seconds
            step_size=900,  # 15 minutes
            output_interval=900,
            fmi_type='CoSimulation',
            debug_logging=False
        )

        print(f"✅ Co-simulation completed!")
        print(f"   Duration: 2 days")
        print(f"   Timestep: 15 minutes")
        print(f"   Data points: {len(result['time'])}\n")

        # Show available variables
        print(f"📊 Available output variables:")
        var_names = result.dtype.names
        for i, name in enumerate(var_names[:20]):
            print(f"   {i+1}. {name}")

        if len(var_names) > 20:
            print(f"   ... and {len(var_names) - 20} more")

        # Create visualization
        print(f"\n📈 Creating visualization...")

        fig, axes = plt.subplots(min(3, len(var_names)-1), 1, figsize=(12, 10))

        if not isinstance(axes, np.ndarray):
            axes = [axes]

        time_hours = result['time'] / 3600

        for i, ax in enumerate(axes):
            if i + 1 < len(var_names):
                var_name = var_names[i + 1]  # Skip 'time'
                ax.plot(time_hours, result[var_name], linewidth=1.5)
                ax.set_ylabel(var_name, fontsize=9)
                ax.grid(True, alpha=0.3)
                if i == len(axes) - 1:
                    ax.set_xlabel('Time (hours)', fontsize=10)

        plt.suptitle('FMU Co-Simulation Results', fontsize=14, fontweight='bold')
        plt.tight_layout()

        plot_file = work_dir / "fmu_cosimulation_results.png"
        plt.savefig(plot_file, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"   ✅ Plot saved: {plot_file.name}\n")

        return True

    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main execution"""

    print("\n" + "="*80)
    print("ENERGYPLUS FMU CO-SIMULATION - WORKING EXAMPLE")
    print("="*80)

    # Export FMU
    fmu_file = export_fmu_from_example()

    if not fmu_file:
        print("\n❌ FMU export failed")
        print("\n💡 The IDF file needs ExternalInterface objects for FMU export")
        print("   Using pre-configured example from EnergyPlusToFMU/Examples/")
        return

    # Simulate
    success = simulate_fmu(fmu_file)

    if success:
        print("\n" + "="*80)
        print("✅ FMU CO-SIMULATION COMPLETED SUCCESSFULLY!")
        print("="*80)

        print("\n🎉 What was accomplished:")
        print("   1. ✅ Exported EnergyPlus building as FMU")
        print("   2. ✅ Ran 2-day co-simulation using FMPy")
        print("   3. ✅ Visualized results")

        print("\n📁 Output Files:")
        print(f"   - FMU: fmu_working/Building.fmu")
        print(f"   - Plot: fmu_working/fmu_cosimulation_results.png")

        print("\n💡 What FMU co-simulation enables:")
        print("   - Portable building energy models")
        print("   - Couple with control systems in real-time")
        print("   - Integrate with MATLAB, Modelica, Python")
        print("   - Test HVAC strategies")
        print("   - Renewable energy integration")
        print("   - Grid interaction studies")

        print("\n🔄 Next steps:")
        print("   - Modify control inputs during simulation")
        print("   - Add custom thermostat logic")
        print("   - Connect multiple FMUs (building + solar + battery)")
        print("   - Export to other simulation platforms")

        print("\n💻 View results:")
        print(f"   docker cp energyplus-mcp:/workspace/energyplus-mcp-server/fmu_working/fmu_cosimulation_results.png .")
        print(f"   open fmu_cosimulation_results.png")

    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
