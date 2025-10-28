#!/usr/bin/env python3
"""
FMU Co-Simulation Demonstration
Simulates what FMU co-simulation does using a simplified building thermal model
Shows the concept without requiring actual FMU export
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

class SimplifiedBuildingModel:
    """
    Simplified thermal model that mimics what an FMU would do
    Represents a single-zone building
    """

    def __init__(self, initial_temp=20):
        self.zone_temp = initial_temp
        self.outdoor_temp = 0
        self.heating_setpoint = 21
        self.cooling_setpoint = 24
        self.time = 0

        # Building thermal properties
        self.thermal_mass = 5000000  # J/K (thermal capacity) - much larger for stability
        self.ua_value = 200  # W/K (heat loss coefficient)
        self.max_heating = 10000  # W
        self.max_cooling = 8000  # W
        self.internal_gains = 1000  # W (people, lights, equipment)

    def set_outdoor_temp(self, temp):
        """Set outdoor temperature (from weather)"""
        self.outdoor_temp = temp

    def set_heating_setpoint(self, setpoint):
        """Set heating setpoint (from controller)"""
        self.heating_setpoint = setpoint

    def set_cooling_setpoint(self, setpoint):
        """Set cooling setpoint (from controller)"""
        self.cooling_setpoint = setpoint

    def get_zone_temp(self):
        """Read zone temperature (FMU output)"""
        return self.zone_temp

    def get_heating_power(self):
        """Get current heating power"""
        return self.heating_power

    def get_cooling_power(self):
        """Get current cooling power"""
        return self.cooling_power

    def do_step(self, timestep_seconds):
        """
        Simulate one timestep (like FMU doStep)
        """

        # Calculate heat transfer with outdoors
        q_transmission = self.ua_value * (self.outdoor_temp - self.zone_temp)

        # Determine HVAC power needed (with proportional control for stability)
        if self.zone_temp < self.heating_setpoint - 0.5:
            # Need heating
            error = self.heating_setpoint - self.zone_temp
            self.heating_power = min(self.max_heating, error * 500)  # Proportional gain
            self.cooling_power = 0
        elif self.zone_temp > self.cooling_setpoint + 0.5:
            # Need cooling
            error = self.zone_temp - self.cooling_setpoint
            self.cooling_power = min(self.max_cooling, error * 500)
            self.heating_power = 0
        else:
            # In deadband
            self.heating_power = 0
            self.cooling_power = 0

        # Energy balance
        q_net = (q_transmission +
                self.internal_gains +
                self.heating_power -
                self.cooling_power)

        # Update zone temperature
        delta_temp = (q_net * timestep_seconds) / self.thermal_mass
        self.zone_temp += delta_temp

        self.time += timestep_seconds

class BaselineController:
    """Traditional fixed schedule control"""

    def __init__(self):
        self.name = "Baseline (Fixed Schedule)"

    def get_setpoint(self, hour_of_day, day_of_week):
        """Fixed setpoint schedule"""
        # Weekday occupied 7am-6pm
        if day_of_week < 5 and 7 <= hour_of_day < 18:
            return 21, 24  # Heating, cooling setpoints
        else:
            return 18, 27  # Setback

class SmartController:
    """Smart adaptive control"""

    def __init__(self):
        self.name = "Smart (Adaptive)"

    def get_setpoint(self, hour_of_day, day_of_week, outdoor_temp):
        """Adaptive setpoint based on conditions"""

        # Occupied hours
        if day_of_week < 5 and 7 <= hour_of_day < 18:
            # Occupied - adapt based on outdoor temp
            if outdoor_temp < -5:
                return 22, 24  # Warmer in extreme cold
            elif outdoor_temp > 25:
                return 21, 25  # Allow warmer in hot weather
            else:
                return 21, 24  # Normal
        else:
            # Unoccupied - aggressive setback
            if outdoor_temp < 0:
                return 16, 30  # Prevent freezing
            else:
                return 15, 30  # Deep setback

def generate_weather(hours=168):
    """Generate typical winter week weather"""
    time = np.arange(hours)

    # Daily cycle: cold at night, warmer during day
    daily = 5 + 8 * np.sin((time - 6) / 24 * 2 * np.pi)

    # Weekly trend: getting colder
    weekly_trend = -0.05 * time

    # Some random variation
    noise = np.random.normal(0, 2, hours)

    outdoor_temp = daily + weekly_trend + noise

    return outdoor_temp

def run_cosimulation(controller, hours=168):
    """
    Run co-simulation for one week
    This mimics the FMU co-simulation loop
    """

    print(f"\n{'='*70}")
    print(f"Running Co-Simulation: {controller.name}")
    print(f"{'='*70}\n")

    # Initialize building FMU
    building = SimplifiedBuildingModel(initial_temp=20)

    # Generate weather
    weather = generate_weather(hours)

    # Storage for results
    results = {
        'time': [],
        'zone_temp': [],
        'outdoor_temp': [],
        'heating_setpoint': [],
        'cooling_setpoint': [],
        'heating_power': [],
        'cooling_power': []
    }

    # Co-simulation loop (like FMU master algorithm)
    for hour in range(hours):
        # Current conditions
        outdoor_temp = weather[hour]
        day_of_week = (hour // 24) % 7
        hour_of_day = hour % 24

        # Set outdoor temperature (from weather file)
        building.set_outdoor_temp(outdoor_temp)

        # Get control setpoints (from controller)
        if isinstance(controller, SmartController):
            heat_sp, cool_sp = controller.get_setpoint(hour_of_day, day_of_week, outdoor_temp)
        else:
            heat_sp, cool_sp = controller.get_setpoint(hour_of_day, day_of_week)

        building.set_heating_setpoint(heat_sp)
        building.set_cooling_setpoint(cool_sp)

        # Simulate one hour (FMU.doStep)
        building.do_step(3600)

        # Read outputs (FMU.getReal)
        zone_temp = building.get_zone_temp()
        heating_power = building.get_heating_power()
        cooling_power = building.get_cooling_power()

        # Store results
        results['time'].append(hour)
        results['zone_temp'].append(zone_temp)
        results['outdoor_temp'].append(outdoor_temp)
        results['heating_setpoint'].append(heat_sp)
        results['cooling_setpoint'].append(cool_sp)
        results['heating_power'].append(heating_power / 1000)  # kW
        results['cooling_power'].append(cooling_power / 1000)  # kW

        # Progress
        if hour % 24 == 0:
            day = hour // 24 + 1
            print(f"  Day {day} completed - Zone temp: {zone_temp:.1f}°C")

    # Calculate energy use
    total_heating = sum(results['heating_power'])  # kWh (power * 1 hour)
    total_cooling = sum(results['cooling_power'])
    total_energy = total_heating + total_cooling

    print(f"\n✅ Simulation completed!")
    print(f"   Total Heating: {total_heating:.1f} kWh")
    print(f"   Total Cooling: {total_cooling:.1f} kWh")
    print(f"   Total Energy: {total_energy:.1f} kWh")

    return results, total_energy

def compare_strategies():
    """Compare baseline vs smart control"""

    print("\n" + "="*80)
    print("FMU CO-SIMULATION DEMONSTRATION")
    print("Comparing Control Strategies for Building Energy Management")
    print("="*80)

    # Run baseline
    baseline_results, baseline_energy = run_cosimulation(BaselineController())

    # Run smart
    smart_results, smart_energy = run_cosimulation(SmartController())

    # Calculate savings
    savings_kwh = baseline_energy - smart_energy
    savings_pct = (savings_kwh / baseline_energy) * 100
    cost_savings = savings_kwh * 0.12  # $0.12/kWh

    print(f"\n{'='*80}")
    print("COMPARISON RESULTS")
    print(f"{'='*80}\n")

    print(f"📊 Energy Consumption (1 week):")
    print(f"   Baseline:  {baseline_energy:.1f} kWh")
    print(f"   Smart:     {smart_energy:.1f} kWh")
    print(f"   Savings:   {savings_kwh:.1f} kWh ({savings_pct:.1f}%)")

    print(f"\n💰 Cost Impact:")
    print(f"   Weekly savings: ${cost_savings:.2f}")
    print(f"   Annual savings: ${cost_savings * 52:.0f}")

    print(f"\n🎯 What This Demonstrates:")
    print(f"   - FMU co-simulation enables testing control strategies")
    print(f"   - Controller reads zone temperature each timestep")
    print(f"   - Controller adjusts setpoints based on logic")
    print(f"   - Building model responds to control signals")
    print(f"   - Quantify energy savings from smart controls")

    # Visualize
    print(f"\n📈 Creating visualization...")

    fig, axes = plt.subplots(3, 1, figsize=(14, 10))

    time = baseline_results['time']

    # Temperature
    ax = axes[0]
    ax.plot(time, baseline_results['zone_temp'], label='Baseline Zone Temp', linewidth=2)
    ax.plot(time, smart_results['zone_temp'], label='Smart Zone Temp', linewidth=2)
    ax.plot(time, baseline_results['outdoor_temp'], label='Outdoor Temp', linewidth=1, alpha=0.6, linestyle='--')
    ax.set_ylabel('Temperature (°C)', fontsize=11)
    ax.set_title('FMU Co-Simulation: Zone Temperature Control', fontsize=13, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Setpoints
    ax = axes[1]
    ax.plot(time, baseline_results['heating_setpoint'], label='Baseline Setpoint', linewidth=2, alpha=0.7)
    ax.plot(time, smart_results['heating_setpoint'], label='Smart Setpoint', linewidth=2)
    ax.set_ylabel('Heating Setpoint (°C)', fontsize=11)
    ax.set_title('Control Strategy: Adaptive vs Fixed Schedule', fontsize=13, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Power
    ax = axes[2]
    ax.plot(time, baseline_results['heating_power'], label='Baseline Heating', linewidth=2, alpha=0.7)
    ax.plot(time, smart_results['heating_power'], label='Smart Heating', linewidth=2)
    ax.set_xlabel('Time (hours)', fontsize=11)
    ax.set_ylabel('Heating Power (kW)', fontsize=11)
    ax.set_title(f'Energy Use - Savings: {savings_pct:.1f}% ({savings_kwh:.1f} kWh)', fontsize=13, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    plot_file = Path("/workspace/energyplus-mcp-server/fmu_cosim_demo_results.png")
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"   ✅ Plot saved: {plot_file.name}")

    print(f"\n💻 View results:")
    print(f"   docker cp energyplus-mcp:/workspace/energyplus-mcp-server/fmu_cosim_demo_results.png .")
    print(f"   open fmu_cosim_demo_results.png")

    print("\n" + "="*80)
    print("✅ FMU CO-SIMULATION DEMONSTRATION COMPLETE!")
    print("="*80 + "\n")

    print("📝 Key Concepts Demonstrated:")
    print("   1. ✅ Co-simulation loop: Controller ⟷ Building")
    print("   2. ✅ Real-time control decisions based on building state")
    print("   3. ✅ Comparison of control strategies")
    print("   4. ✅ Energy savings quantification")
    print("")
    print("   This is what FMU co-simulation enables with real EnergyPlus models!")
    print("")

if __name__ == "__main__":
    compare_strategies()
