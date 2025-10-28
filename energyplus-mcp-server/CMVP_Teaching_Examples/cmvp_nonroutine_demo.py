#!/usr/bin/env python3
"""
CMVP Non-Routine Adjustment Demonstration
Shows how to handle a one-time event in Year 2 (server room addition)
"""

import json
import os
from pathlib import Path
import pandas as pd
import shutil

# Setup environment
script_dir = Path(__file__).parent.absolute()
os.chdir(script_dir)
os.environ['EPLUS_IDD_PATH'] = '/Applications/EnergyPlus-25-1-0/Energy+.idd'

# Create directories
(script_dir / 'logs').mkdir(exist_ok=True)
(script_dir / 'outputs').mkdir(exist_ok=True)

from energyplus_mcp_server.energyplus_tools import EnergyPlusManager
from energyplus_mcp_server.config import Config, PathConfig, EnergyPlusConfig

# Initialize
config = Config(
    paths=PathConfig(
        workspace_root=str(script_dir),
        output_dir=str(script_dir / 'outputs'),
        sample_files_path=str(script_dir / 'sample_files'),
        temp_dir='/tmp'
    ),
    energyplus=EnergyPlusConfig(
        idd_path='/Applications/EnergyPlus-25-1-0/Energy+.idd',
        installation_path='/Applications/EnergyPlus-25-1-0',
        executable_path='/usr/local/bin/energyplus'
    )
)

manager = EnergyPlusManager(config)

print()
print('╔' + '═' * 78 + '╗')
print('║' + ' ' * 20 + 'CMVP NON-ROUTINE ADJUSTMENT DEMONSTRATION' + ' ' * 17 + '║')
print('║' + ' ' * 22 + 'Server Room Addition in Year 2' + ' ' * 26 + '║')
print('╚' + '═' * 78 + '╝')
print()

print('SCENARIO:')
print('=' * 80)
print('Building: Medium Office (4,982 m²)')
print('Location: San Francisco, CA')
print()
print('YEAR 1 (Baseline Period):')
print('  - Normal office operations')
print('  - All spaces used as designed')
print('  - Lighting: 6.89 W/m²')
print('  - Equipment: 10.76 W/m²')
print()
print('YEAR 2 (Reporting Period):')
print('  - **NON-ROUTINE EVENT**: Server room added to Core_mid zone')
print('  - Date: July 1, Year 2 (mid-year addition)')
print('  - Area affected: ~550 m² (Core_mid zone)')
print('  - New equipment load: +40 W/m² for servers (24/7 operation)')
print('  - This represents a 372% increase in equipment density for that zone')
print('  - NOT representative of routine operations')
print('=' * 80)
print()

# Step 1: Create Year 1 baseline
print('STEP 1: Creating Year 1 Baseline Model')
print('-' * 80)

baseline_year1 = 'sample_files/ASHRAE901_OfficeMedium.idf'
print(f'  Using: {baseline_year1}')

# Inspect baseline equipment
equip_json = manager.inspect_electric_equipment(baseline_year1)
equip_data = json.loads(equip_json)

print(f'  Equipment objects: {equip_data["total_electric_equipment_objects"]}')

# Use typical office equipment density for baseline
# ASHRAE 90.1 medium office: ~10.76 W/m² for equipment
baseline_wpf = 10.76
print(f'  Baseline equipment density (typical office): {baseline_wpf:.2f} W/m²')

print()

# Step 2: Run Year 1 simulation
print('STEP 2: Running Year 1 Baseline Simulation')
print('-' * 80)
print('  This represents normal operations before the server room addition...')

weather_file = 'sample_files/USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw'

result_json = manager.run_simulation(
    idf_path=baseline_year1,
    weather_file=weather_file,
    annual=True,
    design_day=False
)
result_year1 = json.loads(result_json)

if result_year1.get('success'):
    print(f'  ✓ Year 1 simulation complete')
    print(f'    Output: {result_year1["output_directory"]}')
    year1_output = result_year1['output_directory']
else:
    print(f'  ✗ Failed: {result_year1.get("error")}')
    exit(1)

print()

# Step 3: Create Year 2 model with server room
print('STEP 3: Creating Year 2 Model (with Server Room Addition)')
print('-' * 80)

year2_model = 'sample_files/ASHRAE901_OfficeMedium_Year2_ServerRoom.idf'
shutil.copy(baseline_year1, year2_model)
print(f'  Created: {year2_model}')

# Modify equipment in Core_mid to simulate server room addition
# Increase equipment density from ~10.76 to ~50.76 W/m² (add 40 W/m² for servers)
new_wpf = baseline_wpf + 40.0  # Add server load

modifications = [{
    'target': 'zone:Core_mid',
    'field_updates': {
        'Watts_per_Floor_Area': new_wpf
    }
}]

print(f'  Modifying Core_mid equipment:')
print(f'    Baseline: {baseline_wpf:.2f} W/m²')
print(f'    With servers: {new_wpf:.2f} W/m²')
print(f'    Increase: +{new_wpf - baseline_wpf:.2f} W/m² (+{(new_wpf/baseline_wpf - 1)*100:.0f}%)')

# Apply modification using eppy directly
from eppy.modeleditor import IDF
IDF.setiddname(config.energyplus.idd_path)

idf_year2 = IDF(year2_model)
equipment_objs = idf_year2.idfobjects.get('ElectricEquipment', [])

for equip in equipment_objs:
    zone_name = equip.Zone_or_ZoneList_or_Space_or_SpaceList_Name
    if 'Core_mid' in zone_name:
        equip.Watts_per_Floor_Area = new_wpf
        print(f'  ✓ Updated: {equip.Name}')

idf_year2.save()
print()

# Step 4: Run Year 2 simulation
print('STEP 4: Running Year 2 Simulation (with Server Room)')
print('-' * 80)
print('  Simulating with server room operating full year...')

result_json = manager.run_simulation(
    idf_path=year2_model,
    weather_file=weather_file,
    annual=True,
    design_day=False
)
result_year2 = json.loads(result_json)

if result_year2.get('success'):
    print(f'  ✓ Year 2 simulation complete')
    print(f'    Output: {result_year2["output_directory"]}')
    year2_output = result_year2['output_directory']
else:
    print(f'  ✗ Failed: {result_year2.get("error")}')
    exit(1)

print()
print('=' * 80)
print('Simulations complete! Now analyzing results...')
print('=' * 80)
print()

# Export annual totals for next steps
print(json.dumps({
    'year1_output': year1_output,
    'year2_output': year2_output,
    'baseline_wpf': baseline_wpf,
    'year2_wpf': new_wpf
}, indent=2))
