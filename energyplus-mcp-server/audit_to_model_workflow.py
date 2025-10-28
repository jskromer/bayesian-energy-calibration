#!/usr/bin/env python3
"""
Complete Energy Audit → Calibrated Model → Retrofit Analysis Workflow

WORKFLOW:
1. Energy Audit: Collect building data
2. Initial Model: Create EnergyPlus model from audit
3. Calibration: Match model to utility bills using Bayesian methods
4. Baseline: Validated, calibrated baseline model
5. Retrofit: Test ECMs (Energy Conservation Measures)
6. M&V: Calculate savings with uncertainty

This follows ASHRAE Guideline 14 and IPMVP protocols
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime

class EnergyAuditData:
    """
    Energy audit data collection template
    This represents what you'd gather during a site visit
    """

    def __init__(self):
        self.audit_date = datetime.now().strftime("%Y-%m-%d")
        self.building_info = {}
        self.envelope = {}
        self.hvac = {}
        self.lighting = {}
        self.equipment = {}
        self.occupancy = {}
        self.utility_data = {}

    def collect_building_info(self):
        """Basic building information"""
        return {
            "building_name": "Example Office Building",
            "address": "123 Main St, Chicago, IL",
            "building_type": "Office",
            "year_built": 1995,
            "gross_area_sqft": 25000,
            "conditioned_area_sqft": 23500,
            "num_floors": 3,
            "floor_to_floor_height_ft": 13,
            "operating_hours": {
                "weekday": "7:00 AM - 6:00 PM",
                "saturday": "Closed",
                "sunday": "Closed"
            },
            "num_occupants": 75
        }

    def collect_envelope_data(self):
        """Building envelope characteristics"""
        return {
            "walls": {
                "construction": "Brick veneer with batt insulation",
                "r_value": 11,  # hr-ft²-°F/BTU
                "measured_thickness_inches": 10,
                "condition": "Fair - some air leakage noted"
            },
            "roof": {
                "construction": "Built-up roof with rigid insulation",
                "r_value": 15,
                "age_years": 15,
                "condition": "Good"
            },
            "windows": {
                "type": "Double-pane, aluminum frame",
                "u_factor": 0.55,  # BTU/hr-ft²-°F
                "shgc": 0.60,  # Solar Heat Gain Coefficient
                "window_to_wall_ratio": 0.35,
                "condition": "Original, some seal failures"
            },
            "infiltration": {
                "blower_door_test": False,
                "estimated_ach50": 12,  # Air Changes per Hour at 50 Pa
                "notes": "Visible gaps around doors, windows"
            }
        }

    def collect_hvac_data(self):
        """HVAC system information"""
        return {
            "system_type": "Packaged Rooftop Units (RTUs)",
            "units": [
                {
                    "unit_id": "RTU-1",
                    "serves": "Floors 1-2",
                    "capacity_tons": 15,
                    "manufacturer": "Carrier",
                    "model": "48TFE015",
                    "year_installed": 2005,
                    "efficiency_eer": 10.5,
                    "heating_type": "Natural gas furnace",
                    "heating_efficiency_afue": 0.80,
                    "condition": "Fair - maintenance irregular",
                    "economizer": True,
                    "economizer_working": False  # Noted during audit!
                },
                {
                    "unit_id": "RTU-2",
                    "serves": "Floor 3",
                    "capacity_tons": 10,
                    "manufacturer": "Trane",
                    "model": "YCD120",
                    "year_installed": 2008,
                    "efficiency_eer": 11.0,
                    "heating_type": "Natural gas furnace",
                    "heating_efficiency_afue": 0.82,
                    "condition": "Good",
                    "economizer": True,
                    "economizer_working": True
                }
            ],
            "thermostat_schedule": {
                "occupied_cooling_setpoint_f": 73,
                "occupied_heating_setpoint_f": 70,
                "unoccupied_cooling_setpoint_f": 78,
                "unoccupied_heating_setpoint_f": 65
            },
            "duct_leakage": {
                "tested": False,
                "estimated_leakage_pct": 15,  # Typical for older systems
                "notes": "Visible gaps at connections, poor sealing"
            }
        }

    def collect_lighting_data(self):
        """Lighting system inventory"""
        return {
            "spaces": [
                {
                    "space_type": "Open Office",
                    "area_sqft": 15000,
                    "fixture_type": "2x4 T8 fluorescent troffer",
                    "lamps_per_fixture": 3,
                    "watts_per_lamp": 32,
                    "num_fixtures": 300,
                    "total_watts": 28800,
                    "lpd_w_per_sqft": 1.92,
                    "hours_per_day": 10,
                    "occupancy_sensor": False,
                    "daylight_sensor": False
                },
                {
                    "space_type": "Private Offices",
                    "area_sqft": 4500,
                    "fixture_type": "2x4 T8 fluorescent",
                    "lamps_per_fixture": 2,
                    "watts_per_lamp": 32,
                    "num_fixtures": 90,
                    "total_watts": 5760,
                    "lpd_w_per_sqft": 1.28,
                    "hours_per_day": 10,
                    "occupancy_sensor": False,
                    "daylight_sensor": False
                },
                {
                    "space_type": "Corridors/Restrooms",
                    "area_sqft": 2500,
                    "fixture_type": "2x2 T8 fluorescent",
                    "lamps_per_fixture": 2,
                    "watts_per_lamp": 17,
                    "num_fixtures": 50,
                    "total_watts": 1700,
                    "lpd_w_per_sqft": 0.68,
                    "hours_per_day": 12,  # Longer hours
                    "occupancy_sensor": False,
                    "daylight_sensor": False
                },
                {
                    "space_type": "Parking Lot",
                    "area_sqft": 30000,
                    "fixture_type": "Metal Halide pole lights",
                    "watts_per_fixture": 400,
                    "num_fixtures": 12,
                    "total_watts": 4800,
                    "hours_per_day": 12,  # Dusk to dawn
                    "condition": "Poor efficiency, frequent failures"
                }
            ],
            "total_interior_lpd": 1.54,  # W/sqft weighted average
            "control_issues": [
                "Many lights left on after hours",
                "No automatic shutoff",
                "Occupancy sensors not used"
            ]
        }

    def collect_equipment_data(self):
        """Plug loads and equipment"""
        return {
            "office_equipment": {
                "computers": 75,
                "watts_per_computer": 150,
                "monitors": 75,
                "watts_per_monitor": 50,
                "printers_copiers": 8,
                "watts_per_unit": 500,
                "usage_hours_per_day": 9
            },
            "kitchen_breakroom": {
                "refrigerators": 3,
                "microwaves": 2,
                "coffee_makers": 2,
                "vending_machines": 2
            },
            "estimated_plug_load_density": 1.2,  # W/sqft
            "notes": "Equipment left on 24/7, no power management"
        }

    def collect_occupancy_data(self):
        """Occupancy patterns"""
        return {
            "typical_weekday": {
                "peak_occupancy": 75,
                "peak_time": "10:00 AM - 3:00 PM",
                "arrival_time": "7:00 AM - 9:00 AM",
                "departure_time": "4:00 PM - 6:00 PM"
            },
            "weekend": "Closed - security only",
            "holidays": 10,  # days per year
            "density_people_per_1000sqft": 3.2
        }

    def collect_utility_data(self):
        """12 months of utility bills"""
        return {
            "electricity": {
                "utility": "ComEd",
                "account": "1234567890",
                "rate_structure": "Commercial - Time of Use",
                "monthly_kwh": [
                    # Month, kWh, Cost
                    ("2024-01", 28500, 3420),
                    ("2024-02", 26800, 3216),
                    ("2024-03", 29200, 3504),
                    ("2024-04", 31500, 3780),
                    ("2024-05", 36800, 4416),
                    ("2024-06", 42500, 5100),
                    ("2024-07", 48200, 5784),
                    ("2024-08", 47800, 5736),
                    ("2024-09", 39500, 4740),
                    ("2024-10", 33200, 3984),
                    ("2024-11", 30500, 3660),
                    ("2024-12", 29800, 3576)
                ],
                "annual_kwh": 424300,
                "annual_cost": 50916,
                "avg_rate_per_kwh": 0.12,
                "demand_charges": "Yes - $15/kW peak"
            },
            "natural_gas": {
                "utility": "Peoples Gas",
                "account": "9876543210",
                "monthly_therms": [
                    # Month, Therms, Cost
                    ("2024-01", 2850, 3135),
                    ("2024-02", 2650, 2915),
                    ("2024-03", 2150, 2365),
                    ("2024-04", 1200, 1320),
                    ("2024-05", 450, 495),
                    ("2024-06", 280, 308),
                    ("2024-07", 250, 275),
                    ("2024-08", 240, 264),
                    ("2024-09", 380, 418),
                    ("2024-10", 950, 1045),
                    ("2024-11", 1850, 2035),
                    ("2024-12", 2680, 2948)
                ],
                "annual_therms": 15930,
                "annual_cost": 17523,
                "avg_rate_per_therm": 1.10
            }
        }

    def generate_audit_report(self):
        """Compile complete audit data"""

        print("\n" + "="*80)
        print("ENERGY AUDIT DATA COLLECTION")
        print("="*80 + "\n")

        audit_data = {
            "audit_date": self.audit_date,
            "building": self.collect_building_info(),
            "envelope": self.collect_envelope_data(),
            "hvac": self.collect_hvac_data(),
            "lighting": self.collect_lighting_data(),
            "equipment": self.collect_equipment_data(),
            "occupancy": self.collect_occupancy_data(),
            "utility_data": self.collect_utility_data()
        }

        # Save to JSON
        output_file = Path("/workspace/energyplus-mcp-server/energy_audit_data.json")
        with open(output_file, 'w') as f:
            json.dump(audit_data, f, indent=2)

        print(f"✅ Energy audit data compiled")
        print(f"   Saved to: {output_file}")

        # Print summary
        print(f"\n📋 BUILDING SUMMARY")
        print(f"   Name: {audit_data['building']['building_name']}")
        print(f"   Type: {audit_data['building']['building_type']}")
        print(f"   Size: {audit_data['building']['gross_area_sqft']:,} sq ft")
        print(f"   Built: {audit_data['building']['year_built']}")

        print(f"\n💡 ANNUAL ENERGY CONSUMPTION")
        print(f"   Electricity: {audit_data['utility_data']['electricity']['annual_kwh']:,} kWh")
        print(f"   Natural Gas: {audit_data['utility_data']['natural_gas']['annual_therms']:,} therms")
        print(f"   Total Cost: ${audit_data['utility_data']['electricity']['annual_cost'] + audit_data['utility_data']['natural_gas']['annual_cost']:,}")

        print(f"\n📊 ENERGY USE INTENSITY")
        area = audit_data['building']['gross_area_sqft']
        elec_eui = audit_data['utility_data']['electricity']['annual_kwh'] / area
        gas_eui = audit_data['utility_data']['natural_gas']['annual_therms'] * 100 / area  # kBTU/sqft
        print(f"   Electric: {elec_eui:.1f} kWh/sqft/year")
        print(f"   Gas: {gas_eui:.1f} kBTU/sqft/year")

        print(f"\n🔍 KEY FINDINGS FROM AUDIT")
        print(f"   ⚠️  RTU-1 economizer not functional")
        print(f"   ⚠️  Estimated 15% duct leakage")
        print(f"   ⚠️  No lighting controls (occupancy/daylight sensors)")
        print(f"   ⚠️  Equipment left on 24/7 (no power management)")
        print(f"   ⚠️  Infiltration issues (visible gaps)")
        print(f"   ⚠️  Old windows (U=0.55, SHGC=0.60)")

        print(f"\n💡 RECOMMENDED ECMs (Energy Conservation Measures)")
        print(f"   1. Fix RTU-1 economizer")
        print(f"   2. Seal ductwork (reduce leakage to <5%)")
        print(f"   3. LED lighting retrofit + occupancy sensors")
        print(f"   4. Enable computer power management")
        print(f"   5. Air sealing / weatherization")
        print(f"   6. Window film or replacement (long-term)")

        print("\n" + "="*80 + "\n")

        return audit_data

def main():
    """Run energy audit data collection"""

    print("\n" + "="*80)
    print("ENERGY AUDIT TO CALIBRATED MODEL WORKFLOW")
    print("Step 1: Energy Audit Data Collection")
    print("="*80)

    # Create audit
    audit = EnergyAuditData()
    audit_data = audit.generate_audit_report()

    print("✅ STEP 1 COMPLETE: Audit Data Collected")
    print("\nNext Steps:")
    print("  Step 2: Build initial EnergyPlus model from audit data")
    print("  Step 3: Calibrate model to match utility bills")
    print("  Step 4: Create validated baseline")
    print("  Step 5: Model retrofit scenarios")
    print("  Step 6: Calculate savings with uncertainty")

    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
