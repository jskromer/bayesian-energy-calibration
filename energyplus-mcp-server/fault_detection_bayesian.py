#!/usr/bin/env python3
"""
Fault Detection with Bayesian Analysis + MCP Integration

This script demonstrates:
1. Detect building faults using Bayesian calibration
2. ArviZ visualization of posterior distributions
3. Counterfactual analysis: What if we fix the fault?
4. Predict savings distribution with uncertainty quantification

Use case: Building has higher than expected energy use.
Question: Is there a duct leak? How much savings if we fix it?
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

# Bayesian/ML imports
ARVIZ_AVAILABLE = False
GP_AVAILABLE = False

try:
    import arviz as az
    import matplotlib.pyplot as plt
    ARVIZ_AVAILABLE = True
except ImportError:
    pass

try:
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
    GP_AVAILABLE = True
except ImportError:
    pass

if not GP_AVAILABLE:
    print("⚠️  scikit-learn not installed. Install with: uv pip install scikit-learn")
    print("   Continuing with simple linear interpolation...")

if not ARVIZ_AVAILABLE:
    print("⚠️  ArviZ not installed. Install with: uv pip install arviz matplotlib")
    print("   Visualizations will be skipped...")


class FaultDetector:
    """
    Detect and quantify building faults using Bayesian calibration
    """

    def __init__(self, idf_path: str, weather_file: str):
        self.idf_path = idf_path
        self.weather_file = weather_file

        # MCP Manager
        config = get_config()
        self.manager = EnergyPlusManager(config)

        # Training data
        self.X_train = []  # Parameter values
        self.y_train = []  # Energy results
        self.gp = None

        print(f"🔍 Fault Detector Initialized")
        print(f"   IDF: {idf_path}")
        print(f"   Weather: {weather_file}")

    def run_mcp_simulation(self, infiltration_mult: float, label: str = "") -> float:
        """
        Run EnergyPlus simulation via MCP with specified infiltration multiplier

        Args:
            infiltration_mult: Multiplier for infiltration (1.0 = baseline, >1.0 = leak)
            label: Description for logging

        Returns:
            Annual energy consumption (kWh)
        """
        print(f"\n🔧 Running Simulation: {label}")
        print(f"   Infiltration multiplier: {infiltration_mult:.2f}")

        # Create modified IDF
        modified_idf = f"sample_files/fault_detection_{infiltration_mult:.2f}.idf"

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
            match = re.search(r'Total Site Energy.*?(\d+\.\d+).*?GJ', html_content, re.DOTALL)
            if match:
                energy_gj = float(match.group(1))
                energy_kwh = energy_gj * 277.778

                print(f"   ✅ Energy: {energy_kwh:,.0f} kWh/year")
                return energy_kwh

        raise ValueError(f"Could not extract energy from {output_dir}")

    def build_surrogate_model(self, n_samples: int = 8):
        """
        Build GP surrogate by sampling parameter space

        Args:
            n_samples: Number of simulations to run
        """
        print(f"\n📊 Building GP Surrogate Model")
        print(f"   Running {n_samples} simulations...")

        # Sample infiltration multipliers from 0.5 to 2.0
        # (0.5 = very tight building, 2.0 = major leaks)
        infiltration_values = np.linspace(0.5, 2.0, n_samples)

        for i, infil_mult in enumerate(infiltration_values, 1):
            energy = self.run_mcp_simulation(
                infiltration_mult=infil_mult,
                label=f"Training sample {i}/{n_samples}"
            )

            self.X_train.append([infil_mult])
            self.y_train.append(energy)

        self.X_train = np.array(self.X_train)
        self.y_train = np.array(self.y_train)

        # Fit GP or use simple interpolation
        if GP_AVAILABLE:
            kernel = C(1.0, (1e-3, 1e3)) * RBF(1.0, (1e-2, 1e2))
            self.gp = GaussianProcessRegressor(
                kernel=kernel,
                n_restarts_optimizer=10,
                alpha=1e-6,
                normalize_y=True
            )
            self.gp.fit(self.X_train, self.y_train)
        else:
            # Simple linear interpolation as fallback
            self.gp = SimpleInterpolator(self.X_train, self.y_train)

        print(f"\n✅ GP Surrogate Model Built")
        print(f"   Training points: {len(self.y_train)}")
        print(f"   Energy range: {self.y_train.min():,.0f} - {self.y_train.max():,.0f} kWh/year")

    def bayesian_fault_detection(self, observed_energy: float, n_posterior_samples: int = 1000):
        """
        Use Bayesian inference to detect fault severity

        Args:
            observed_energy: Measured annual energy from utility bills (kWh)
            n_posterior_samples: Number of posterior samples to draw

        Returns:
            Posterior samples of infiltration multiplier
        """
        print(f"\n🎯 Bayesian Fault Detection")
        print(f"   Observed energy: {observed_energy:,.0f} kWh/year")
        print(f"   Generating posterior samples...")

        # Simple rejection sampling for posterior
        # Prior: Uniform(0.5, 2.0) on infiltration multiplier
        # Likelihood: Normal(GP_prediction, sigma) where sigma = observation noise

        prior_samples = np.random.uniform(0.5, 2.0, size=n_posterior_samples * 10)

        # Predict energy for each prior sample
        gp_predictions, gp_std = self.gp.predict(prior_samples.reshape(-1, 1), return_std=True)

        # Likelihood: how well does predicted energy match observed?
        observation_noise = 5000  # ±5,000 kWh measurement uncertainty
        likelihood = np.exp(-0.5 * ((gp_predictions - observed_energy) / observation_noise) ** 2)

        # Rejection sampling
        acceptance_prob = likelihood / likelihood.max()
        accepted = np.random.rand(len(prior_samples)) < acceptance_prob

        posterior_samples = prior_samples[accepted][:n_posterior_samples]

        print(f"   ✅ Generated {len(posterior_samples)} posterior samples")
        print(f"   Acceptance rate: {accepted.sum() / len(prior_samples) * 100:.1f}%")

        return posterior_samples

    def counterfactual_analysis(self, posterior_samples: np.ndarray, electricity_rate: float = 0.10):
        """
        Counterfactual: What if we fix the leak (set infiltration_mult = 1.0)?

        Args:
            posterior_samples: Posterior distribution of infiltration multiplier
            electricity_rate: $/kWh

        Returns:
            DataFrame with savings analysis
        """
        print(f"\n💡 Counterfactual Analysis: Fix the Leak")
        print(f"   Comparing current state vs. fixed building (infiltration_mult=1.0)")

        # Predict energy for current (faulty) state
        faulty_energy, faulty_std = self.gp.predict(
            posterior_samples.reshape(-1, 1),
            return_std=True
        )

        # Predict energy for fixed state (infiltration_mult = 1.0)
        fixed_samples = np.ones_like(posterior_samples)  # All set to 1.0
        fixed_energy, fixed_std = self.gp.predict(
            fixed_samples.reshape(-1, 1),
            return_std=True
        )

        # Calculate savings distribution
        energy_savings = faulty_energy - fixed_energy  # kWh/year
        cost_savings = energy_savings * electricity_rate  # $/year

        # Create results DataFrame
        results = pd.DataFrame({
            'infiltration_mult': posterior_samples,
            'faulty_energy_kwh': faulty_energy,
            'fixed_energy_kwh': fixed_energy,
            'energy_savings_kwh': energy_savings,
            'cost_savings_usd': cost_savings
        })

        # Summary statistics
        print(f"\n📊 Savings Distribution Summary:")
        print(f"   Energy Savings:")
        print(f"      Mean:   {energy_savings.mean():>10,.0f} kWh/year")
        print(f"      Median: {np.median(energy_savings):>10,.0f} kWh/year")
        print(f"      95% CI: [{np.percentile(energy_savings, 2.5):>8,.0f}, {np.percentile(energy_savings, 97.5):>8,.0f}] kWh/year")

        print(f"\n   Cost Savings (@ ${electricity_rate:.2f}/kWh):")
        print(f"      Mean:   ${cost_savings.mean():>10,.2f}/year")
        print(f"      Median: ${np.median(cost_savings):>10,.2f}/year")
        print(f"      95% CI: [${np.percentile(cost_savings, 2.5):>8,.2f}, ${np.percentile(cost_savings, 97.5):>8,.2f}]/year")

        # Probability that leak exists (infiltration_mult > 1.1)
        leak_prob = (posterior_samples > 1.1).sum() / len(posterior_samples) * 100
        print(f"\n   Probability of significant leak (>10%): {leak_prob:.1f}%")

        return results

    def visualize_results(self, posterior_samples: np.ndarray, observed_energy: float,
                         counterfactual_results: pd.DataFrame):
        """
        Create ArviZ-style visualizations

        Args:
            posterior_samples: Posterior distribution of infiltration multiplier
            observed_energy: Observed annual energy
            counterfactual_results: Results from counterfactual analysis
        """
        if not ARVIZ_AVAILABLE:
            print("⚠️  ArviZ not available, skipping visualization")
            return

        print(f"\n📈 Creating Visualizations...")

        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # 1. Posterior distribution of infiltration multiplier
        ax1 = fig.add_subplot(gs[0, :2])
        ax1.hist(posterior_samples, bins=30, color='steelblue', alpha=0.7, density=True)
        ax1.axvline(1.0, color='green', linestyle='--', linewidth=2, label='No leak (1.0)')
        ax1.axvline(posterior_samples.mean(), color='red', linestyle='--', linewidth=2,
                   label=f'Posterior mean ({posterior_samples.mean():.2f})')
        ax1.set_xlabel('Infiltration Multiplier', fontsize=12)
        ax1.set_ylabel('Probability Density', fontsize=12)
        ax1.set_title('Posterior Distribution: Infiltration Multiplier', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(alpha=0.3)

        # 2. GP surrogate model with uncertainty
        ax2 = fig.add_subplot(gs[0, 2])
        x_plot = np.linspace(0.5, 2.0, 100).reshape(-1, 1)
        y_pred, y_std = self.gp.predict(x_plot, return_std=True)

        ax2.plot(x_plot, y_pred, 'b-', label='GP mean', linewidth=2)
        ax2.fill_between(x_plot.ravel(), y_pred - 2*y_std, y_pred + 2*y_std,
                        alpha=0.3, color='blue', label='95% CI')
        ax2.scatter(self.X_train, self.y_train, c='red', s=50, zorder=10, label='Training data')
        ax2.axhline(observed_energy, color='green', linestyle='--', linewidth=2, label='Observed')
        ax2.set_xlabel('Infiltration Mult', fontsize=10)
        ax2.set_ylabel('Energy (kWh)', fontsize=10)
        ax2.set_title('GP Surrogate Model', fontsize=12, fontweight='bold')
        ax2.legend(fontsize=8)
        ax2.grid(alpha=0.3)

        # 3. Energy savings distribution
        ax3 = fig.add_subplot(gs[1, :2])
        ax3.hist(counterfactual_results['energy_savings_kwh'], bins=30, color='orange', alpha=0.7, density=True)
        ax3.axvline(0, color='red', linestyle='--', linewidth=2, label='No savings')
        ax3.axvline(counterfactual_results['energy_savings_kwh'].mean(),
                   color='green', linestyle='--', linewidth=2,
                   label=f'Mean: {counterfactual_results["energy_savings_kwh"].mean():,.0f} kWh/yr')
        ax3.set_xlabel('Energy Savings (kWh/year)', fontsize=12)
        ax3.set_ylabel('Probability Density', fontsize=12)
        ax3.set_title('Counterfactual: Energy Savings if Leak Fixed', fontsize=14, fontweight='bold')
        ax3.legend()
        ax3.grid(alpha=0.3)

        # 4. Cost savings distribution
        ax4 = fig.add_subplot(gs[1, 2])
        ax4.hist(counterfactual_results['cost_savings_usd'], bins=30, color='green', alpha=0.7, density=True)
        ax4.set_xlabel('Cost Savings ($/year)', fontsize=10)
        ax4.set_ylabel('Probability Density', fontsize=10)
        ax4.set_title('Annual Cost Savings', fontsize=12, fontweight='bold')
        ax4.grid(alpha=0.3)

        # 5. Scatter: Infiltration vs Energy
        ax5 = fig.add_subplot(gs[2, 0])
        ax5.scatter(counterfactual_results['infiltration_mult'],
                   counterfactual_results['faulty_energy_kwh'],
                   alpha=0.5, s=10, color='red', label='Faulty')
        ax5.axhline(observed_energy, color='blue', linestyle='--', linewidth=2, label='Observed')
        ax5.set_xlabel('Infiltration Mult', fontsize=10)
        ax5.set_ylabel('Energy (kWh)', fontsize=10)
        ax5.set_title('Faulty Building Energy', fontsize=12, fontweight='bold')
        ax5.legend()
        ax5.grid(alpha=0.3)

        # 6. Scatter: Infiltration vs Savings
        ax6 = fig.add_subplot(gs[2, 1])
        ax6.scatter(counterfactual_results['infiltration_mult'],
                   counterfactual_results['energy_savings_kwh'],
                   alpha=0.5, s=10, color='orange')
        ax6.axhline(0, color='red', linestyle='--', linewidth=1)
        ax6.set_xlabel('Infiltration Mult', fontsize=10)
        ax6.set_ylabel('Savings (kWh)', fontsize=10)
        ax6.set_title('Savings vs Leak Severity', fontsize=12, fontweight='bold')
        ax6.grid(alpha=0.3)

        # 7. Summary statistics table
        ax7 = fig.add_subplot(gs[2, 2])
        ax7.axis('off')

        summary_text = f"""
FAULT DETECTION SUMMARY

Infiltration Multiplier:
  Mean:   {posterior_samples.mean():.3f}
  Median: {np.median(posterior_samples):.3f}
  95% CI: [{np.percentile(posterior_samples, 2.5):.3f},
           {np.percentile(posterior_samples, 97.5):.3f}]

Energy Savings Potential:
  Mean:   {counterfactual_results['energy_savings_kwh'].mean():,.0f} kWh/yr
  Median: {counterfactual_results['energy_savings_kwh'].median():,.0f} kWh/yr

Cost Savings Potential:
  Mean:   ${counterfactual_results['cost_savings_usd'].mean():,.0f}/yr
  Median: ${counterfactual_results['cost_savings_usd'].median():,.0f}/yr

Leak Probability:
  P(infiltration > 1.1) = {(posterior_samples > 1.1).sum() / len(posterior_samples) * 100:.1f}%
        """

        ax7.text(0.1, 0.5, summary_text, fontsize=10, verticalalignment='center',
                family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        plt.suptitle('Bayesian Fault Detection & Counterfactual Analysis',
                    fontsize=16, fontweight='bold', y=0.995)

        # Save figure
        output_file = 'fault_detection_analysis.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"   ✅ Saved visualization: {output_file}")

        plt.close()


def main():
    """
    Main workflow: Detect fault, quantify severity, estimate savings
    """
    print("=" * 80)
    print("BAYESIAN FAULT DETECTION WITH MCP INTEGRATION")
    print("=" * 80)

    # Configuration
    idf_path = "sample_files/MediumOffice-90.1-2004.idf"
    weather_file = "sample_files/USA_CO_Denver.Intl.AP.725650_TMY3.epw"

    # Simulated "observed" energy (higher than baseline, suggests a leak)
    # In reality, this would come from utility bills
    observed_energy = 750000  # kWh/year (higher than baseline ~715k)

    electricity_rate = 0.12  # $/kWh

    print(f"\n🏢 Building Information:")
    print(f"   IDF Model: {idf_path}")
    print(f"   Weather: {weather_file}")
    print(f"   Observed annual energy: {observed_energy:,.0f} kWh/year")
    print(f"   Electricity rate: ${electricity_rate:.2f}/kWh")

    # Initialize detector
    detector = FaultDetector(idf_path, weather_file)

    # Step 1: Build GP surrogate model
    detector.build_surrogate_model(n_samples=8)

    # Step 2: Bayesian fault detection
    posterior_samples = detector.bayesian_fault_detection(
        observed_energy=observed_energy,
        n_posterior_samples=1000
    )

    # Step 3: Counterfactual analysis
    counterfactual_results = detector.counterfactual_analysis(
        posterior_samples=posterior_samples,
        electricity_rate=electricity_rate
    )

    # Step 4: Visualize results
    detector.visualize_results(
        posterior_samples=posterior_samples,
        observed_energy=observed_energy,
        counterfactual_results=counterfactual_results
    )

    # Save detailed results
    output_csv = 'fault_detection_results.csv'
    counterfactual_results.to_csv(output_csv, index=False)
    print(f"\n💾 Saved detailed results: {output_csv}")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)

    # Final recommendation
    mean_savings = counterfactual_results['cost_savings_usd'].mean()
    leak_severity = posterior_samples.mean()

    print(f"\n💡 RECOMMENDATION:")
    if leak_severity > 1.2:
        print(f"   ⚠️  MAJOR LEAK DETECTED (infiltration {(leak_severity - 1)*100:.0f}% above baseline)")
        print(f"   💰 Expected annual savings if fixed: ${mean_savings:,.0f}")
        print(f"   ✅ RECOMMEND: Immediate duct sealing / air sealing retrofit")
    elif leak_severity > 1.1:
        print(f"   ⚠️  Moderate leak detected (infiltration {(leak_severity - 1)*100:.0f}% above baseline)")
        print(f"   💰 Expected annual savings if fixed: ${mean_savings:,.0f}")
        print(f"   ✅ RECOMMEND: Schedule duct leakage testing and sealing")
    else:
        print(f"   ✅ No significant leak detected")
        print(f"   💰 Minimal savings potential: ${mean_savings:,.0f}")
        print(f"   ℹ️  Building performance within expected range")


if __name__ == "__main__":
    main()
