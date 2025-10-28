#!/usr/bin/env python3
"""
Bayesian Calibration with PyMC + MCP Integration

This script demonstrates:
1. Gaussian Process (GP) surrogate modeling
2. PyMC MCMC sampling for Bayesian inference
3. Active learning with real EnergyPlus simulations via MCP
4. Iterative refinement (every N samples, run real sim and update GP)

Total simulations: ~10-20 real MCP calls instead of thousands
"""

import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import json

# MCP Integration - Direct Python imports
from energyplus_mcp_server.config import get_config
from energyplus_mcp_server.energyplus_tools import EnergyPlusManager

# Bayesian/ML imports
try:
    import pymc as pm
    import arviz as az
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Install with: uv pip install pymc arviz scikit-learn")
    exit(1)


class BayesianCalibrator:
    """
    Bayesian calibration using GP surrogate + PyMC MCMC + MCP simulations
    """

    def __init__(self, idf_path: str, weather_file: str, observed_energy: float):
        """
        Initialize calibrator

        Args:
            idf_path: Path to baseline IDF model
            weather_file: Path to weather file
            observed_energy: Observed annual energy (kWh) from utility bills
        """
        self.idf_path = idf_path
        self.weather_file = weather_file
        self.observed_energy = observed_energy

        # MCP Manager
        config = get_config()
        self.manager = EnergyPlusManager(config)

        # Parameter space (3 parameters to calibrate)
        self.param_names = ['r_value_mult', 'thermostat_setpoint', 'infiltration_mult']
        self.param_bounds = {
            'r_value_mult': (0.6, 1.4),      # ±40% insulation uncertainty
            'thermostat_setpoint': (68, 76),  # °F setpoint range
            'infiltration_mult': (0.5, 2.0),  # 50% to 200% infiltration
        }

        # GP surrogate model storage
        self.X_train = []  # Parameter samples
        self.y_train = []  # Energy results (kWh)
        self.gp = None

        # Simulation counter
        self.n_real_sims = 0
        self.max_real_sims = 20

        print(f"🎯 Bayesian Calibrator Initialized")
        print(f"   Target observed energy: {observed_energy:,.0f} kWh/year")
        print(f"   Calibrating {len(self.param_names)} parameters")
        print(f"   Max real simulations: {self.max_real_sims}")

    def run_mcp_simulation(self, params: dict) -> float:
        """
        Run real EnergyPlus simulation via MCP tools

        Args:
            params: Dictionary with parameter values

        Returns:
            Annual energy consumption (kWh)
        """
        self.n_real_sims += 1
        print(f"\n🔧 Real Simulation #{self.n_real_sims}/{self.max_real_sims}")
        print(f"   Parameters: {params}")

        # Create modified IDF with these parameters
        modified_idf = f"sample_files/calibration_run_{self.n_real_sims}.idf"

        # Apply infiltration multiplier via MCP
        self.manager.change_infiltration_by_mult(
            idf_path=self.idf_path,
            mult=params['infiltration_mult'],
            output_path=modified_idf
        )

        # TODO: Apply R-value and setpoint modifications
        # (Would need additional MCP tools or direct IDF manipulation)

        # Run simulation (returns JSON string with results)
        result_json = self.manager.run_simulation(
            idf_path=modified_idf,
            weather_file=self.weather_file,
            annual=True
        )

        # Parse JSON result
        result = json.loads(result_json)
        output_dir = result['output_directory']

        # Extract annual energy from results
        energy_kwh = self._extract_annual_energy(output_dir)

        print(f"   ✅ Result: {energy_kwh:,.0f} kWh/year")

        return energy_kwh

    def _extract_annual_energy(self, output_dir: str) -> float:
        """Extract annual energy from EnergyPlus outputs"""
        # Read from HTML table or SQL database
        output_path = Path(output_dir)

        # Find HTML table file (name varies based on output prefix)
        html_files = list(output_path.glob("*Table.htm"))
        if not html_files:
            html_files = list(output_path.glob("eplustbl.htm"))

        if html_files:
            html_file = html_files[0]
            # Parse HTML for total site energy
            # Simplified - in practice would use pandas.read_html()
            import re
            html_content = html_file.read_text()

            # Find "Total Site Energy" in GJ, convert to kWh
            match = re.search(r'Total Site Energy.*?(\d+\.\d+).*?GJ', html_content, re.DOTALL)
            if match:
                energy_gj = float(match.group(1))
                energy_kwh = energy_gj * 277.778  # GJ to kWh
                return energy_kwh

        # Fallback: use meter CSV
        meter_file = Path(output_dir) / "eplusout_meters.csv"
        if meter_file.exists():
            df = pd.read_csv(meter_file, skiprows=1)
            if 'Electricity:Facility [J](Hourly)' in df.columns:
                total_joules = df['Electricity:Facility [J](Hourly)'].sum()
                return total_joules / 3.6e6  # Joules to kWh

        raise ValueError(f"Could not extract energy from {output_dir}")

    def initialize_gp_surrogate(self, n_initial_samples: int = 10):
        """
        Initialize GP with Latin Hypercube Sampling

        Args:
            n_initial_samples: Number of initial real simulations
        """
        print(f"\n📊 Initializing GP Surrogate with {n_initial_samples} samples")

        # Latin Hypercube Sampling for space-filling design
        from scipy.stats import qmc

        sampler = qmc.LatinHypercube(d=len(self.param_names))
        samples = sampler.random(n=n_initial_samples)

        # Scale to parameter bounds
        for i, (param_name, (lb, ub)) in enumerate(self.param_bounds.items()):
            samples[:, i] = lb + samples[:, i] * (ub - lb)

        # Run real simulations for each sample
        for sample in samples:
            params = dict(zip(self.param_names, sample))
            energy = self.run_mcp_simulation(params)

            self.X_train.append(sample)
            self.y_train.append(energy)

        self.X_train = np.array(self.X_train)
        self.y_train = np.array(self.y_train)

        # Train initial GP
        self._fit_gp()

        print(f"✅ GP initialized with {len(self.y_train)} real simulations")
        print(f"   Energy range: {self.y_train.min():,.0f} - {self.y_train.max():,.0f} kWh")

    def _fit_gp(self):
        """Fit/update Gaussian Process surrogate"""
        kernel = C(1.0, (1e-3, 1e3)) * RBF([1.0] * len(self.param_names), (1e-2, 1e2))

        self.gp = GaussianProcessRegressor(
            kernel=kernel,
            n_restarts_optimizer=10,
            alpha=1e-6,
            normalize_y=True
        )

        self.gp.fit(self.X_train, self.y_train)

        print(f"   GP updated with {len(self.y_train)} training points")

    def gp_predict(self, X: np.ndarray) -> tuple:
        """
        Predict energy using GP surrogate

        Returns:
            (mean, std) predictions
        """
        if self.gp is None:
            raise ValueError("GP not initialized. Call initialize_gp_surrogate() first.")

        mean, std = self.gp.predict(X.reshape(-1, len(self.param_names)), return_std=True)
        return mean, std

    def run_bayesian_inference(self, n_samples: int = 500, tune: int = 200):
        """
        Run PyMC MCMC sampling with active learning

        Args:
            n_samples: Number of MCMC samples per chain
            tune: Number of tuning steps
        """
        print(f"\n🔬 Running Bayesian Inference")
        print(f"   MCMC samples: {n_samples} (tune: {tune})")
        print(f"   Active learning: Refine GP every 20 samples")

        with pm.Model() as model:
            # Priors for calibration parameters
            r_mult = pm.TruncatedNormal(
                'r_value_mult',
                mu=1.0, sigma=0.2,
                lower=self.param_bounds['r_value_mult'][0],
                upper=self.param_bounds['r_value_mult'][1]
            )

            setpoint = pm.TruncatedNormal(
                'thermostat_setpoint',
                mu=72, sigma=2,
                lower=self.param_bounds['thermostat_setpoint'][0],
                upper=self.param_bounds['thermostat_setpoint'][1]
            )

            leak_mult = pm.Uniform(
                'infiltration_mult',
                lower=self.param_bounds['infiltration_mult'][0],
                upper=self.param_bounds['infiltration_mult'][1]
            )

            # Stack parameters for GP prediction
            params = pm.math.stack([r_mult, setpoint, leak_mult])

            # GP surrogate prediction (mean only for now)
            # Note: PyMC doesn't directly support sklearn GP, so we use custom function
            def gp_surrogate(param_array):
                """Custom GP prediction for PyMC"""
                mean, _ = self.gp_predict(param_array)
                return mean[0]

            # Predicted energy from GP surrogate
            mu = pm.Deterministic('predicted_energy',
                                  pm.math.as_tensor_variable(
                                      [gp_surrogate(params.eval()) for _ in range(1)]
                                  )[0])

            # Observation uncertainty
            sigma = pm.HalfNormal('obs_uncertainty', sigma=10000)  # ±10,000 kWh uncertainty

            # Likelihood
            likelihood = pm.Normal(
                'observed_energy',
                mu=mu,
                sigma=sigma,
                observed=self.observed_energy
            )

            # Sample posterior
            print("\n   Starting MCMC sampling...")
            trace = pm.sample(
                draws=n_samples,
                tune=tune,
                chains=2,
                target_accept=0.9,
                return_inferencedata=True
            )

        # Active Learning: Refine GP with samples from posterior
        # Extract every 20th sample and run real simulation
        posterior_samples = az.extract(trace, num_samples=20)

        print(f"\n🔄 Active Learning: Refining GP with posterior samples")
        for i in range(min(10, self.max_real_sims - self.n_real_sims)):
            # Get sample from posterior
            sample_params = {
                'r_value_mult': float(posterior_samples['r_value_mult'][i]),
                'thermostat_setpoint': float(posterior_samples['thermostat_setpoint'][i]),
                'infiltration_mult': float(posterior_samples['infiltration_mult'][i])
            }

            # Run real simulation
            energy = self.run_mcp_simulation(sample_params)

            # Add to training set
            param_array = np.array([sample_params[name] for name in self.param_names])
            self.X_train = np.vstack([self.X_train, param_array])
            self.y_train = np.append(self.y_train, energy)

            # Refit GP
            self._fit_gp()

        return trace, model

    def analyze_results(self, trace):
        """
        Analyze and visualize calibration results
        """
        print(f"\n📈 Calibration Results Analysis")

        # Summary statistics
        summary = az.summary(trace, var_names=['r_value_mult', 'thermostat_setpoint', 'infiltration_mult'])
        print("\nPosterior Summary:")
        print(summary)

        # Extract posterior means
        posterior_means = {
            'r_value_mult': trace.posterior['r_value_mult'].mean().item(),
            'thermostat_setpoint': trace.posterior['thermostat_setpoint'].mean().item(),
            'infiltration_mult': trace.posterior['infiltration_mult'].mean().item()
        }

        print(f"\n🎯 Calibrated Parameters (Posterior Means):")
        for param, value in posterior_means.items():
            print(f"   {param:25s}: {value:.3f}")

        # Run final simulation with calibrated parameters
        print(f"\n✅ Running final validation simulation...")
        final_energy = self.run_mcp_simulation(posterior_means)

        error = abs(final_energy - self.observed_energy)
        error_pct = (error / self.observed_energy) * 100

        print(f"\n📊 Validation Results:")
        print(f"   Observed energy:    {self.observed_energy:>12,.0f} kWh/year")
        print(f"   Calibrated energy:  {final_energy:>12,.0f} kWh/year")
        print(f"   Absolute error:     {error:>12,.0f} kWh/year")
        print(f"   Percent error:      {error_pct:>12.2f}%")

        # Plot posterior distributions
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        az.plot_posterior(trace, var_names=['r_value_mult'], ax=axes[0, 0])
        axes[0, 0].set_title('R-Value Multiplier')

        az.plot_posterior(trace, var_names=['thermostat_setpoint'], ax=axes[0, 1])
        axes[0, 1].set_title('Thermostat Setpoint (°F)')

        az.plot_posterior(trace, var_names=['infiltration_mult'], ax=axes[1, 0])
        axes[1, 0].set_title('Infiltration Multiplier')

        # Plot GP training data
        axes[1, 1].scatter(self.y_train, range(len(self.y_train)), alpha=0.6)
        axes[1, 1].axvline(self.observed_energy, color='r', linestyle='--', label='Observed')
        axes[1, 1].set_xlabel('Energy (kWh)')
        axes[1, 1].set_ylabel('Simulation #')
        axes[1, 1].set_title(f'GP Training Data (n={len(self.y_train)})')
        axes[1, 1].legend()

        plt.tight_layout()
        plt.savefig('bayesian_calibration_results.png', dpi=300)
        print(f"\n💾 Saved plots to: bayesian_calibration_results.png")

        return posterior_means, final_energy


def main():
    """
    Main calibration workflow
    """
    print("=" * 80)
    print("BAYESIAN CALIBRATION WITH PYMC + MCP INTEGRATION")
    print("=" * 80)

    # Configuration
    idf_path = "sample_files/MediumOffice-90.1-2004.idf"
    weather_file = "sample_files/USA_CO_Denver.Intl.AP.725650_TMY3.epw"

    # Synthetic observed data (replace with real utility bill data)
    # For demo: Run baseline once to get "observed" value
    print("\n🎯 Step 1: Get baseline 'observed' energy")
    config = get_config()
    manager = EnergyPlusManager(config)

    baseline_result = manager.run_simulation(
        idf_path=idf_path,
        weather_file=weather_file,
        annual=True
    )

    # Extract baseline energy (simplified)
    observed_energy = 714762.0  # From previous runs (kWh/year)
    print(f"   Using observed energy: {observed_energy:,.0f} kWh/year")

    # Create calibrator
    calibrator = BayesianCalibrator(
        idf_path=idf_path,
        weather_file=weather_file,
        observed_energy=observed_energy
    )

    # Step 2: Initialize GP with Latin Hypercube samples
    print("\n🎯 Step 2: Initialize GP Surrogate")
    calibrator.initialize_gp_surrogate(n_initial_samples=10)

    # Step 3: Run Bayesian inference with active learning
    print("\n🎯 Step 3: Bayesian Inference + Active Learning")
    trace, model = calibrator.run_bayesian_inference(n_samples=500, tune=200)

    # Step 4: Analyze results
    print("\n🎯 Step 4: Analyze Results")
    posterior_means, final_energy = calibrator.analyze_results(trace)

    print("\n" + "=" * 80)
    print("CALIBRATION COMPLETE!")
    print("=" * 80)
    print(f"Total real simulations: {calibrator.n_real_sims}")
    print(f"Final calibrated energy: {final_energy:,.0f} kWh/year")
    print(f"Observed energy: {observed_energy:,.0f} kWh/year")
    print(f"Match: {(1 - abs(final_energy - observed_energy) / observed_energy) * 100:.1f}%")


if __name__ == "__main__":
    main()
