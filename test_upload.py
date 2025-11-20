#!/usr/bin/env python3
"""
Test script for utility data upload functionality
Tests the CSV parsing and validation without running Streamlit
"""

import pandas as pd
import numpy as np
from pathlib import Path

def parse_uploaded_data(file_path):
    """
    Parse and validate uploaded utility data CSV

    Returns:
        tuple: (success: bool, message: str, data: tuple or None)
    """
    try:
        df = pd.read_csv(file_path)

        # Validate required columns
        required_cols = ['Month', 'Measured (kWh)']
        if not all(col in df.columns for col in required_cols):
            return False, f"Missing required columns. Need: {', '.join(required_cols)}", None

        # Validate 12 months of data
        if len(df) != 12:
            return False, f"Expected 12 months of data, found {len(df)} rows", None

        # Extract data
        measured_monthly = df['Measured (kWh)'].values

        # Check for optional uncertainty column
        if 'Uncertainty (kWh)' in df.columns:
            measurement_noise_std = df['Uncertainty (kWh)'].values
        else:
            # Default: 5% of measured value as uncertainty
            measurement_noise_std = measured_monthly * 0.05

        # Validate data ranges
        if np.any(measured_monthly <= 0):
            return False, "Energy consumption values must be positive", None

        if np.any(measurement_noise_std <= 0):
            return False, "Uncertainty values must be positive", None

        # Create cleaned dataframe
        measured_data = pd.DataFrame({
            'Month': df['Month'].values,
            'Measured (kWh)': measured_monthly,
            'Uncertainty (kWh)': measurement_noise_std
        })

        return True, "Data loaded successfully!", (measured_data, measured_monthly, measurement_noise_std)

    except Exception as e:
        return False, f"Error parsing file: {str(e)}", None


def run_tests():
    """Run test suite for upload functionality"""

    print("=" * 70)
    print("UTILITY DATA UPLOAD TEST SUITE")
    print("=" * 70)

    # Test 1: Valid file with uncertainty
    print("\n[TEST 1] Valid CSV with uncertainty column")
    print("-" * 70)
    success, message, data = parse_uploaded_data('test_utility_data.csv')
    print(f"✓ Success: {success}")
    print(f"✓ Message: {message}")
    if data:
        df, measured_monthly, measurement_noise_std = data
        print(f"✓ Data shape: {df.shape}")
        print(f"✓ Total annual consumption: {measured_monthly.sum():.0f} kWh")
        print(f"✓ Average monthly consumption: {measured_monthly.mean():.0f} kWh")
        print(f"✓ Average uncertainty: {measurement_noise_std.mean():.1f} kWh")
        print("\nFirst 3 months:")
        print(df.head(3).to_string(index=False))

    # Test 2: Create a CSV without uncertainty column
    print("\n[TEST 2] Valid CSV without uncertainty column")
    print("-" * 70)
    test_df = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'Measured (kWh)': [1500, 1400, 1300, 1200, 1100, 1200,
                           1400, 1350, 1100, 1200, 1400, 1500]
    })
    test_df.to_csv('test_no_uncertainty.csv', index=False)

    success, message, data = parse_uploaded_data('test_no_uncertainty.csv')
    print(f"✓ Success: {success}")
    print(f"✓ Message: {message}")
    if data:
        df, measured_monthly, measurement_noise_std = data
        print(f"✓ Auto-calculated uncertainty (5% of measured): {measurement_noise_std[:3]}")

    # Test 3: Invalid - wrong number of months
    print("\n[TEST 3] Invalid CSV - only 6 months")
    print("-" * 70)
    test_df = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Measured (kWh)': [1500, 1400, 1300, 1200, 1100, 1200]
    })
    test_df.to_csv('test_invalid_months.csv', index=False)

    success, message, data = parse_uploaded_data('test_invalid_months.csv')
    print(f"✓ Success: {success}")
    print(f"✓ Error message: {message}")

    # Test 4: Invalid - missing required column
    print("\n[TEST 4] Invalid CSV - missing required column")
    print("-" * 70)
    test_df = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'Energy': [1500, 1400, 1300, 1200, 1100, 1200,
                   1400, 1350, 1100, 1200, 1400, 1500]
    })
    test_df.to_csv('test_wrong_columns.csv', index=False)

    success, message, data = parse_uploaded_data('test_wrong_columns.csv')
    print(f"✓ Success: {success}")
    print(f"✓ Error message: {message}")

    # Test 5: Invalid - negative values
    print("\n[TEST 5] Invalid CSV - negative values")
    print("-" * 70)
    test_df = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'Measured (kWh)': [1500, -1400, 1300, 1200, 1100, 1200,
                           1400, 1350, 1100, 1200, 1400, 1500]
    })
    test_df.to_csv('test_negative.csv', index=False)

    success, message, data = parse_uploaded_data('test_negative.csv')
    print(f"✓ Success: {success}")
    print(f"✓ Error message: {message}")

    # Test 6: CSV template generation
    print("\n[TEST 6] CSV Template Generation")
    print("-" * 70)
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    template = pd.DataFrame({
        'Month': months,
        'Measured (kWh)': [1500, 1400, 1300, 1200, 1100, 1200,
                          1400, 1350, 1100, 1200, 1400, 1500],
        'Uncertainty (kWh)': [75, 70, 65, 60, 55, 60,
                              70, 67, 55, 60, 70, 75]
    })
    template_csv = template.to_csv(index=False)
    print(f"✓ Template generated ({len(template_csv)} characters)")
    print("✓ First 200 characters:")
    print(template_csv[:200])

    # Cleanup temporary test files
    print("\n[CLEANUP] Removing temporary test files")
    print("-" * 70)
    temp_files = ['test_no_uncertainty.csv', 'test_invalid_months.csv',
                  'test_wrong_columns.csv', 'test_negative.csv']
    for f in temp_files:
        if Path(f).exists():
            Path(f).unlink()
            print(f"✓ Removed {f}")

    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
