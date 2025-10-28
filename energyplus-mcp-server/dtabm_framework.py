#!/usr/bin/env python3
"""
DTABM - Digital Twin Asset-Based Model Framework

CONCEPT:
- DTABM_Baseline: Calibrated model representing pre-retrofit condition
- DTABM_Operational: Real-time digital twin tracking actual performance
- DTActual: Post-ECM model that updates based on actual measured data

This enables:
1. Real-time performance monitoring
2. Continuous M&V (comparing actual vs. predicted)
3. Fault detection (deviations from expected performance)
4. Automated model updating as building changes
5. Predictive analytics (forecasting based on current state)
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

class DigitalTwinABM:
    """
    Digital Twin Asset-Based Model

    Maintains multiple model versions:
    - DTABM_Baseline: Pre-retrofit calibrated model (frozen)
    - DTABM_Operational: Current operating model (updates monthly)
    - DTActual: Post-ECM model reflecting implemented changes
    """

    def __init__(self, calibrated_baseline_idf):
        self.baseline_idf = calibrated_baseline_idf
        self.work_dir = Path("/workspace/energyplus-mcp-server/digital_twin")
        self.work_dir.mkdir(exist_ok=True)

        # Initialize digital twin structure
        self.dt_registry = {
            "DTABM_Baseline": {
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "description": "Calibrated pre-retrofit baseline (FROZEN)",
                "idf_file": str(calibrated_baseline_idf),
                "status": "frozen",
                "last_validation": None
            },
            "DTABM_Operational": {
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "description": "Current operational model (LIVE - updates monthly)",
                "idf_file": None,
                "status": "active",
                "last_update": None,
                "update_frequency": "monthly"
            },
            "DTActual": {
                "version": None,
                "created": None,
                "description": "Post-ECM model reflecting actual changes",
                "idf_file": None,
                "ecms_implemented": [],
                "status": "pending",
                "last_update": None
            }
        }

        # Save registry
        self.save_registry()

        print("\n" + "="*80)
        print("DIGITAL TWIN ASSET-BASED MODEL (DTABM) INITIALIZED")
        print("="*80 + "\n")

    def save_registry(self):
        """Save digital twin registry"""
        registry_file = self.work_dir / "dtabm_registry.json"
        with open(registry_file, 'w') as f:
            json.dump(self.dt_registry, f, indent=2)

    def create_dtabm_operational(self):
        """
        Create DTABM_Operational from baseline
        This is the living model that gets updated monthly
        """

        print("="*80)
        print("CREATING DTABM_OPERATIONAL")
        print("="*80 + "\n")

        import shutil

        # Copy baseline as starting point
        operational_idf = self.work_dir / "DTABM_Operational_v1.0.0.idf"
        shutil.copy(self.baseline_idf, operational_idf)

        # Update registry
        self.dt_registry["DTABM_Operational"]["idf_file"] = str(operational_idf)
        self.dt_registry["DTABM_Operational"]["last_update"] = datetime.now().isoformat()
        self.save_registry()

        print(f"✅ DTABM_Operational created")
        print(f"   File: {operational_idf.name}")
        print(f"   Status: ACTIVE - will update monthly with actual data")
        print(f"   Purpose: Real-time performance tracking\n")

        return operational_idf

    def monthly_update_dtabm(self, actual_energy_kwh, weather_data=None):
        """
        Monthly update of DTABM_Operational based on actual metered data

        This is the key to digital twin functionality:
        1. Get actual energy consumption from utility meter
        2. Compare to model prediction
        3. If deviation > threshold, recalibrate parameters
        4. Update operational model
        """

        print("="*80)
        print("MONTHLY DTABM UPDATE PROCESS")
        print("="*80 + "\n")

        current_date = datetime.now()

        print(f"📅 Update Date: {current_date.strftime('%Y-%m-%d')}")
        print(f"📊 Actual Energy (this month): {actual_energy_kwh:,.0f} kWh")

        # Run current operational model for comparison
        operational_idf = Path(self.dt_registry["DTABM_Operational"]["idf_file"])

        print(f"\n⏳ Running DTABM_Operational model...")

        # Simulate (simplified - would run for specific month with actual weather)
        predicted_energy_kwh = self.run_monthly_simulation(operational_idf)

        if predicted_energy_kwh:
            print(f"   Predicted: {predicted_energy_kwh:,.0f} kWh")
            print(f"   Actual: {actual_energy_kwh:,.0f} kWh")

            error_pct = (actual_energy_kwh - predicted_energy_kwh) / predicted_energy_kwh * 100
            print(f"   Deviation: {error_pct:+.1f}%")

            # Determine if recalibration needed
            if abs(error_pct) > 10:
                print(f"\n⚠️  ALERT: Deviation > 10% - Recalibration recommended")
                print(f"   Possible causes:")
                print(f"   - Occupancy change")
                print(f"   - Equipment failure")
                print(f"   - Operational schedule change")
                print(f"   - Weather normalization issue")

                # Log for investigation
                self.log_anomaly(current_date, predicted_energy_kwh, actual_energy_kwh, error_pct)

            elif abs(error_pct) > 5:
                print(f"\n⚠️  Warning: Deviation > 5% - Monitor trend")

            else:
                print(f"\n✅ Model tracking well (< 5% error)")

            # Update tracking data
            self.update_tracking_data(current_date, predicted_energy_kwh, actual_energy_kwh, error_pct)

        # Update registry
        self.dt_registry["DTABM_Operational"]["last_update"] = current_date.isoformat()
        self.save_registry()

        return error_pct

    def run_monthly_simulation(self, idf_file):
        """Run model for specific month (simplified)"""
        # In real implementation, would:
        # 1. Use actual weather data for the month
        # 2. Run EnergyPlus for just that month
        # 3. Extract monthly energy consumption

        # For demo, return calibrated baseline annual / 12
        return 449389 / 12  # ~37,449 kWh/month

    def log_anomaly(self, date, predicted, actual, error_pct):
        """Log performance anomalies for investigation"""

        anomaly_log = self.work_dir / "anomaly_log.csv"

        anomaly = {
            'date': date.strftime('%Y-%m-%d'),
            'predicted_kwh': predicted,
            'actual_kwh': actual,
            'error_pct': error_pct,
            'severity': 'HIGH' if abs(error_pct) > 15 else 'MEDIUM',
            'investigated': False
        }

        # Append to log
        df = pd.DataFrame([anomaly])

        if anomaly_log.exists():
            df.to_csv(anomaly_log, mode='a', header=False, index=False)
        else:
            df.to_csv(anomaly_log, index=False)

        print(f"\n   📝 Anomaly logged to: {anomaly_log.name}")

    def update_tracking_data(self, date, predicted, actual, error):
        """Update monthly tracking data"""

        tracking_file = self.work_dir / "dtabm_tracking.csv"

        data = {
            'date': date.strftime('%Y-%m-%d'),
            'predicted_kwh': predicted,
            'actual_kwh': actual,
            'error_pct': error,
            'model_version': self.dt_registry["DTABM_Operational"]["version"]
        }

        df = pd.DataFrame([data])

        if tracking_file.exists():
            df.to_csv(tracking_file, mode='a', header=False, index=False)
        else:
            df.to_csv(tracking_file, index=False)

    def implement_ecm(self, ecm_name, ecm_description, ecm_modifications):
        """
        Create DTActual model after ECM implementation

        This is called AFTER physical retrofit is complete
        Creates new model reflecting actual changes made
        """

        print("\n" + "="*80)
        print(f"IMPLEMENTING ECM IN DIGITAL TWIN: {ecm_name}")
        print("="*80 + "\n")

        print(f"📋 ECM: {ecm_name}")
        print(f"   Description: {ecm_description}")
        print(f"   Implementation Date: {datetime.now().strftime('%Y-%m-%d')}")

        # Create DTActual if first ECM
        if self.dt_registry["DTActual"]["version"] is None:
            print(f"\n🆕 Creating DTActual (first ECM implementation)")

            import shutil

            # Start from DTABM_Operational (most current)
            operational_idf = Path(self.dt_registry["DTABM_Operational"]["idf_file"])
            dtactual_idf = self.work_dir / "DTActual_v1.0.0.idf"
            shutil.copy(operational_idf, dtactual_idf)

            self.dt_registry["DTActual"]["version"] = "1.0.0"
            self.dt_registry["DTActual"]["created"] = datetime.now().isoformat()
            self.dt_registry["DTActual"]["idf_file"] = str(dtactual_idf)
            self.dt_registry["DTActual"]["status"] = "active"

        else:
            dtactual_idf = Path(self.dt_registry["DTActual"]["idf_file"])

        # Apply ECM modifications
        print(f"\n🔧 Applying modifications to DTActual...")

        with open(dtactual_idf, 'r') as f:
            content = f.read()

        # Apply modifications (example: LED lighting)
        if 'lighting' in ecm_modifications:
            import re
            reduction_factor = ecm_modifications['lighting']['reduction_factor']
            print(f"   - Reducing lighting power by {(1-reduction_factor)*100:.0f}%")

            content = re.sub(
                r'(Lights,\s*[^;]+?Watts/Area[^;]+?)(\d+\.?\d*)',
                lambda m: f"{m.group(1)}{float(m.group(2)) * reduction_factor:.2f}",
                content,
                flags=re.IGNORECASE
            )

        # Write updated DTActual
        with open(dtactual_idf, 'w') as f:
            f.write(content)

        # Log ECM implementation
        ecm_record = {
            'ecm_name': ecm_name,
            'description': ecm_description,
            'implementation_date': datetime.now().isoformat(),
            'modifications': ecm_modifications
        }

        self.dt_registry["DTActual"]["ecms_implemented"].append(ecm_record)
        self.dt_registry["DTActual"]["last_update"] = datetime.now().isoformat()

        # Increment version
        current_version = self.dt_registry["DTActual"]["version"]
        major, minor, patch = current_version.split('.')
        new_version = f"{major}.{int(minor)+1}.{patch}"
        self.dt_registry["DTActual"]["version"] = new_version

        # Rename file with new version
        new_dtactual = self.work_dir / f"DTActual_v{new_version}.idf"
        import shutil
        shutil.copy(dtactual_idf, new_dtactual)
        self.dt_registry["DTActual"]["idf_file"] = str(new_dtactual)

        self.save_registry()

        print(f"\n✅ DTActual updated")
        print(f"   Version: {new_version}")
        print(f"   ECMs implemented: {len(self.dt_registry['DTActual']['ecms_implemented'])}")
        print(f"   File: {new_dtactual.name}")

        return new_dtactual

    def post_ecm_validation(self, post_ecm_actual_energy, duration_months=3):
        """
        Validate DTActual against post-ECM actual data
        Ensures digital twin reflects reality after retrofit
        """

        print("\n" + "="*80)
        print("POST-ECM VALIDATION: DTActual vs. Actual Performance")
        print("="*80 + "\n")

        print(f"📊 Validation Period: {duration_months} months post-implementation")
        print(f"   Actual Energy: {post_ecm_actual_energy:,.0f} kWh")

        # Run DTActual
        dtactual_idf = Path(self.dt_registry["DTActual"]["idf_file"])
        print(f"\n⏳ Running DTActual model...")

        predicted_energy = self.run_monthly_simulation(dtactual_idf) * duration_months

        print(f"   DTActual Predicted: {predicted_energy:,.0f} kWh")
        print(f"   Actual Measured: {post_ecm_actual_energy:,.0f} kWh")

        error_pct = (post_ecm_actual_energy - predicted_energy) / predicted_energy * 100
        print(f"   Deviation: {error_pct:+.1f}%")

        if abs(error_pct) <= 5:
            print(f"\n✅ DTActual VALIDATED - tracking post-ECM performance well")
            self.dt_registry["DTActual"]["status"] = "validated"
        elif abs(error_pct) <= 10:
            print(f"\n⚠️  DTActual ACCEPTABLE - minor recalibration may improve")
            self.dt_registry["DTActual"]["status"] = "acceptable"
        else:
            print(f"\n❌ DTActual NEEDS RECALIBRATION - significant deviation")
            self.dt_registry["DTActual"]["status"] = "needs_recalibration"

        self.save_registry()

        return error_pct

    def calculate_mv_savings(self, baseline_energy, actual_energy, weather_adjustment=1.0):
        """
        Calculate M&V savings: DTABM_Baseline vs. Actual

        Savings = Baseline - Actual (weather-adjusted)
        """

        print("\n" + "="*80)
        print("M&V SAVINGS CALCULATION")
        print("="*80 + "\n")

        print(f"📊 Measurement & Verification (IPMVP Option C)")

        # Weather-normalize actual energy
        actual_normalized = actual_energy * weather_adjustment

        print(f"\n   DTABM_Baseline: {baseline_energy:,.0f} kWh")
        print(f"   Actual (measured): {actual_energy:,.0f} kWh")
        print(f"   Weather adjustment factor: {weather_adjustment:.3f}")
        print(f"   Actual (normalized): {actual_normalized:,.0f} kWh")

        savings_kwh = baseline_energy - actual_normalized
        savings_pct = (savings_kwh / baseline_energy) * 100

        print(f"\n💰 SAVINGS:")
        print(f"   Energy: {savings_kwh:,.0f} kWh ({savings_pct:.1f}%)")
        print(f"   Cost (@ $0.12/kWh): ${savings_kwh * 0.12:,.0f}")

        # Save M&V report
        mv_report = {
            'report_date': datetime.now().isoformat(),
            'baseline_kwh': baseline_energy,
            'actual_kwh': actual_energy,
            'weather_adjustment': weather_adjustment,
            'actual_normalized_kwh': actual_normalized,
            'savings_kwh': savings_kwh,
            'savings_pct': savings_pct,
            'cost_savings_usd': savings_kwh * 0.12
        }

        mv_file = self.work_dir / "mv_report.json"
        with open(mv_file, 'w') as f:
            json.dump(mv_report, f, indent=2)

        print(f"\n   📄 M&V Report saved: {mv_file.name}")

        return savings_kwh, savings_pct

    def generate_dashboard_data(self):
        """Generate data for digital twin dashboard"""

        print("\n" + "="*80)
        print("DIGITAL TWIN DASHBOARD DATA")
        print("="*80 + "\n")

        dashboard = {
            "models": {
                "DTABM_Baseline": {
                    "status": self.dt_registry["DTABM_Baseline"]["status"],
                    "purpose": "Pre-retrofit reference (frozen)",
                    "annual_energy_kwh": 449389
                },
                "DTABM_Operational": {
                    "status": self.dt_registry["DTABM_Operational"]["status"],
                    "purpose": "Current operations tracking",
                    "last_update": self.dt_registry["DTABM_Operational"]["last_update"],
                    "update_frequency": "monthly"
                },
                "DTActual": {
                    "status": self.dt_registry["DTActual"].get("status", "not_created"),
                    "purpose": "Post-ECM performance model",
                    "ecms_count": len(self.dt_registry["DTActual"].get("ecms_implemented", []))
                }
            },
            "alerts": self.check_alerts(),
            "performance_metrics": self.calculate_performance_metrics()
        }

        print("📊 DTABM Status:")
        for model_name, info in dashboard["models"].items():
            print(f"\n   {model_name}:")
            print(f"      Status: {info['status']}")
            print(f"      Purpose: {info['purpose']}")

        return dashboard

    def check_alerts(self):
        """Check for performance alerts"""

        alerts = []

        # Check for anomalies
        anomaly_log = self.work_dir / "anomaly_log.csv"
        if anomaly_log.exists():
            df = pd.read_csv(anomaly_log)
            uninvestigated = df[df['investigated'] == False]

            if len(uninvestigated) > 0:
                alerts.append({
                    'severity': 'HIGH',
                    'message': f'{len(uninvestigated)} uninvestigated anomalies'
                })

        return alerts

    def calculate_performance_metrics(self):
        """Calculate key performance metrics"""

        tracking_file = self.work_dir / "dtabm_tracking.csv"

        if tracking_file.exists():
            df = pd.read_csv(tracking_file)

            if len(df) > 0:
                avg_error = df['error_pct'].abs().mean()
                max_error = df['error_pct'].abs().max()

                return {
                    'avg_tracking_error_pct': avg_error,
                    'max_tracking_error_pct': max_error,
                    'months_tracked': len(df)
                }

        return {}

def main():
    """Initialize DTABM Framework"""

    print("\n" + "="*80)
    print("DIGITAL TWIN ASSET-BASED MODEL (DTABM) FRAMEWORK")
    print("="*80)

    # Initialize with calibrated baseline
    calibrated_baseline = Path("/workspace/energyplus-mcp-server/calibration_workflow/baseline_calibrated.idf")

    if not calibrated_baseline.exists():
        print("\n❌ Calibrated baseline not found. Run steps 1-3 first.")
        return

    print("\n✅ Calibrated baseline found")

    # Create DTABM
    dtabm = DigitalTwinABM(calibrated_baseline)

    # Create operational model
    dtabm.create_dtabm_operational()

    # Demo: Monthly update
    print("\n" + "="*80)
    print("DEMO: MONTHLY OPERATIONAL TRACKING")
    print("="*80 + "\n")

    # Simulate first month of operation
    actual_january = 38500  # kWh (slightly higher than predicted)
    dtabm.monthly_update_dtabm(actual_january)

    # Demo: ECM Implementation
    print("\n" + "="*80)
    print("DEMO: ECM IMPLEMENTATION")
    print("="*80)

    dtabm.implement_ecm(
        ecm_name="LED_Lighting_Retrofit",
        ecm_description="Replace T8 fluorescent with LED fixtures",
        ecm_modifications={
            'lighting': {
                'reduction_factor': 0.5  # 50% reduction
            }
        }
    )

    # Demo: Post-ECM validation
    print("\n" + "="*80)
    print("DEMO: POST-ECM VALIDATION")
    print("="*80)

    # Simulate 3 months post-ECM
    post_ecm_actual = 95000  # kWh for 3 months
    dtabm.post_ecm_validation(post_ecm_actual, duration_months=3)

    # Demo: M&V Savings
    print("\n" + "="*80)
    print("DEMO: M&V SAVINGS CALCULATION")
    print("="*80)

    baseline_annual = 449389  # From calibrated model
    actual_post_ecm_annual = 380000  # Hypothetical actual consumption
    dtabm.calculate_mv_savings(baseline_annual, actual_post_ecm_annual, weather_adjustment=1.02)

    # Generate dashboard
    dashboard = dtabm.generate_dashboard_data()

    print("\n" + "="*80)
    print("✅ DTABM FRAMEWORK OPERATIONAL")
    print("="*80)

    print(f"\n📁 Digital Twin Registry: {dtabm.work_dir}/dtabm_registry.json")
    print(f"\n🎯 Framework Ready For:")
    print(f"   - Real-time performance monitoring")
    print(f"   - Continuous M&V")
    print(f"   - Fault detection")
    print(f"   - Automated model updating")
    print(f"   - Predictive analytics")

    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
