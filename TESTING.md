# Testing the Utility Data Upload Feature

## Quick Format Check (No Dependencies)

Validate CSV format without installing dependencies:

```bash
python3 test_csv_format.py
```

This checks:
- Required columns exist
- 12 months of data present
- Values are numeric and positive
- CSV structure is valid

## Full Test Suite (Requires Dependencies)

Install dependencies first:

```bash
pip install -r requirements.txt
```

Then run comprehensive tests:

```bash
python3 test_upload.py
```

This tests:
- Valid CSV with uncertainty column
- Valid CSV without uncertainty (auto-calculates 5%)
- Invalid inputs (wrong column names, missing data, negative values)
- Template generation

## Run the Full Application

Start the Streamlit app:

```bash
streamlit run streamlit_app.py
```

Then in the browser:
1. Click "📥 Download CSV Template" to get the format
2. Upload `test_utility_data.csv` to test with sample data
3. Verify the data table shows your uploaded values
4. Click "🚀 Run Calibration" to run Bayesian inference
5. Test "🔄 Use Synthetic Data Instead" to switch back

## Test Files

- `test_utility_data.csv` - Valid sample data with 12 months
- `test_csv_format.py` - Basic validation (no dependencies)
- `test_upload.py` - Full test suite (requires pandas/numpy)

## Expected CSV Format

```csv
Month,Measured (kWh),Uncertainty (kWh)
Jan,1650,82.5
Feb,1520,76.0
...
```

**Required columns:**
- `Month` - Month names
- `Measured (kWh)` - Energy consumption

**Optional columns:**
- `Uncertainty (kWh)` - Measurement uncertainty (defaults to 5% if omitted)
