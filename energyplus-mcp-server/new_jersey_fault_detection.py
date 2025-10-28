#!/usr/bin/env python3
"""
New Jersey Building Fault Detection

Customized fault detection analysis for New Jersey building project.
Demonstrates MCP integration with local climate and utility rates.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import json

# MCP Integration
from energyplus_mcp_server.config import get_config
from energyplus_mcp_server.energyplus_tools import EnergyPlusManager


class SimpleInterpolator:
    """Simple linear interpolation fallback if scikit-learn not available"""

    def __init__(self, X, y):
        self.X = X.ravel()
        self.y = y
        # Sort by X
        sort_idx = np.argsort(self.X)
        self.X = self.X[sort_idx]
        self.y = self.y[sort_idx]

    def predict(self, X_new, return_std=False):
        X_new = np.array(X_new).ravel()
        y_pred = np.interp(X_new, self.X, self.y)

        if return_std:
            # Simple heuristic: higher uncertainty farther from data
            distances = np.min(np.abs(X_new[:, None] - self.X), axis=1)
            std = 5000 * (1 + distances * 5)  # Rough uncertainty estimate
            return y_pred, std
        else:
            return y_pred


# Check for optional dependencies
GP_AVAILABLE = False
ARVIZ_AVAILABLE = False

try:
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
    GP_AVAILABLE = True
except ImportError:
    print("⚠️  scikit-learn not installed. Using simple interpolation.")
    print("   Install with: uv pip install scikit-learn")

try:
    import arviz as az
    import matplotlib.pyplot as plt
    ARVIZ_AVAILABLE = True
except ImportError:
    print("⚠️  ArviZ/matplotlib not installed. Visualizations will be skipped.")
    print("   Install with: uv pip install arviz matplotlib")


class NewJerseyFaultDetector:
    """
    Fault detection customized for New Jersey buildings
    """

    def __init__(self, idf_path: str, weather_file: str, building_name: str = "NJ Building"):
        self.idf_path = idf_path
        self.weather_file = weather_file
        self.building_name = building_name

        # MCP Manager
        config = get_config()
        self.manager = EnergyPlusManager(config)

        # Training data
        self.X_train = []
        self.y_train = []
        self.gp = None

        # New Jersey specific settings
        self.nj_electricity_rate = 0.15  # $/kWh (NJ commercial average ~$0.15)
        self.nj_gas_rate = 1.20  # $/therm (NJ commercial average ~$1.20)

        print(f"🏢 New Jersey Fault Detector Initialized")
        print(f"   Building: {building_name}")
        print(f"   IDF: {idf_path}")
        print(f"   Weather: {weather_file}")
        print(f"   Electricity rate: ${self.nj_electricity_rate:.2f}/kWh")
        print(f"   Natural gas rate: ${self.nj_gas_rate:.2f}/therm")

    def run_simulation(self, infiltration_mult: float, label: str = "") -> dict:
        """
        Run EnergyPlus simulation via MCP

        Returns:
            dict with energy results (electricity_kwh, gas_therms)
        """
        print(f"\n🔧 {label}")
        print(f"   Infiltration multiplier: {infiltration_mult:.2f}")

        # Create modified IDF
        modified_idf = f"sample_files/nj_fault_{infiltration_mult:.2f}.idf"

        self.manager.change_infiltration_by_mult(
            idf_path=self.idf_path,
            mult=infiltration_mult,
            output_path=modified_idf
        )

        # Run simulation
        result_json = self.manager.run_simulation(
            idf_path=modified_idf,
            weather_file=self.weather_file,
            annual=True
        )

        # Parse result
        result = json.loads(result_json)
        output_dir = Path(result['output_directory'])

        # Extract energy from HTML
        html_files = list(output_dir.glob("*Table.htm"))
        if html_files:
            import re
            html_content = html_files[0].read_text()

            # Total site energy
            match = re.search(r'Total Site Energy.*?(\d+\.\d+).*?GJ', html_content, re.DOTALL)
            if match:
                energy_gj = float(match.group(1))
                energy_kwh = energy_gj * 277.778

                print(f"   ✅ Total Energy: {energy_kwh:,.0f} kWh/year")

                return {
                    'total_energy_kwh': energy_kwh,
                    'infiltration_mult': infiltration_mult
                }

        raise ValueError(f"Could not extract energy from {output_dir}")

    def build_surrogate(self, n_samples: int = 8):
        """Build surrogate model across parameter space"""
        print(f"\n📊 Building Surrogate Model for {self.building_name}")
        print(f"   Running {n_samples} simulations...")

        infiltration_values = np.linspace(0.5, 2.0, n_samples)

        for i, infil_mult in enumerate(infiltration_values, 1):
            result = self.run_simulation(
                infiltration_mult=infil_mult,
                label=f"Training simulation {i}/{n_samples}"
            )

            self.X_train.append([infil_mult])
            self.y_train.append(result['total_energy_kwh'])

        self.X_train = np.array(self.X_train)
        self.y_train = np.array(self.y_train)

        # Fit model
        if GP_AVAILABLE:
            kernel = C(1.0, (1e-3, 1e3)) * RBF(1.0, (1e-2, 1e2))
            self.gp = GaussianProcessRegressor(
                kernel=kernel,
                n_restarts_optimizer=10,
                alpha=1e-6,
                normalize_y=True
            )
            self.gp.fit(self.X_train, self.y_train)
            print(f"   ✅ Gaussian Process surrogate fitted")
        else:
            self.gp = SimpleInterpolator(self.X_train, self.y_train)
            print(f"   ✅ Linear interpolator fitted")

        print(f"   Energy range: {self.y_train.min():,.0f} - {self.y_train.max():,.0f} kWh/year")

    def detect_fault(self, observed_energy_kwh: float, n_samples: int = 1000):
        """
        Bayesian fault detection

        Args:
            observed_energy_kwh: Measured annual energy from utility bills
            n_samples: Number of posterior samples

        Returns:
            Posterior samples of infiltration multiplier
        """
        print(f"\n🎯 Bayesian Fault Detection")
        print(f"   Observed energy: {observed_energy_kwh:,.0f} kWh/year")

        # Rejection sampling for posterior
        prior_samples = np.random.uniform(0.5, 2.0, size=n_samples * 10)
        gp_predictions, gp_std = self.gp.predict(prior_samples.reshape(-1, 1), return_std=True)

        # Likelihood with measurement uncertainty
        observation_noise = 5000  # kWh
        likelihood = np.exp(-0.5 * ((gp_predictions - observed_energy_kwh) / observation_noise) ** 2)

        # Sample from posterior
        acceptance_prob = likelihood / likelihood.max()
        accepted = np.random.rand(len(prior_samples)) < acceptance_prob
        posterior_samples = prior_samples[accepted][:n_samples]

        print(f"   ✅ Generated {len(posterior_samples)} posterior samples")
        print(f"   Acceptance rate: {accepted.sum() / len(prior_samples) * 100:.1f}%")

        return posterior_samples

    def counterfactual_savings(self, posterior_samples: np.ndarray):
        """
        Calculate savings if leak is fixed (infiltration = 1.0)

        Returns:
            DataFrame with savings analysis
        """
        print(f"\n💡 Counterfactual Analysis: Fix the Leak")

        # Current (faulty) state
        faulty_energy, _ = self.gp.predict(posterior_samples.reshape(-1, 1), return_std=True)

        # Fixed state (no leak)
        fixed_samples = np.ones_like(posterior_samples)
        fixed_energy, _ = self.gp.predict(fixed_samples.reshape(-1, 1), return_std=True)

        # Savings
        energy_savings_kwh = faulty_energy - fixed_energy
        cost_savings_usd = energy_savings_kwh * self.nj_electricity_rate

        results = pd.DataFrame({
            'infiltration_mult': posterior_samples,
            'faulty_energy_kwh': faulty_energy,
            'fixed_energy_kwh': fixed_energy,
            'energy_savings_kwh': energy_savings_kwh,
            'cost_savings_usd': cost_savings_usd
        })

        # Summary
        print(f"\n📊 Savings Potential (New Jersey Rates):")
        print(f"   Energy Savings:")
        print(f"      Mean:   {energy_savings_kwh.mean():>10,.0f} kWh/year")
        print(f"      95% CI: [{np.percentile(energy_savings_kwh, 2.5):>8,.0f}, "
              f"{np.percentile(energy_savings_kwh, 97.5):>8,.0f}] kWh/year")
        print(f"\n   Cost Savings (@ ${self.nj_electricity_rate:.2f}/kWh):")
        print(f"      Mean:   ${cost_savings_usd.mean():>10,.2f}/year")
        print(f"      95% CI: [${np.percentile(cost_savings_usd, 2.5):>8,.2f}, "
              f"${np.percentile(cost_savings_usd, 97.5):>8,.2f}]/year")

        leak_prob = (posterior_samples > 1.1).sum() / len(posterior_samples) * 100
        print(f"\n   P(leak > 10%): {leak_prob:.1f}%")

        return results

    def visualize(self, posterior_samples: np.ndarray, observed_energy: float,
                  savings_results: pd.DataFrame, output_file: str = "nj_fault_analysis.png"):
        """Create visualization"""
        if not ARVIZ_AVAILABLE:
            print("⚠️  Visualization skipped (matplotlib not available)")
            return

        print(f"\n📈 Creating Visualizations...")

        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        fig.suptitle(f'{self.building_name} - Fault Detection Analysis (New Jersey)',
                     fontsize=16, fontweight='bold')

        # 1. Posterior distribution
        axes[0, 0].hist(posterior_samples, bins=30, color='steelblue', alpha=0.7, density=True)
        axes[0, 0].axvline(1.0, color='green', linestyle='--', linewidth=2, label='No leak')
        axes[0, 0].axvline(posterior_samples.mean(), color='red', linestyle='--', linewidth=2,
                          label=f'Mean: {posterior_samples.mean():.2f}')
        axes[0, 0].set_xlabel('Infiltration Multiplier')
        axes[0, 0].set_ylabel('Probability Density')
        axes[0, 0].set_title('Posterior: Leak Severity')
        axes[0, 0].legend()
        axes[0, 0].grid(alpha=0.3)

        # 2. GP surrogate
        x_plot = np.linspace(0.5, 2.0, 100).reshape(-1, 1)
        y_pred, y_std = self.gp.predict(x_plot, return_std=True)
        axes[0, 1].plot(x_plot, y_pred, 'b-', linewidth=2, label='GP mean')
        axes[0, 1].fill_between(x_plot.ravel(), y_pred - 2*y_std, y_pred + 2*y_std,
                               alpha=0.3, color='blue', label='95% CI')
        axes[0, 1].scatter(self.X_train, self.y_train, c='red', s=100, zorder=10,
                          label='Training data', edgecolor='black', linewidth=1)
        axes[0, 1].axhline(observed_energy, color='green', linestyle='--', linewidth=2,
                          label='Observed')
        axes[0, 1].set_xlabel('Infiltration Multiplier')
        axes[0, 1].set_ylabel('Energy (kWh/year)')
        axes[0, 1].set_title('Surrogate Model')
        axes[0, 1].legend()
        axes[0, 1].grid(alpha=0.3)

        # 3. Energy savings distribution
        axes[0, 2].hist(savings_results['energy_savings_kwh'], bins=30, color='orange',
                       alpha=0.7, density=True)
        axes[0, 2].axvline(savings_results['energy_savings_kwh'].mean(), color='green',
                          linestyle='--', linewidth=2,
                          label=f"Mean: {savings_results['energy_savings_kwh'].mean():,.0f} kWh/yr")
        axes[0, 2].set_xlabel('Energy Savings (kWh/year)')
        axes[0, 2].set_ylabel('Probability Density')
        axes[0, 2].set_title('Energy Savings Potential')
        axes[0, 2].legend()
        axes[0, 2].grid(alpha=0.3)

        # 4. Cost savings distribution
        axes[1, 0].hist(savings_results['cost_savings_usd'], bins=30, color='green',
                       alpha=0.7, density=True)
        axes[1, 0].axvline(savings_results['cost_savings_usd'].mean(), color='darkgreen',
                          linestyle='--', linewidth=2,
                          label=f"Mean: ${savings_results['cost_savings_usd'].mean():,.0f}/yr")
        axes[1, 0].set_xlabel('Cost Savings ($/year)')
        axes[1, 0].set_ylabel('Probability Density')
        axes[1, 0].set_title(f'Cost Savings (NJ Rate: ${self.nj_electricity_rate:.2f}/kWh)')
        axes[1, 0].legend()
        axes[1, 0].grid(alpha=0.3)

        # 5. Scatter: infiltration vs savings
        axes[1, 1].scatter(savings_results['infiltration_mult'],
                          savings_results['energy_savings_kwh'],
                          alpha=0.5, s=20, color='orange')
        axes[1, 1].axhline(0, color='red', linestyle='--', linewidth=1)
        axes[1, 1].set_xlabel('Infiltration Multiplier')
        axes[1, 1].set_ylabel('Energy Savings (kWh)')
        axes[1, 1].set_title('Savings vs Leak Severity')
        axes[1, 1].grid(alpha=0.3)

        # 6. Summary table
        axes[1, 2].axis('off')
        summary_text = f"""
NEW JERSEY BUILDING ANALYSIS

Infiltration Multiplier:
  Mean:   {posterior_samples.mean():.3f}
  Median: {np.median(posterior_samples):.3f}
  95% CI: [{np.percentile(posterior_samples, 2.5):.3f},
           {np.percentile(posterior_samples, 97.5):.3f}]

Energy Savings:
  Mean:   {savings_results['energy_savings_kwh'].mean():,.0f} kWh/yr
  95% CI: [{np.percentile(savings_results['energy_savings_kwh'], 2.5):,.0f},
           {np.percentile(savings_results['energy_savings_kwh'], 97.5):,.0f}]

Cost Savings (NJ):
  Mean:   ${savings_results['cost_savings_usd'].mean():,.0f}/yr
  95% CI: [${np.percentile(savings_results['cost_savings_usd'], 2.5):,.0f},
           ${np.percentile(savings_results['cost_savings_usd'], 97.5):,.0f}]

Leak Detection:
  P(leak > 10%) = {(posterior_samples > 1.1).sum() / len(posterior_samples) * 100:.1f}%

NJ Utility Rates:
  Electricity: ${self.nj_electricity_rate:.2f}/kWh
  Natural Gas: ${self.nj_gas_rate:.2f}/therm
        """
        axes[1, 2].text(0.05, 0.5, summary_text, fontsize=10, verticalalignment='center',
                       family='monospace', bbox=dict(boxstyle='round', facecolor='lightblue',
                                                     alpha=0.3))

        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"   ✅ Saved: {output_file}")
        plt.close()


def main():
    """
    New Jersey Project - Fault Detection Analysis
    """
    print("=" * 80)
    print("NEW JERSEY BUILDING - FAULT DETECTION ANALYSIS")
    print("=" * 80)

    # ========================
    # CUSTOMIZE THESE SETTINGS
    # ========================

    # Building configuration
    building_name = "NJ Medium Office"
    idf_path = "sample_files/MediumOffice-90.1-2004.idf"  # Use your NJ building model

    # New Jersey weather file
    # Options:
    # - Newark: USA_NJ_Newark.Intl.AP.725020_TMY3.epw
    # - Atlantic City: USA_NJ_Atlantic.City.Intl.AP.724070_TMY3.epw
    # - Trenton: USA_NJ_McGuire.AFB.724096_TMY3.epw
    weather_file = "sample_files/USA_NJ_Newark.Intl.AP.725020_TMY3.epw"

    # Observed energy from utility bills (kWh/year)
    # Replace with actual annual consumption from NJ utility bills
    observed_energy_kwh = 750000  # Example: 750 MWh/year

    # Number of simulations for surrogate model (8-10 recommended)
    n_training_simulations = 8

    # ========================
    # END CUSTOMIZATION
    # ========================

    print(f"\n🏢 Project Configuration:")
    print(f"   Building: {building_name}")
    print(f"   Location: New Jersey")
    print(f"   Observed Energy: {observed_energy_kwh:,.0f} kWh/year")
    print(f"   Training Simulations: {n_training_simulations}")

    # Initialize detector
    detector = NewJerseyFaultDetector(
        idf_path=idf_path,
        weather_file=weather_file,
        building_name=building_name
    )

    # Step 1: Build surrogate model
    detector.build_surrogate(n_samples=n_training_simulations)

    # Step 2: Detect fault
    posterior_samples = detector.detect_fault(
        observed_energy_kwh=observed_energy_kwh,
        n_samples=1000
    )

    # Step 3: Counterfactual analysis
    savings_results = detector.counterfactual_savings(posterior_samples)

    # Step 4: Visualize
    detector.visualize(
        posterior_samples=posterior_samples,
        observed_energy=observed_energy_kwh,
        savings_results=savings_results,
        output_file="nj_fault_analysis.png"
    )

    # Save results
    savings_results.to_csv('nj_fault_results.csv', index=False)
    print(f"\n💾 Saved: nj_fault_results.csv")

    # Final recommendation
    print("\n" + "=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)

    mean_infiltration = posterior_samples.mean()
    mean_savings = savings_results['cost_savings_usd'].mean()
    leak_prob = (posterior_samples > 1.1).sum() / len(posterior_samples) * 100

    if mean_infiltration > 1.2:
        print(f"   ⚠️  MAJOR LEAK DETECTED")
        print(f"   Infiltration: {(mean_infiltration - 1) * 100:.0f}% above baseline")
        print(f"   Confidence: {leak_prob:.0f}% probability of leak > 10%")
        print(f"\n   💰 Annual Savings Potential: ${mean_savings:,.0f}")
        print(f"   ✅ RECOMMEND: Immediate air sealing / duct sealing retrofit")
        print(f"   📋 Next Steps:")
        print(f"      1. Schedule blower door test")
        print(f"      2. Conduct duct leakage testing")
        print(f"      3. Perform infrared thermography")
        print(f"      4. Seal identified leaks")
        print(f"      5. Re-test and verify savings")
    elif mean_infiltration > 1.1:
        print(f"   ⚠️  Moderate leak detected")
        print(f"   Infiltration: {(mean_infiltration - 1) * 100:.0f}% above baseline")
        print(f"   💰 Annual Savings Potential: ${mean_savings:,.0f}")
        print(f"   ✅ RECOMMEND: Schedule diagnostic testing")
    else:
        print(f"   ✅ No significant leak detected")
        print(f"   Building performance within expected range")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    main()
