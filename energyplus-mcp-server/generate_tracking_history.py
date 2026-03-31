#!/usr/bin/env python3
"""
Generate synthetic DTABM tracking history for dashboard demos.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


APP_ROOT = Path(__file__).resolve().parent
DIGITAL_TWIN_ROOT = APP_ROOT / "digital_twin"
TRACKING_FILE = DIGITAL_TWIN_ROOT / "dtabm_tracking.csv"
REGISTRY_FILE = DIGITAL_TWIN_ROOT / "dtabm_registry.json"


def build_history(periods: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=periods, freq="MS")

    base_predicted = 37449.08
    seasonal = np.sin(np.linspace(0, 2 * np.pi, periods, endpoint=False)) * 2800
    drift = np.linspace(-900, 1200, periods)
    predicted = base_predicted + seasonal + drift

    noise = rng.normal(0, 1100, periods)
    actual = predicted + noise

    # Introduce a couple of notable events for the chart.
    if periods >= 6:
        actual[periods // 3] *= 1.09
        actual[(2 * periods) // 3] *= 0.92

    error_pct = (actual - predicted) / predicted * 100

    return pd.DataFrame(
        {
            "date": dates.strftime("%Y-%m-%d"),
            "predicted_kwh": predicted.round(2),
            "actual_kwh": actual.round(2),
            "error_pct": error_pct.round(3),
            "model_version": "1.0.0",
        }
    )


def update_registry_last_date(latest_date: str) -> None:
    if not REGISTRY_FILE.exists():
        return

    with REGISTRY_FILE.open() as f:
        registry = json.load(f)

    if "DTABM_Operational" in registry:
        registry["DTABM_Operational"]["last_update"] = f"{latest_date}T00:00:00"

    with REGISTRY_FILE.open("w") as f:
        json.dump(registry, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--months", type=int, default=12, help="Number of monthly events to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible history")
    parser.add_argument("--append", action="store_true", help="Append instead of replacing the tracking history")
    args = parser.parse_args()

    DIGITAL_TWIN_ROOT.mkdir(exist_ok=True)
    history = build_history(args.months, args.seed)

    if args.append and TRACKING_FILE.exists():
        existing = pd.read_csv(TRACKING_FILE)
        history = pd.concat([existing, history], ignore_index=True)
        history = history.drop_duplicates(subset=["date"], keep="last").sort_values("date")

    history.to_csv(TRACKING_FILE, index=False)
    update_registry_last_date(history.iloc[-1]["date"])

    print(f"Generated {len(history)} tracking events at {TRACKING_FILE}")
    print(f"Latest date: {history.iloc[-1]['date']}")


if __name__ == "__main__":
    main()
