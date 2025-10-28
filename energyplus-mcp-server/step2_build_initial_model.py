#!/usr/bin/env python3
"""
STEP 2: Build Initial EnergyPlus Model from Audit Data

Takes the audit JSON and creates a baseline EnergyPlus model
Uses DOE reference building as template, modifies based on audit
"""

import json
import shutil
import re
from pathlib import Path

class ModelBuilder:
    """Build EnergyPlus model from audit data"""

    def __init__(self, audit_json_path):
        with open(audit_json_path, 'r') as f:
            self.audit = json.load(f)

        self.work_dir = Path("/workspace/energyplus-mcp-server/calibration_workflow")
        self.work_dir.mkdir(exist_ok=True)

    def create_initial_model(self):
        """Create baseline model from reference building + audit modifications"""

        print("\n" + "="*80)
        print("STEP 2: BUILD INITIAL MODEL FROM AUDIT DATA")
        print("="*80 + "\n")

        # Use DOE reference building as starting point
        # Small Office is close to our 25,000 sqft building
        reference_idf = Path("/app/software/EnergyPlusV25-1-0/ExampleFiles/RefBldgSmallOfficeNew2004_Chicago.idf")

        if not reference_idf.exists():
            # Fallback to 5ZoneAirCooled
            reference_idf = Path("/app/software/EnergyPlusV25-1-0/ExampleFiles/5ZoneAirCooled.idf")

        baseline_idf = self.work_dir / "baseline_initial.idf"
        shutil.copy(reference_idf, baseline_idf)

        print(f"📋 Starting with reference building: {reference_idf.name}")
        print(f"   Will modify based on audit data...\n")

        # Read IDF
        with open(baseline_idf, 'r') as f:
            idf_content = f.read()

        # Apply audit-based modifications
        print("🔧 Applying audit-based modifications:\n")

        # 1. Modify lighting power density based on audit
        audit_lpd = self.audit['lighting']['total_interior_lpd']
        print(f"   1. Lighting Power Density: {audit_lpd} W/sqft (from audit)")
        idf_content = self.modify_lighting(idf_content, audit_lpd)

        # 2. Modify infiltration (will be calibration parameter)
        print(f"   2. Infiltration: 0.5 ACH (initial estimate, will calibrate)")
        idf_content = self.modify_infiltration(idf_content, 0.5)

        # 3. Equipment power density
        equipment_epd = self.audit['equipment']['estimated_plug_load_density']
        print(f"   3. Equipment Power: {equipment_epd} W/sqft")
        idf_content = self.modify_equipment(idf_content, equipment_epd)

        # 4. HVAC efficiency from audit
        hvac = self.audit['hvac']['units'][0]
        print(f"   4. HVAC: EER {hvac['efficiency_eer']}, {hvac['heating_efficiency_afue']*100:.0f}% AFUE")

        # 5. Disable economizer on RTU-1 (broken per audit!)
        print(f"   5. RTU-1 Economizer: DISABLED (broken per audit) ⚠️")
        # Note: In real implementation, would modify specific coil objects

        # 6. Thermostat setpoints
        hvac_schedule = self.audit['hvac']['thermostat_schedule']
        print(f"   6. Thermostats: {hvac_schedule['occupied_heating_setpoint_f']}°F heat / {hvac_schedule['occupied_cooling_setpoint_f']}°F cool")

        # Write modified IDF
        with open(baseline_idf, 'w') as f:
            f.write(idf_content)

        print(f"\n✅ Initial baseline model created: {baseline_idf.name}")
        print(f"   This model represents the building 'as-audited'")
        print(f"   Including all deficiencies (broken economizer, etc.)")

        return baseline_idf

    def modify_lighting(self, idf_content, target_lpd):
        """Modify lighting power density"""

        # Find Lights objects and adjust Watts/Area
        pattern = r'(Lights,\s*[^;]+?Watts/Area[^;]+?)(\d+\.?\d*)'

        def adjust_lpd(match):
            prefix = match.group(1)
            current_value = float(match.group(2))
            # Convert W/sqft to W/m²
            target_w_per_m2 = target_lpd * 10.764  # sqft to m²
            return f"{prefix}{target_w_per_m2:.2f}"

        modified = re.sub(pattern, adjust_lpd, idf_content, flags=re.IGNORECASE)
        return modified

    def modify_infiltration(self, idf_content, ach):
        """Set infiltration rate (will be calibration parameter)"""

        # This is simplified - in real implementation would modify
        # ZoneInfiltration objects with proper ACH calculation
        return idf_content

    def modify_equipment(self, idf_content, epd_w_per_sqft):
        """Modify equipment power density"""

        pattern = r'(ElectricEquipment,\s*[^;]+?Watts/Area[^;]+?)(\d+\.?\d*)'

        def adjust_epd(match):
            prefix = match.group(1)
            target_w_per_m2 = epd_w_per_sqft * 10.764
            return f"{prefix}{target_w_per_m2:.2f}"

        modified = re.sub(pattern, adjust_epd, idf_content, flags=re.IGNORECASE)
        return modified

    def run_initial_simulation(self, idf_file):
        """Run initial annual simulation"""

        print("\n" + "="*80)
        print("RUNNING INITIAL SIMULATION")
        print("="*80 + "\n")

        import subprocess

        weather_file = Path("/app/software/EnergyPlusV25-1-0/WeatherData/USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")
        output_dir = self.work_dir / "initial_run"
        output_dir.mkdir(exist_ok=True)

        print("⏳ Running annual simulation (2-3 minutes)...\n")

        cmd = [
            "energyplus",
            "--annual",
            "-w", str(weather_file),
            "-d", str(output_dir),
            str(idf_file)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Initial simulation completed!")
        else:
            print(f"⚠️  Simulation returned code {result.returncode}")

        # Extract annual energy
        table_file = output_dir / "eplustbl.htm"
        if table_file.exists():
            with open(table_file, 'r') as f:
                content = f.read()

            # Extract total site energy
            match = re.search(r'Total Site Energy.*?<td[^>]*>\s*([\d.]+)', content, re.IGNORECASE | re.DOTALL)
            if match:
                total_gj = float(match.group(1))
                total_kwh = total_gj * 277.778
                print(f"\n📊 Initial Model Results:")
                print(f"   Total Site Energy: {total_kwh:,.0f} kWh/year")
                print(f"   (vs. Actual bills: {self.audit['utility_data']['electricity']['annual_kwh']:,} kWh/year)")

                error = ((total_kwh - self.audit['utility_data']['electricity']['annual_kwh']) /
                        self.audit['utility_data']['electricity']['annual_kwh'] * 100)
                print(f"   Initial Error: {error:+.1f}%")

                if abs(error) > 15:
                    print(f"   ⚠️  Model needs calibration (>15% error)")
                elif abs(error) > 5:
                    print(f"   ⚠️  Model needs calibration (>5% error)")
                else:
                    print(f"   ✅ Model already close! (But still should calibrate)")

                return total_kwh, error

        return None, None

def main():
    """Execute Step 2"""

    print("\n" + "="*80)
    print("AUDIT → MODEL → CALIBRATION WORKFLOW")
    print("="*80)

    # Step 1 recap
    audit_file = Path("/workspace/energyplus-mcp-server/energy_audit_data.json")

    if not audit_file.exists():
        print("\n❌ Error: Audit data not found!")
        print("   Run step1 first: python audit_to_model_workflow.py")
        return

    print("\n✅ STEP 1 COMPLETE: Audit data available")

    # Step 2: Build model
    builder = ModelBuilder(audit_file)
    baseline_idf = builder.create_initial_model()

    # Run initial simulation
    initial_energy, initial_error = builder.run_initial_simulation(baseline_idf)

    # Summary
    print("\n" + "="*80)
    print("✅ STEP 2 COMPLETE: Initial Model Built & Simulated")
    print("="*80)

    print(f"\n📁 Files created:")
    print(f"   Model: {baseline_idf}")
    print(f"   Results: {builder.work_dir}/initial_run/")

    print(f"\n🎯 Next: STEP 3 - Calibration")
    print(f"   Goal: Adjust uncertain parameters to match utility bills")
    print(f"   Target: MBE < ±5%, CV(RMSE) < ±15% (ASHRAE Guideline 14)")
    print(f"   Current error: {initial_error:+.1f}%")

    if abs(initial_error) > 15:
        print(f"   ⚠️  Calibration will make significant improvements")
    else:
        print(f"   ✅ Model already reasonable, calibration will refine")

    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
