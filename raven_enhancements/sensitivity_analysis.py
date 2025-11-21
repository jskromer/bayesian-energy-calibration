#!/usr/bin/env python3
"""
RAVEN-Inspired Sensitivity Analysis for Energy Calibration

Implements Sobol indices and variance-based sensitivity analysis
to identify which building parameters have the most impact on energy consumption.

Based on RAVEN's sensitivity analysis framework.
"""

import numpy as np
from SALib.sample import saltelli
from SALib.analyze import sobol
import pandas as pd
import matplotlib.pyplot as plt
from typing import Callable, Dict, List


class SensitivityAnalyzer:
    """
    Variance-based sensitivity analysis using Sobol indices

    Similar to RAVEN's sensitivity analysis module but specialized
    for building energy models.
    """

    def __init__(self, param_bounds: Dict[str, tuple], model_function: Callable):
        """
        Initialize sensitivity analyzer

        Args:
            param_bounds: Dict of {param_name: (lower, upper)}
            model_function: Function that takes param dict and returns energy (kWh)
        """
        self.param_bounds = param_bounds
        self.model_function = model_function
        self.param_names = list(param_bounds.keys())

        # Define problem for SALib
        self.problem = {
            'num_vars': len(self.param_names),
            'names': self.param_names,
            'bounds': [param_bounds[name] for name in self.param_names]
        }

        self.samples = None
        self.results = None
        self.sobol_indices = None

    def run_analysis(self, n_samples: int = 1024, calc_second_order: bool = True):
        """
        Run full sensitivity analysis

        Args:
            n_samples: Base sample size (actual = n_samples * (2*d + 2) for Saltelli)
            calc_second_order: Calculate 2nd order interaction indices

        Returns:
            Dict with first-order (S1), total-order (ST), and optionally second-order (S2)
        """
        print(f"🔍 Running Sobol Sensitivity Analysis")
        print(f"   Parameters: {self.param_names}")
        print(f"   Base samples: {n_samples}")

        # Generate Saltelli samples (quasi-random low-discrepancy)
        self.samples = saltelli.sample(
            self.problem,
            n_samples,
            calc_second_order=calc_second_order
        )

        total_samples = self.samples.shape[0]
        print(f"   Total model evaluations: {total_samples}")

        # Evaluate model for all samples
        print(f"   Evaluating model...")
        self.results = np.zeros(total_samples)

        for i, sample in enumerate(self.samples):
            # Convert to parameter dictionary
            params = dict(zip(self.param_names, sample))
            self.results[i] = self.model_function(params)

            if (i + 1) % 100 == 0:
                print(f"      Progress: {i+1}/{total_samples} ({100*(i+1)/total_samples:.1f}%)")

        # Compute Sobol indices
        print(f"   Computing Sobol indices...")
        self.sobol_indices = sobol.analyze(
            self.problem,
            self.results,
            calc_second_order=calc_second_order,
            print_to_console=False
        )

        return self.sobol_indices

    def plot_results(self, save_path: str = 'sensitivity_analysis.png'):
        """
        Create publication-quality sensitivity plots
        """
        if self.sobol_indices is None:
            raise ValueError("Run analysis first with run_analysis()")

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # 1. First-order indices (direct effect)
        s1 = self.sobol_indices['S1']
        s1_conf = self.sobol_indices['S1_conf']

        axes[0, 0].barh(self.param_names, s1, xerr=s1_conf, alpha=0.7, color='steelblue')
        axes[0, 0].set_xlabel('First-order Sobol Index (S1)')
        axes[0, 0].set_title('Direct Parameter Effects')
        axes[0, 0].set_xlim(0, 1)
        axes[0, 0].axvline(0.05, color='r', linestyle='--', alpha=0.3, label='5% threshold')
        axes[0, 0].legend()

        # 2. Total-order indices (total effect including interactions)
        st = self.sobol_indices['ST']
        st_conf = self.sobol_indices['ST_conf']

        axes[0, 1].barh(self.param_names, st, xerr=st_conf, alpha=0.7, color='darkorange')
        axes[0, 1].set_xlabel('Total-order Sobol Index (ST)')
        axes[0, 1].set_title('Total Effects (Direct + Interactions)')
        axes[0, 1].set_xlim(0, 1)

        # 3. Interaction effects (ST - S1)
        interactions = st - s1

        axes[1, 0].barh(self.param_names, interactions, alpha=0.7, color='green')
        axes[1, 0].set_xlabel('Interaction Index (ST - S1)')
        axes[1, 0].set_title('Parameter Interaction Effects')

        # 4. Parameter ranking
        importance_df = pd.DataFrame({
            'Parameter': self.param_names,
            'S1': s1,
            'ST': st,
            'Interactions': interactions
        }).sort_values('ST', ascending=True)

        y_pos = np.arange(len(self.param_names))
        axes[1, 1].barh(y_pos, importance_df['S1'], alpha=0.5, label='First-order', color='steelblue')
        axes[1, 1].barh(y_pos, importance_df['Interactions'], left=importance_df['S1'],
                       alpha=0.5, label='Interactions', color='green')
        axes[1, 1].set_yticks(y_pos)
        axes[1, 1].set_yticklabels(importance_df['Parameter'])
        axes[1, 1].set_xlabel('Sobol Index')
        axes[1, 1].set_title('Parameter Ranking (Stacked)')
        axes[1, 1].legend()

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\n💾 Sensitivity plots saved to: {save_path}")

    def get_summary_table(self) -> pd.DataFrame:
        """
        Get summary table of sensitivity indices

        Returns:
            DataFrame with S1, ST, and ranking
        """
        if self.sobol_indices is None:
            raise ValueError("Run analysis first with run_analysis()")

        df = pd.DataFrame({
            'Parameter': self.param_names,
            'S1 (Direct)': self.sobol_indices['S1'],
            'S1_conf': self.sobol_indices['S1_conf'],
            'ST (Total)': self.sobol_indices['ST'],
            'ST_conf': self.sobol_indices['ST_conf'],
            'Interactions': self.sobol_indices['ST'] - self.sobol_indices['S1']
        })

        # Add ranking
        df['Rank'] = df['ST (Total)'].rank(ascending=False).astype(int)

        # Sort by importance
        df = df.sort_values('ST (Total)', ascending=False)

        return df

    def identify_important_parameters(self, threshold: float = 0.05) -> List[str]:
        """
        Identify parameters with ST > threshold

        Args:
            threshold: Minimum total Sobol index to be considered important

        Returns:
            List of important parameter names
        """
        if self.sobol_indices is None:
            raise ValueError("Run analysis first with run_analysis()")

        st = self.sobol_indices['ST']
        important = [name for name, idx in zip(self.param_names, st) if idx > threshold]

        print(f"\n🎯 Important Parameters (ST > {threshold}):")
        for name in important:
            idx_val = st[self.param_names.index(name)]
            print(f"   {name:30s}: {idx_val:.3f}")

        return important


def example_usage_with_gp_surrogate():
    """
    Example: Use sensitivity analysis with GP surrogate instead of real simulations

    This is RAVEN-style: SA on surrogate, then focus calibration on important params
    """
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C

    print("=" * 80)
    print("EXAMPLE: SENSITIVITY ANALYSIS WITH GP SURROGATE")
    print("=" * 80)

    # Step 1: Define parameter space
    param_bounds = {
        'wall_r_value': (10, 20),
        'roof_r_value': (25, 40),
        'window_u_factor': (0.25, 0.45),
        'infiltration_ach': (0.2, 0.6),
        'heating_efficiency': (0.75, 0.95),
        'cooling_cop': (2.5, 4.0),
        'lighting_power_density': (0.5, 1.2),
        'occupant_count': (1, 4)
    }

    # Step 2: Train GP on initial LHS samples (would use real EnergyPlus here)
    print("\n📊 Step 1: Training GP surrogate on initial samples...")
    from scipy.stats import qmc

    n_initial = 50
    param_names = list(param_bounds.keys())
    sampler = qmc.LatinHypercube(d=len(param_names))
    samples = sampler.random(n=n_initial)

    # Scale to bounds
    X_train = np.zeros_like(samples)
    for i, (name, (lb, ub)) in enumerate(param_bounds.items()):
        X_train[:, i] = lb + samples[:, i] * (ub - lb)

    # Synthetic energy model (replace with real EnergyPlus)
    def synthetic_energy_model(params_array):
        """Simplified building energy model"""
        wall_r, roof_r, window_u, infil, heat_eff, cool_cop, lpd, occ = params_array

        # Heating load (inversely related to R-values, efficiency)
        heating = (2000 / wall_r + 1500 / roof_r + 300 * window_u) * (1 + infil * 0.2) / heat_eff

        # Cooling load
        cooling = (2000 / wall_r + 1500 / roof_r + 300 * window_u) * 0.5 / cool_cop

        # Internal loads
        internal = lpd * 2000 * 8760 / 1000 + occ * 1200

        return heating * 5000 + cooling * 2000 + internal

    y_train = np.array([synthetic_energy_model(x) for x in X_train])

    # Train GP
    kernel = C(1.0, (1e-3, 1e3)) * RBF([1.0] * len(param_names), (1e-2, 1e2))
    gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10, normalize_y=True)
    gp.fit(X_train, y_train)

    print(f"   ✅ GP trained on {n_initial} samples")
    print(f"   Energy range: {y_train.min():,.0f} - {y_train.max():,.0f} kWh/year")

    # Step 3: Run sensitivity analysis on GP surrogate (CHEAP!)
    print("\n🔍 Step 2: Running sensitivity analysis on GP surrogate...")

    def gp_model_function(params_dict):
        """Wrapper for GP prediction"""
        param_array = np.array([params_dict[name] for name in param_names])
        return gp.predict(param_array.reshape(1, -1))[0]

    analyzer = SensitivityAnalyzer(param_bounds, gp_model_function)
    sobol_indices = analyzer.run_analysis(n_samples=512)  # 512 * 18 = 9216 GP evals (fast!)

    # Step 4: Analyze results
    print("\n" + "=" * 80)
    print("SENSITIVITY ANALYSIS RESULTS")
    print("=" * 80)

    summary = analyzer.get_summary_table()
    print("\n" + summary.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    # Identify important parameters
    important_params = analyzer.identify_important_parameters(threshold=0.05)

    # Create plots
    analyzer.plot_results('raven_enhancements/sensitivity_analysis_example.png')

    print("\n" + "=" * 80)
    print("CALIBRATION RECOMMENDATIONS")
    print("=" * 80)
    print(f"\n🎯 Focus your Bayesian calibration on these {len(important_params)} parameters:")
    print(f"   {important_params}")
    print(f"\n💡 You can fix the unimportant parameters at their prior means")
    print(f"   This will reduce MCMC dimensionality and speed up convergence!")


if __name__ == "__main__":
    example_usage_with_gp_surrogate()
