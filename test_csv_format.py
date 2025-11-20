#!/usr/bin/env python3
"""
Simple CSV format validator - no dependencies needed
Tests basic CSV structure without pandas/numpy
"""

import csv
from pathlib import Path

def validate_csv_format(file_path):
    """Validate CSV structure without pandas"""
    print(f"\nValidating: {file_path}")
    print("-" * 60)

    try:
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            # Check columns
            if not reader.fieldnames:
                print("✗ No columns found")
                return False

            print(f"✓ Columns found: {', '.join(reader.fieldnames)}")

            # Check required columns
            required = ['Month', 'Measured (kWh)']
            has_required = all(col in reader.fieldnames for col in required)

            if not has_required:
                print(f"✗ Missing required columns: {required}")
                return False
            print(f"✓ Has required columns: {required}")

            # Check optional columns
            if 'Uncertainty (kWh)' in reader.fieldnames:
                print("✓ Has optional 'Uncertainty (kWh)' column")
            else:
                print("ℹ Missing optional 'Uncertainty (kWh)' column (will default to 5%)")

            # Check row count
            if len(rows) != 12:
                print(f"✗ Expected 12 rows, found {len(rows)}")
                return False
            print(f"✓ Has 12 months of data")

            # Check values are numeric and positive
            total = 0
            for i, row in enumerate(rows):
                month = row['Month']
                try:
                    value = float(row['Measured (kWh)'])
                    if value <= 0:
                        print(f"✗ Row {i+1} ({month}): Value must be positive, got {value}")
                        return False
                    total += value
                except ValueError:
                    print(f"✗ Row {i+1} ({month}): Invalid number '{row['Measured (kWh)']}'")
                    return False

            print(f"✓ All values are valid and positive")
            print(f"✓ Total annual consumption: {total:.0f} kWh")

            # Show sample data
            print("\nSample data (first 3 months):")
            for row in rows[:3]:
                month = row['Month']
                kwh = row['Measured (kWh)']
                unc = row.get('Uncertainty (kWh)', 'N/A')
                print(f"  {month}: {kwh} kWh (±{unc})")

            return True

    except FileNotFoundError:
        print(f"✗ File not found: {file_path}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("CSV FORMAT VALIDATION TEST")
    print("=" * 60)

    # Test the example file
    if Path('test_utility_data.csv').exists():
        result = validate_csv_format('test_utility_data.csv')
        if result:
            print("\n✅ test_utility_data.csv is VALID")
        else:
            print("\n❌ test_utility_data.csv is INVALID")
    else:
        print("\n⚠ test_utility_data.csv not found")

    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)
    print("\nTo run full tests with pandas/numpy validation:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Run: python3 test_upload.py")
