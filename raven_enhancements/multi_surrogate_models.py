#!/usr/bin/env python3
"""
RAVEN-Inspired Multi-Surrogate Model Framework

RAVEN supports multiple surrogate types (GP, SVM, Polynomial Chaos, etc.)
This module implements ensemble surrogates for better accuracy and uncertainty.

Key innovation: Use multiple surrogate models and select the best one
based on cross-validation, or ensemble them for robust predictions.
"""

import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Matern, ConstantKernel as C
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
import pandas as pd
from typing import Dict, List, Tuple


class MultiSurrogateFramework:
    """
    RAVEN-style multi-surrogate modeling framework

    Implements:
    - Gaussian Process (GP)
    - Support Vector Regression (SVR)
    - Random Forest
    - Gradient Boosting
    - Polynomial Chaos Expansion (via Ridge regression)
    - Ensemble averaging
    """

    def __init__(self, param_names: List[str]):
        """
        Initialize framework

        Args:
            param_names: List of parameter names
        """
        self.param_names = param_names
        self.n_params = len(param_names)

        # Dictionary of surrogate models
        self.models = {}
        self.cv_scores = {}
        self.best_model_name = None

        self._initialize_models()

    def _initialize_models(self):
        """Initialize all surrogate model types"""

        # 1. Gaussian Process (Matern kernel - good for building physics)
        gp_kernel = C(1.0, (1e-3, 1e3)) * Matern(
            length_scale=[1.0] * self.n_params,
            length_scale_bounds=(1e-2, 1e2),
            nu=2.5  # Twice differentiable
        )
        self.models['GP_Matern'] = GaussianProcessRegressor(
            kernel=gp_kernel,
            n_restarts_optimizer=10,
            alpha=1e-6,
            normalize_y=True
        )

        # 2. Gaussian Process (RBF kernel - smoother)
        gp_kernel_rbf = C(1.0, (1e-3, 1e3)) * RBF(
            length_scale=[1.0] * self.n_params,
            length_scale_bounds=(1e-2, 1e2)
        )
        self.models['GP_RBF'] = GaussianProcessRegressor(
            kernel=gp_kernel_rbf,
            n_restarts_optimizer=10,
            alpha=1e-6,
            normalize_y=True
        )

        # 3. Support Vector Regression (good for nonlinear, limited data)
        self.models['SVR_RBF'] = SVR(
            kernel='rbf',
            C=100.0,
            epsilon=0.1,
            gamma='scale'
        )

        # 4. Random Forest (handles interactions well)
        self.models['RandomForest'] = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42
        )

        # 5. Gradient Boosting (excellent accuracy)
        self.models['GradientBoosting'] = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )

        # 6. Polynomial Chaos Expansion (via Ridge)
        # Uses polynomial features - similar to RAVEN's PCE
        self.models['PCE_Ridge'] = Ridge(alpha=1.0)

    def fit_all(self, X_train: np.ndarray, y_train: np.ndarray, use_pce_features: bool = True):
        """
        Fit all surrogate models

        Args:
            X_train: Training inputs (n_samples, n_params)
            y_train: Training outputs (n_samples,)
            use_pce_features: Use polynomial features for PCE model
        """
        print(f"🔧 Training {len(self.models)} surrogate models...")

        for name, model in self.models.items():
            print(f"\n   Training {name}...")

            # Special handling for PCE (needs polynomial features)
            if 'PCE' in name and use_pce_features:
                from sklearn.preprocessing import PolynomialFeatures
                poly = PolynomialFeatures(degree=2, include_bias=False)
                X_poly = poly.fit_transform(X_train)
                model.poly_transformer = poly  # Store for prediction
                model.fit(X_poly, y_train)
            else:
                model.fit(X_train, y_train)

            # Cross-validation score (R² on held-out data)
            try:
                if 'PCE' in name and use_pce_features:
                    cv_scores = cross_val_score(model, X_poly, y_train, cv=5, scoring='r2')
                else:
                    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')

                self.cv_scores[name] = cv_scores.mean()
                print(f"      CV R² = {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
            except Exception as e:
                print(f"      CV failed: {e}")
                self.cv_scores[name] = -np.inf

        # Identify best model
        self.best_model_name = max(self.cv_scores, key=self.cv_scores.get)
        print(f"\n✅ Best model: {self.best_model_name} (R² = {self.cv_scores[self.best_model_name]:.4f})")

    def predict(self, X_test: np.ndarray, model_name: str = None) -> np.ndarray:
        """
        Predict using a specific model or best model

        Args:
            X_test: Test inputs (n_samples, n_params)
            model_name: Model to use (None = best model)

        Returns:
            Predictions (n_samples,)
        """
        if model_name is None:
            model_name = self.best_model_name

        model = self.models[model_name]

        # Handle PCE polynomial features
        if 'PCE' in model_name and hasattr(model, 'poly_transformer'):
            X_test_transformed = model.poly_transformer.transform(X_test)
            return model.predict(X_test_transformed)
        else:
            return model.predict(X_test)

    def predict_ensemble(self, X_test: np.ndarray, weights: Dict[str, float] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Ensemble prediction (weighted average of all models)

        Args:
            X_test: Test inputs
            weights: Optional weights for each model (default: equal weights)

        Returns:
            (mean_prediction, std_prediction) - uncertainty from ensemble variance
        """
        if weights is None:
            # Equal weights
            weights = {name: 1.0 / len(self.models) for name in self.models.keys()}

        predictions = []
        for name in self.models.keys():
            pred = self.predict(X_test, model_name=name)
            predictions.append(pred * weights[name])

        predictions = np.array(predictions)

        # Ensemble mean and uncertainty
        ensemble_mean = predictions.sum(axis=0)
        ensemble_std = predictions.std(axis=0)

        return ensemble_mean, ensemble_std

    def predict_with_uncertainty(self, X_test: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict with uncertainty quantification

        For GP: use GP uncertainty
        For ensemble: use ensemble variance
        """
        # If best model is GP, use its built-in uncertainty
        if 'GP' in self.best_model_name:
            model = self.models[self.best_model_name]
            mean, std = model.predict(X_test, return_std=True)
            return mean, std

        # Otherwise, use ensemble uncertainty
        return self.predict_ensemble(X_test)

    def get_model_comparison_table(self) -> pd.DataFrame:
        """
        Get comparison table of all models

        Returns:
            DataFrame with model performance metrics
        """
        df = pd.DataFrame({
            'Model': list(self.cv_scores.keys()),
            'CV_R2': list(self.cv_scores.values())
        })

        df = df.sort_values('CV_R2', ascending=False)
        df['Rank'] = range(1, len(df) + 1)

        return df


def example_usage():
    """
    Example: Compare surrogate models for energy calibration
    """
    print("=" * 80)
    print("MULTI-SURROGATE MODEL COMPARISON (RAVEN-INSPIRED)")
    print("=" * 80)

    # Step 1: Generate synthetic training data
    print("\n📊 Generating training data...")
    from scipy.stats import qmc

    param_names = ['wall_r', 'window_u', 'infiltration', 'heating_eff', 'cooling_cop']
    param_bounds = {
        'wall_r': (10, 20),
        'window_u': (0.25, 0.45),
        'infiltration': (0.2, 0.6),
        'heating_eff': (0.75, 0.95),
        'cooling_cop': (2.5, 4.0)
    }

    n_train = 100
    sampler = qmc.LatinHypercube(d=len(param_names))
    samples = sampler.random(n=n_train)

    X_train = np.zeros_like(samples)
    for i, (name, (lb, ub)) in enumerate(param_bounds.items()):
        X_train[:, i] = lb + samples[:, i] * (ub - lb)

    # Synthetic energy model with nonlinearity
    def energy_model(params):
        wall_r, window_u, infil, heat_eff, cool_cop = params
        heating = (2000 / wall_r + 300 * window_u) * (1 + infil * 0.3) / heat_eff
        cooling = (2000 / wall_r + 300 * window_u) * 0.6 / cool_cop
        return heating * 5000 + cooling * 2000 + np.random.normal(0, 1000)  # Add noise

    y_train = np.array([energy_model(x) for x in X_train])

    print(f"   Training samples: {n_train}")
    print(f"   Energy range: {y_train.min():,.0f} - {y_train.max():,.0f} kWh/year")

    # Step 2: Train all surrogate models
    framework = MultiSurrogateFramework(param_names)
    framework.fit_all(X_train, y_train)

    # Step 3: Compare models
    print("\n" + "=" * 80)
    print("MODEL COMPARISON")
    print("=" * 80)

    comparison = framework.get_model_comparison_table()
    print("\n" + comparison.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    # Step 4: Test ensemble prediction
    print("\n" + "=" * 80)
    print("ENSEMBLE PREDICTION TEST")
    print("=" * 80)

    # Test point
    X_test = np.array([[15.0, 0.35, 0.4, 0.85, 3.2]])

    # Individual predictions
    print("\nIndividual model predictions:")
    for name in framework.models.keys():
        pred = framework.predict(X_test, model_name=name)
        print(f"   {name:20s}: {pred[0]:>12,.0f} kWh/year")

    # Ensemble prediction
    ensemble_mean, ensemble_std = framework.predict_ensemble(X_test)
    print(f"\n   {'Ensemble Mean':20s}: {ensemble_mean[0]:>12,.0f} kWh/year")
    print(f"   {'Ensemble Std':20s}: {ensemble_std[0]:>12,.0f} kWh/year")
    print(f"   95% CI: [{ensemble_mean[0] - 1.96*ensemble_std[0]:,.0f}, "
          f"{ensemble_mean[0] + 1.96*ensemble_std[0]:,.0f}] kWh/year")

    # Recommendation
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print(f"\n✅ Best single model: {framework.best_model_name}")
    print(f"   Use this for fast predictions in your Bayesian calibration")
    print(f"\n🎯 Ensemble approach:")
    print(f"   Use ensemble for final predictions to get uncertainty estimates")
    print(f"   Ensemble std captures model uncertainty + data uncertainty")


if __name__ == "__main__":
    example_usage()
