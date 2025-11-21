#!/usr/bin/env python3
"""
RAVEN-Inspired Adaptive Sampling Strategies

RAVEN's adaptive sampling sequentially selects new sample points based on:
1. High prediction uncertainty (exploration)
2. Proximity to observed data (exploitation)
3. Expected improvement (optimization-focused)

This is more sophisticated than your current "every N samples" approach.
"""

import numpy as np
from scipy.stats import norm
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
from typing import Callable, Dict, Tuple, List
import matplotlib.pyplot as plt


class AdaptiveSampler:
    """
    Adaptive sampling for expensive simulations

    Strategies:
    1. Maximum Uncertainty Sampling (exploration)
    2. Expected Improvement (optimization)
    3. Probability of Improvement (optimization)
    4. Upper Confidence Bound (exploration-exploitation tradeoff)
    """

    def __init__(self, param_bounds: Dict[str, Tuple[float, float]],
                 simulator: Callable, max_iterations: int = 20):
        """
        Initialize adaptive sampler

        Args:
            param_bounds: {param_name: (lower, upper)}
            simulator: Function(params_dict) -> energy (kWh)
            max_iterations: Maximum number of adaptive samples
        """
        self.param_bounds = param_bounds
        self.param_names = list(param_bounds.keys())
        self.simulator = simulator
        self.max_iterations = max_iterations

        # Training data
        self.X_train = []
        self.y_train = []

        # GP surrogate
        self.gp = None

        # Best observed value
        self.y_best = None

    def initialize_lhs(self, n_initial: int = 10):
        """
        Initialize with Latin Hypercube Sampling

        Args:
            n_initial: Number of initial samples
        """
        print(f"🎲 Initializing with LHS ({n_initial} samples)...")

        from scipy.stats import qmc
        sampler = qmc.LatinHypercube(d=len(self.param_names))
        samples = sampler.random(n=n_initial)

        # Scale to bounds
        for i, (name, (lb, ub)) in enumerate(self.param_bounds.items()):
            samples[:, i] = lb + samples[:, i] * (ub - lb)

        # Run simulations
        for sample in samples:
            params = dict(zip(self.param_names, sample))
            energy = self.simulator(params)

            self.X_train.append(sample)
            self.y_train.append(energy)

        self.X_train = np.array(self.X_train)
        self.y_train = np.array(self.y_train)
        self.y_best = self.y_train.min()  # Assuming minimization

        # Fit initial GP
        self._update_gp()

        print(f"   ✅ Initialized with {n_initial} samples")
        print(f"   Energy range: {self.y_train.min():,.0f} - {self.y_train.max():,.0f} kWh")

    def _update_gp(self):
        """Update GP surrogate with current training data"""
        kernel = C(1.0, (1e-3, 1e3)) * RBF([1.0] * len(self.param_names), (1e-2, 1e2))
        self.gp = GaussianProcessRegressor(
            kernel=kernel,
            n_restarts_optimizer=10,
            alpha=1e-6,
            normalize_y=True
        )
        self.gp.fit(self.X_train, self.y_train)

    def acquisition_max_uncertainty(self, X_candidates: np.ndarray) -> int:
        """
        Maximum Uncertainty Sampling (pure exploration)

        Select point with highest GP prediction variance
        """
        _, std = self.gp.predict(X_candidates, return_std=True)
        return std.argmax()

    def acquisition_expected_improvement(self, X_candidates: np.ndarray, xi: float = 0.01) -> int:
        """
        Expected Improvement (EI) - classic Bayesian optimization

        Args:
            X_candidates: Candidate points
            xi: Exploration parameter (default 0.01)

        Returns:
            Index of best candidate
        """
        mu, sigma = self.gp.predict(X_candidates, return_std=True)

        # Compute EI
        with np.errstate(divide='warn'):
            improvement = self.y_best - mu - xi
            Z = improvement / sigma
            ei = improvement * norm.cdf(Z) + sigma * norm.pdf(Z)
            ei[sigma == 0.0] = 0.0

        return ei.argmax()

    def acquisition_ucb(self, X_candidates: np.ndarray, kappa: float = 2.0) -> int:
        """
        Upper Confidence Bound (UCB)

        Args:
            X_candidates: Candidate points
            kappa: Exploration-exploitation tradeoff (higher = more exploration)

        Returns:
            Index of best candidate
        """
        mu, sigma = self.gp.predict(X_candidates, return_std=True)

        # UCB = mean - kappa * std (negative because we minimize)
        ucb = mu - kappa * sigma

        return ucb.argmin()

    def run_adaptive_sampling(self, strategy: str = 'ei', n_candidates: int = 1000):
        """
        Run adaptive sampling loop

        Args:
            strategy: 'uncertainty', 'ei', 'ucb'
            n_candidates: Number of random candidates to evaluate acquisition on
        """
        print(f"\n🔄 Running Adaptive Sampling ({strategy.upper()} strategy)")
        print(f"   Max iterations: {self.max_iterations}")
        print(f"   Current best: {self.y_best:,.0f} kWh")

        for iteration in range(self.max_iterations):
            print(f"\n   Iteration {iteration + 1}/{self.max_iterations}")

            # Generate random candidate points
            candidates = []
            for _ in range(n_candidates):
                candidate = []
                for name, (lb, ub) in self.param_bounds.items():
                    candidate.append(np.random.uniform(lb, ub))
                candidates.append(candidate)
            X_candidates = np.array(candidates)

            # Select next point using acquisition function
            if strategy == 'uncertainty':
                next_idx = self.acquisition_max_uncertainty(X_candidates)
            elif strategy == 'ei':
                next_idx = self.acquisition_expected_improvement(X_candidates)
            elif strategy == 'ucb':
                next_idx = self.acquisition_ucb(X_candidates)
            else:
                raise ValueError(f"Unknown strategy: {strategy}")

            next_point = X_candidates[next_idx]

            # Run simulation at selected point
            params = dict(zip(self.param_names, next_point))
            energy = self.simulator(params)

            print(f"      Selected: {params}")
            print(f"      Energy: {energy:,.0f} kWh")

            # Update training data
            self.X_train = np.vstack([self.X_train, next_point])
            self.y_train = np.append(self.y_train, energy)

            # Update best
            if energy < self.y_best:
                self.y_best = energy
                print(f"      ✨ New best: {self.y_best:,.0f} kWh")

            # Update GP
            self._update_gp()

        print(f"\n✅ Adaptive sampling complete")
        print(f"   Final best: {self.y_best:,.0f} kWh")
        print(f"   Total simulations: {len(self.y_train)}")

    def get_best_parameters(self) -> Dict[str, float]:
        """
        Get best parameter set found

        Returns:
            Dict of best parameters
        """
        best_idx = self.y_train.argmin()
        best_params = dict(zip(self.param_names, self.X_train[best_idx]))
        return best_params

    def plot_convergence(self, save_path: str = 'adaptive_sampling_convergence.png'):
        """
        Plot convergence of best observed value
        """
        # Compute running minimum
        running_min = np.minimum.accumulate(self.y_train)

        fig, axes = plt.subplots(1, 2, figsize=(12, 4))

        # 1. Convergence plot
        axes[0].plot(running_min, 'o-', linewidth=2, markersize=5)
        axes[0].set_xlabel('Simulation Number')
        axes[0].set_ylabel('Best Energy (kWh)')
        axes[0].set_title('Convergence of Best Observed Value')
        axes[0].grid(alpha=0.3)

        # 2. All observations
        axes[1].scatter(range(len(self.y_train)), self.y_train, alpha=0.6, s=50)
        axes[1].plot(running_min, 'r-', linewidth=2, label='Best so far')
        axes[1].set_xlabel('Simulation Number')
        axes[1].set_ylabel('Energy (kWh)')
        axes[1].set_title('All Observations')
        axes[1].legend()
        axes[1].grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\n💾 Convergence plot saved to: {save_path}")


def compare_sampling_strategies():
    """
    Compare different adaptive sampling strategies
    """
    print("=" * 80)
    print("COMPARISON: ADAPTIVE SAMPLING STRATEGIES")
    print("=" * 80)

    # Define test problem
    param_bounds = {
        'wall_r': (10, 20),
        'window_u': (0.25, 0.45),
        'infiltration': (0.2, 0.6),
    }

    # Synthetic energy model with true optimum
    def energy_simulator(params):
        """Energy model with known optimum at wall_r=18, window_u=0.28, infiltration=0.25"""
        wall_r = params['wall_r']
        window_u = params['window_u']
        infiltration = params['infiltration']

        # Quadratic bowl centered at optimum
        energy = (
            100 * (wall_r - 18)**2 +
            50000 * (window_u - 0.28)**2 +
            20000 * (infiltration - 0.25)**2 +
            50000  # Base energy
        )

        # Add noise
        energy += np.random.normal(0, 500)

        return energy

    true_optimum = energy_simulator({
        'wall_r': 18.0,
        'window_u': 0.28,
        'infiltration': 0.25
    })

    print(f"\n🎯 True optimum energy: {true_optimum:,.0f} kWh (approx)")

    # Test each strategy
    strategies = ['uncertainty', 'ei', 'ucb']
    results = {}

    for strategy in strategies:
        print(f"\n{'=' * 80}")
        print(f"Testing: {strategy.upper()}")
        print(f"{'=' * 80}")

        sampler = AdaptiveSampler(
            param_bounds=param_bounds,
            simulator=energy_simulator,
            max_iterations=15
        )

        sampler.initialize_lhs(n_initial=5)
        sampler.run_adaptive_sampling(strategy=strategy, n_candidates=500)

        best_params = sampler.get_best_parameters()
        best_energy = sampler.y_best

        results[strategy] = {
            'best_energy': best_energy,
            'best_params': best_params,
            'n_simulations': len(sampler.y_train)
        }

        print(f"\n📊 Results for {strategy.upper()}:")
        print(f"   Best energy: {best_energy:,.0f} kWh")
        print(f"   Best params: {best_params}")
        print(f"   Error from true opt: {abs(best_energy - true_optimum):,.0f} kWh")

    # Summary comparison
    print("\n" + "=" * 80)
    print("STRATEGY COMPARISON SUMMARY")
    print("=" * 80)

    for strategy, result in results.items():
        error = abs(result['best_energy'] - true_optimum)
        print(f"\n{strategy.upper():15s}:")
        print(f"   Best found:  {result['best_energy']:>12,.0f} kWh")
        print(f"   Error:       {error:>12,.0f} kWh ({100*error/true_optimum:.1f}%)")

    print("\n💡 RECOMMENDATION:")
    print("   • Use 'EI' (Expected Improvement) for optimization/calibration")
    print("   • Use 'uncertainty' for pure exploration (sensitivity analysis)")
    print("   • Use 'UCB' for good balance (default kappa=2)")


if __name__ == "__main__":
    compare_sampling_strategies()
