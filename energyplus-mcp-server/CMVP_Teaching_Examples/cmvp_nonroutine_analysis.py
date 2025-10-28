#!/usr/bin/env python3
"""
CMVP Non-Routine Adjustment Analysis
Calculates the impact of the server room addition and required adjustments
"""

import pandas as pd
import json
from pathlib import Path

# Output directories from simulation
year1_dir = "outputs/ASHRAE901_OfficeMedium_simulation_20251023_132110"
year2_dir = "outputs/ASHRAE901_OfficeMedium_Year2_ServerRoom_simulation_20251023_132120"

# Read meter data
year1_meter = f"{year1_dir}/ASHRAE901_OfficeMediumMeter.csv"
year2_meter = f"{year2_dir}/ASHRAE901_OfficeMedium_Year2_ServerRoomMeter.csv"

df_year1 = pd.read_csv(year1_meter)
df_year2 = pd.read_csv(year2_meter)

# Clean columns
df_year1.columns = df_year1.columns.str.strip()
df_year2.columns = df_year2.columns.str.strip()

# Extract month
df_year1['Month'] = df_year1['Date/Time'].str.split('/').str[0].astype(int)
df_year2['Month'] = df_year2['Date/Time'].str.split('/').str[0].astype(int)

# Convert J to kWh
J_to_kWh = 1.0 / 3600000.0

# Monthly aggregation
year1_monthly = df_year1.groupby('Month').agg({
    'Electricity:Facility [J](Hourly)': 'sum',
    'NaturalGas:Facility [J](Hourly)': 'sum'
}).reset_index()

year2_monthly = df_year2.groupby('Month').agg({
    'Electricity:Facility [J](Hourly)': 'sum',
    'NaturalGas:Facility [J](Hourly)': 'sum'
}).reset_index()

# Convert to kWh
for df in [year1_monthly, year2_monthly]:
    df['Elec_kWh'] = df['Electricity:Facility [J](Hourly)'] * J_to_kWh
    df['Gas_kWh'] = df['NaturalGas:Facility [J](Hourly)'] * J_to_kWh
    df['Total_kWh'] = df['Elec_kWh'] + df['Gas_kWh']

# Merge for comparison
comparison = pd.merge(
    year1_monthly[['Month', 'Elec_kWh', 'Gas_kWh', 'Total_kWh']],
    year2_monthly[['Month', 'Elec_kWh', 'Gas_kWh', 'Total_kWh']],
    on='Month',
    suffixes=('_Year1', '_Year2')
)

# Calculate differences
comparison['Elec_Change_kWh'] = comparison['Elec_kWh_Year2'] - comparison['Elec_kWh_Year1']
comparison['Gas_Change_kWh'] = comparison['Gas_kWh_Year2'] - comparison['Gas_kWh_Year1']
comparison['Total_Change_kWh'] = comparison['Total_kWh_Year2'] - comparison['Total_kWh_Year1']

# Month names
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
comparison['Month_Name'] = comparison['Month'].apply(lambda x: month_names[x-1])

# Annual totals
annual_year1_elec = comparison['Elec_kWh_Year1'].sum()
annual_year1_gas = comparison['Gas_kWh_Year1'].sum()
annual_year1_total = comparison['Total_kWh_Year1'].sum()

annual_year2_elec = comparison['Elec_kWh_Year2'].sum()
annual_year2_gas = comparison['Gas_kWh_Year2'].sum()
annual_year2_total = comparison['Total_kWh_Year2'].sum()

# Non-routine adjustment calculation
# Server room added July 1 (mid-year), so it operates for 6 months in Year 2
# For M&V, we need to adjust Year 2 to represent "routine" operations

# Estimate server room load (simplified)
# The increase is ~40 W/m² × 550 m² × 8760 hours/year = 192,720 kWh/year
# For 6 months (July-Dec): 192,720 / 2 = 96,360 kWh

# Calculate the actual increase
actual_increase = annual_year2_elec - annual_year1_elec

# For CMVP: Non-routine adjustment = energy attributable to non-routine event
# This should be removed from Year 2 to get "routine" energy
nonroutine_adjustment_elec = comparison.loc[comparison['Month'] >= 7, 'Elec_Change_kWh'].sum()

# Adjusted Year 2 (routine operations only)
adjusted_year2_elec = annual_year2_elec - nonroutine_adjustment_elec
adjusted_year2_total = adjusted_year2_elec + annual_year2_gas

# Calculate savings (if any ECM was implemented)
# In this case, there's no ECM, just the non-routine event
routine_change = adjusted_year2_elec - annual_year1_elec

print()
print('╔' + '═' * 78 + '╗')
print('║' + ' ' * 22 + 'CMVP NON-ROUTINE ADJUSTMENT ANALYSIS' + ' ' * 20 + '║')
print('╚' + '═' * 78 + '╝')
print()

print('ANNUAL ENERGY CONSUMPTION')
print('=' * 80)
print(f'                             Year 1          Year 2        Change')
print(f'                           (Baseline)     (with Server)   (Increase)')
print('-' * 80)
print(f'Electricity (kWh)        {annual_year1_elec:12,.0f}  {annual_year2_elec:12,.0f}  {actual_increase:12,.0f}')
print(f'Natural Gas (kWh)        {annual_year1_gas:12,.0f}  {annual_year2_gas:12,.0f}  {annual_year2_gas - annual_year1_gas:12,.0f}')
print('-' * 80)
print(f'Total Site Energy (kWh)  {annual_year1_total:12,.0f}  {annual_year2_total:12,.0f}  {annual_year2_total - annual_year1_total:12,.0f}')
print('=' * 80)
print()

print('NON-ROUTINE ADJUSTMENT CALCULATION')
print('=' * 80)
print('Event: Server room added July 1, Year 2')
print('Period affected: July-December (6 months)')
print()
print(f'Electricity increase (Jul-Dec):  {nonroutine_adjustment_elec:12,.0f} kWh')
print(f'  Monthly average:                 {nonroutine_adjustment_elec/6:12,.0f} kWh/month')
print()
print('Per IPMVP, this energy must be EXCLUDED from savings calculations')
print('because it represents a non-routine change in facility operation.')
print('=' * 80)
print()

print('ADJUSTED YEAR 2 CONSUMPTION (Routine Operations Only)')
print('=' * 80)
print(f'Year 2 Reported:                 {annual_year2_elec:12,.0f} kWh')
print(f'Less: Non-routine adjustment:    {nonroutine_adjustment_elec:12,.0f} kWh')
print(f'Adjusted Year 2 (routine):       {adjusted_year2_elec:12,.0f} kWh')
print()
print(f'Year 1 Baseline:                 {annual_year1_elec:12,.0f} kWh')
print(f'Routine Change (Year 2-Year 1):  {routine_change:12,.0f} kWh ({routine_change/annual_year1_elec*100:+.1f}%)')
print('=' * 80)
print()

# Monthly breakdown
print('MONTHLY BREAKDOWN OF NON-ROUTINE IMPACT')
print('=' * 80)
print('Month  Year 1    Year 2    Change    Non-Routine  Adjusted Year 2')
print('       (kWh)     (kWh)     (kWh)     Period       (routine)')
print('-' * 80)

for _, row in comparison.iterrows():
    month = row['Month_Name']
    y1 = row['Elec_kWh_Year1']
    y2 = row['Elec_kWh_Year2']
    change = row['Elec_Change_kWh']
    nonroutine = 'YES' if row['Month'] >= 7 else 'NO'
    adjusted = y1 if row['Month'] >= 7 else y2  # Use Y1 for affected months

    print(f'{month:6} {y1:9,.0f} {y2:9,.0f} {change:9,.0f}   {nonroutine:11}  {adjusted:9,.0f}')

print('=' * 80)
print()

# Save comparison data
output_csv = 'outputs/CMVP_NonRoutine_Adjustment_Analysis.csv'
comparison.to_csv(output_csv, index=False, float_format='%.2f')

print(f'✓ Analysis saved to: {output_csv}')
print()

# Save summary
summary = {
    'year1_baseline_elec_kwh': annual_year1_elec,
    'year2_reported_elec_kwh': annual_year2_elec,
    'nonroutine_adjustment_kwh': nonroutine_adjustment_elec,
    'year2_adjusted_routine_kwh': adjusted_year2_elec,
    'routine_change_kwh': routine_change,
    'nonroutine_period': 'July-December Year 2',
    'nonroutine_event': 'Server room addition (40 W/m², 550 m²)'
}

with open('outputs/CMVP_NonRoutine_Summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print('✓ Summary saved to: outputs/CMVP_NonRoutine_Summary.json')
print()
