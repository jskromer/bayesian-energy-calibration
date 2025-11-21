#!/usr/bin/env python3
"""
RAVEN-Inspired Time-Series Analysis for Energy Data

RAVEN includes time-series capabilities for analyzing dynamic system behavior.
This module adapts those concepts for building energy time-series:
- Hourly/monthly patterns
- Autocorrelation analysis
- Anomaly detection
- Forecast uncertainty
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from typing import List, Tuple, Dict
import warnings
warnings.filterwarnings('ignore')


class TimeSeriesAnalyzer:
    """
    Time-series analysis for building energy data

    Features:
    - Statistical decomposition (trend, seasonal, residual)
    - Autocorrelation analysis
    - Uncertainty quantification over time
    - Anomaly detection
    """

    def __init__(self, timestamps: List, energy_data: np.ndarray):
        """
        Initialize analyzer

        Args:
            timestamps: List of timestamps (monthly/hourly)
            energy_data: Energy consumption array (n_samples, n_timesteps)
                        Can be posterior samples from Bayesian calibration
        """
        self.timestamps = pd.to_datetime(timestamps) if not isinstance(timestamps[0], pd.Timestamp) else timestamps
        self.energy_data = energy_data

        # If 1D, convert to 2D
        if len(energy_data.shape) == 1:
            self.energy_data = energy_data.reshape(1, -1)

        self.n_samples, self.n_timesteps = self.energy_data.shape

    def compute_statistics(self) -> pd.DataFrame:
        """
        Compute time-varying statistics (mean, std, percentiles)

        Returns:
            DataFrame with time-varying statistics
        """
        df = pd.DataFrame({
            'timestamp': self.timestamps,
            'mean': self.energy_data.mean(axis=0),
            'std': self.energy_data.std(axis=0),
            'median': np.median(self.energy_data, axis=0),
            'q025': np.percentile(self.energy_data, 2.5, axis=0),
            'q975': np.percentile(self.energy_data, 97.5, axis=0),
        })

        return df

    def analyze_autocorrelation(self, max_lag: int = 12) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute autocorrelation function (ACF)

        Useful for identifying temporal dependencies in residuals

        Args:
            max_lag: Maximum lag to compute

        Returns:
            (lags, acf_values)
        """
        # Use mean trajectory
        mean_energy = self.energy_data.mean(axis=0)

        # Compute ACF
        lags = np.arange(max_lag + 1)
        acf = np.zeros(max_lag + 1)

        for lag in lags:
            if lag == 0:
                acf[lag] = 1.0
            else:
                c0 = np.var(mean_energy)
                c_lag = np.corrcoef(mean_energy[:-lag], mean_energy[lag:])[0, 1]
                acf[lag] = c_lag

        return lags, acf

    def detect_anomalies(self, threshold: float = 3.0) -> List[int]:
        """
        Detect anomalous timesteps using z-score

        Args:
            threshold: Z-score threshold for anomaly detection

        Returns:
            List of anomalous timestep indices
        """
        mean_energy = self.energy_data.mean(axis=0)

        # Compute z-scores
        z_scores = np.abs(stats.zscore(mean_energy))

        # Find anomalies
        anomalies = np.where(z_scores > threshold)[0]

        return anomalies.tolist()

    def decompose_seasonal(self, period: int = 12) -> Dict[str, np.ndarray]:
        """
        Simple seasonal decomposition (additive model)

        Energy = Trend + Seasonal + Residual

        Args:
            period: Seasonal period (12 for monthly)

        Returns:
            Dict with 'trend', 'seasonal', 'residual' components
        """
        from scipy.ndimage import uniform_filter1d

        mean_energy = self.energy_data.mean(axis=0)

        # Trend (moving average)
        trend = uniform_filter1d(mean_energy, size=period, mode='nearest')

        # Detrended
        detrended = mean_energy - trend

        # Seasonal (average by month)
        seasonal = np.zeros(self.n_timesteps)
        for i in range(period):
            indices = np.arange(i, self.n_timesteps, period)
            seasonal[indices] = detrended[indices].mean()

        # Residual
        residual = mean_energy - trend - seasonal

        return {
            'trend': trend,
            'seasonal': seasonal,
            'residual': residual,
            'original': mean_energy
        }

    def plot_uncertainty_bands(self, observed_data: np.ndarray = None,
                               save_path: str = 'time_series_uncertainty.png'):
        """
        Plot time series with uncertainty bands

        Args:
            observed_data: Optional observed data to overlay
            save_path: Path to save plot
        """
        stats_df = self.compute_statistics()

        fig, axes = plt.subplots(2, 1, figsize=(12, 8))

        # Plot 1: Mean with 95% CI
        axes[0].fill_between(
            stats_df['timestamp'],
            stats_df['q025'],
            stats_df['q975'],
            alpha=0.3,
            color='steelblue',
            label='95% Credible Interval'
        )
        axes[0].plot(stats_df['timestamp'], stats_df['mean'], 'b-', linewidth=2, label='Mean')

        if observed_data is not None:
            axes[0].plot(stats_df['timestamp'], observed_data, 'ro-', linewidth=1,
                        markersize=4, label='Observed', alpha=0.7)

        axes[0].set_ylabel('Energy (kWh)')
        axes[0].set_title('Energy Consumption with Uncertainty')
        axes[0].legend()
        axes[0].grid(alpha=0.3)

        # Plot 2: Uncertainty evolution
        axes[1].plot(stats_df['timestamp'], stats_df['std'], 'g-', linewidth=2)
        axes[1].fill_between(stats_df['timestamp'], 0, stats_df['std'], alpha=0.3, color='green')
        axes[1].set_xlabel('Time')
        axes[1].set_ylabel('Std Dev (kWh)')
        axes[1].set_title('Prediction Uncertainty Over Time')
        axes[1].grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"💾 Time-series plot saved to: {save_path}")

    def plot_decomposition(self, save_path: str = 'seasonal_decomposition.png'):
        """
        Plot seasonal decomposition
        """
        decomp = self.decompose_seasonal(period=12)

        fig, axes = plt.subplots(4, 1, figsize=(12, 10))

        # Original
        axes[0].plot(self.timestamps, decomp['original'], 'k-', linewidth=1.5)
        axes[0].set_ylabel('Energy (kWh)')
        axes[0].set_title('Original Time Series')
        axes[0].grid(alpha=0.3)

        # Trend
        axes[1].plot(self.timestamps, decomp['trend'], 'b-', linewidth=2)
        axes[1].set_ylabel('Energy (kWh)')
        axes[1].set_title('Trend Component')
        axes[1].grid(alpha=0.3)

        # Seasonal
        axes[2].plot(self.timestamps, decomp['seasonal'], 'g-', linewidth=2)
        axes[2].set_ylabel('Energy (kWh)')
        axes[2].set_title('Seasonal Component')
        axes[2].grid(alpha=0.3)

        # Residual
        axes[3].plot(self.timestamps, decomp['residual'], 'r-', linewidth=1, alpha=0.7)
        axes[3].axhline(0, color='k', linestyle='--', alpha=0.5)
        axes[3].set_xlabel('Time')
        axes[3].set_ylabel('Energy (kWh)')
        axes[3].set_title('Residual Component')
        axes[3].grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"💾 Decomposition plot saved to: {save_path}")


def example_bayesian_time_series():
    """
    Example: Analyze posterior monthly energy predictions
    """
    print("=" * 80)
    print("TIME-SERIES ANALYSIS FOR BAYESIAN ENERGY CALIBRATION")
    print("=" * 80)

    # Simulate posterior samples of monthly energy
    months = pd.date_range('2023-01-01', periods=12, freq='MS')

    # True seasonal pattern
    seasonal_factors = np.array([1.4, 1.3, 1.1, 0.9, 0.8, 0.9, 1.1, 1.0, 0.8, 0.9, 1.1, 1.3])
    base_energy = 1500

    # Generate posterior samples (e.g., from PyMC)
    n_samples = 1000
    posterior_monthly = []

    for _ in range(n_samples):
        # Each sample: different parameters -> different monthly energy
        param_uncertainty = np.random.normal(1.0, 0.05)  # ±5% parameter uncertainty
        monthly = base_energy * seasonal_factors * param_uncertainty

        # Add month-specific uncertainty
        monthly += np.random.normal(0, 50, size=12)

        posterior_monthly.append(monthly)

    posterior_monthly = np.array(posterior_monthly)

    print(f"\n📊 Posterior samples: {n_samples}")
    print(f"   Time steps: {len(months)}")

    # Synthetic observed data
    observed = base_energy * seasonal_factors + np.random.normal(0, 75, size=12)

    # Analyze
    analyzer = TimeSeriesAnalyzer(months, posterior_monthly)

    # Statistics
    print("\n" + "=" * 80)
    print("TIME-VARYING STATISTICS")
    print("=" * 80)

    stats_df = analyzer.compute_statistics()
    print("\n" + stats_df.to_string(index=False, float_format=lambda x: f"{x:.1f}"))

    # Autocorrelation
    print("\n" + "=" * 80)
    print("AUTOCORRELATION ANALYSIS")
    print("=" * 80)

    lags, acf = analyzer.analyze_autocorrelation(max_lag=6)
    print("\nACF (residuals):")
    for lag, acf_val in zip(lags, acf):
        print(f"   Lag {lag:2d}: {acf_val:>6.3f}")

    # Anomalies
    print("\n" + "=" * 80)
    print("ANOMALY DETECTION")
    print("=" * 80)

    anomalies = analyzer.detect_anomalies(threshold=2.5)
    if anomalies:
        print(f"\n⚠️  Anomalous months detected: {[months[i].strftime('%B') for i in anomalies]}")
    else:
        print("\n✅ No anomalies detected")

    # Seasonal decomposition
    print("\n" + "=" * 80)
    print("SEASONAL DECOMPOSITION")
    print("=" * 80)

    decomp = analyzer.decompose_seasonal(period=12)
    print(f"\n   Trend range: {decomp['trend'].min():.0f} - {decomp['trend'].max():.0f} kWh")
    print(f"   Seasonal amplitude: ±{np.abs(decomp['seasonal']).max():.0f} kWh")
    print(f"   Residual std: {decomp['residual'].std():.0f} kWh")

    # Plots
    analyzer.plot_uncertainty_bands(observed_data=observed,
                                   save_path='raven_enhancements/time_series_uncertainty.png')
    analyzer.plot_decomposition(save_path='raven_enhancements/seasonal_decomposition.png')

    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print("\n✅ Use this analysis to:")
    print("   1. Identify months with high prediction uncertainty")
    print("   2. Detect anomalies in observed vs predicted data")
    print("   3. Validate seasonal patterns in your model")
    print("   4. Check for autocorrelation in residuals (model misspecification)")


if __name__ == "__main__":
    example_bayesian_time_series()
