# M&V Plan — Guinness Brewery Chiller Plant

**Site:** Diageo Guinness Brewery, St. James's Gate, Dublin, Ireland
**Asset:** Process chiller serving wort cooling, fermentation jackets, and brite-tank glycol loop
**M&V framework:** IPMVP Option D (Calibrated Simulation), aligned with ASHRAE Guideline 14-2023
**Simulation engine:** EnergyPlus 24.2 with a DOE prototype model adapted for brewery process cooling

---

## 1. Project context

Guinness's St. James's Gate site has a glycol chilled-water plant supplying:

- Wort cooling via plate heat exchangers (95 °C → 10 °C)
- Cylindro-conical fermenter cooling jackets (set point ≈ 8 °C, crash-cool to 0 °C)
- Bright-beer tank and CIP loops
- Packaging hall comfort loop (small fraction)

The chiller of interest is a single 1,800 kW water-cooled centrifugal unit with R-1234ze refrigerant, paired with a cooling tower and primary/secondary glycol pumps. The retrofit being evaluated is:

1. Replace fixed-speed primary glycol pumps with VFD pumps + ΔP reset
2. Condenser-water temperature reset (28 °C → variable, 18-29 °C)
3. Chiller controls upgrade enabling lower lift at part load

Expected savings: 20-25 % of annual chiller-plant electricity.

---

## 2. IPMVP option selection

**Option D — Calibrated Simulation** is selected because:

- Multiple interactive ECMs are bundled (pumps + tower + chiller controls); retrofit isolation (Option B) would require boundary metering of every flow path.
- Production volume and ambient conditions vary year-to-year; a calibrated model handles the routine adjustments cleanly.
- Whole-facility billing analysis (Option C) is unsuitable because the chiller is a fraction of total brewery load and is masked by brewhouse, utilities, and packaging variability.

Calibration acceptance per ASHRAE G14:

| Index           | Monthly | Hourly |
| --------------- | ------- | ------ |
| NMBE            | ≤ ±5 %  | ≤ ±10 %|
| CV(RMSE)        | ≤ 15 %  | ≤ 30 % |

---

## 3. EnergyPlus prototype model

Starting point: the **DOE Refrigerated Warehouse** prototype, modified to represent process cooling rather than space cooling, plus a custom plant loop. The prototype is used for:

- Plant topology (`PlantLoop`, `CondenserLoop`, sizing factors)
- Chiller object (`Chiller:Electric:EIR`) with curve forms already validated by NREL
- Pump objects (`Pump:VariableSpeed`) and `CoolingTower:VariableSpeed`

Key object overrides:

```idf
Chiller:Electric:EIR,
    GuinnessChiller_01,           !- Name
    1800000,                      !- Reference Capacity {W}
    6.1,                          !- Reference COP {W/W}
    6.67,                         !- Reference Leaving Chilled Water Temp {C}
    29.4,                         !- Reference Entering Condenser Fluid Temp {C}
    0.0762,                       !- Reference Chilled Water Flow Rate {m3/s}
    0.1136,                       !- Reference Condenser Fluid Flow Rate {m3/s}
    CAPFT_Centrifugal_R1234ze,    !- Cooling Capacity Function of Temp Curve
    EIRFT_Centrifugal_R1234ze,    !- EIR Function of Temp Curve
    EIRFPLR_VSD_Centrifugal,      !- EIR Function of PLR Curve
    0.15,                         !- Min Part Load Ratio
    1.00,                         !- Max Part Load Ratio
    0.65,                         !- Optimum Part Load Ratio
    0.20,                         !- Min Unloading Ratio
    ...
    WaterCooled,                  !- Condenser Type
    ...
    LeavingSetpoint;              !- Chiller Flow Mode
```

Process loads enter the chilled-glycol loop through scheduled `LoadProfile:Plant` objects, with hourly demand profiles built from brewhouse SCADA data (wort production batches) and fermenter temperature logs.

Custom inputs that diverge from the prototype:

- 30 % propylene-glycol fluid (`FluidProperties:GlycolConcentration`)
- Chilled-glycol supply set point: −4 °C (vs. +6.7 °C in the unmodified prototype)
- Process load schedule at 1-minute resolution aggregated to hourly for simulation
- Dublin Airport (EIDW) AMY weather file for the baseline and reporting periods

---

## 4. Measurement boundary

Boundary = chiller compressor + condenser-water pumps + cooling-tower fan + primary and secondary glycol pumps. Cooling delivered to processes is **inside** the boundary (it is a model output, not a metered savings driver).

| Point | Sensor                                      | Accuracy   | Logging  |
| ----- | ------------------------------------------- | ---------- | -------- |
| E1    | Chiller compressor kWh (sub-meter)          | ±0.5 %     | 15 min   |
| E2    | Condenser-pump + tower-fan kWh              | ±0.5 %     | 15 min   |
| E3    | Primary + secondary glycol-pump kWh         | ±0.5 %     | 15 min   |
| F1    | Glycol supply/return T (RTD, 4-wire)        | ±0.1 K     | 1 min    |
| F2    | Glycol mass-flow (Coriolis)                 | ±0.2 %     | 1 min    |
| W1    | OAT, RH at site (also cross-check w/ EIDW)  | ±0.3 K     | 5 min    |
| P1    | Wort-cooling batch counter (SCADA tag)      | n/a        | per batch|

Independent variables for the model: OAT, OA wet-bulb, hectolitres brewed per day, fermenter active-cool flag count.

---

## 5. Baseline and reporting periods

| Period         | Dates                       | Notes                                             |
| -------------- | --------------------------- | ------------------------------------------------- |
| Baseline       | 2024-05-01 to 2025-04-30    | Pre-retrofit, full annual cycle                   |
| Construction   | 2025-05-01 to 2025-06-30    | Excluded                                          |
| Reporting      | 2025-07-01 to 2026-06-30    | Post-retrofit, full annual cycle                  |
| Persistence    | Annual through 2030         | Re-run model every 12 months with new AMY weather |

Baseline-period metered data is used to calibrate the model. The calibrated baseline model is then re-run with reporting-period weather and production to produce the **adjusted baseline**.

---

## 6. Calibration procedure

1. **Static inputs:** survey nameplate data, refrigerant, design ΔT, pump curves, tower fan power.
2. **Schedules:** build process-load schedule from SCADA brew counts × per-batch cooling energy.
3. **Parameter tuning** (Bayesian, using this repo's calibration toolkit):
   - Priors on chiller reference COP (𝒩(6.1, 0.3)), pump efficiency, tower UA, glycol-loop heat gain.
   - Likelihood: hourly chiller kWh and glycol ΔT.
   - Posterior obtained via the existing `streamlit_app.py` pipeline / calibration scripts in this repo.
4. **Acceptance:** verify NMBE and CV(RMSE) against thresholds in §2 on a hold-out month before locking the model.

---

## 7. Savings equation

```
Savings_reporting = E_baseline_adjusted − E_reporting_measured ± routine_adjustment
```

where `E_baseline_adjusted` is the calibrated EnergyPlus model run with **baseline equipment** but **reporting-period** weather, production, and set points.

Non-routine adjustments are applied if:
- Production capacity changes >10 %
- A new process load is added to the loop
- Glycol supply set point is re-baselined for product reasons

---

## 8. Example calculation

### Inputs

| Quantity                                                         | Value           |
| ---------------------------------------------------------------- | --------------- |
| Baseline metered chiller-plant electricity (E1+E2+E3), 2024/25   | 4,200,000 kWh   |
| Calibrated model output, baseline equipment + baseline weather   | 4,158,000 kWh   |
| Calibration NMBE / CV(RMSE) hourly                               | −1.0 % / 11.4 % |
| Reporting-period metered electricity, 2025/26                    | 3,150,000 kWh   |
| Reporting-period CDD18 (Dublin)                                  | +8 % vs base    |
| Reporting-period production (hL brewed)                          | +5 % vs base    |

### Step 1 — Re-simulate baseline equipment with reporting-period drivers

Run the calibrated EnergyPlus model with:

- Same chiller object (COP 6.1, fixed-speed pumps, fixed CW set point 28 °C)
- Reporting-period AMY weather file
- Reporting-period brewhouse schedule (5 % more batches)

```
E_baseline_adjusted = 4,420,000 kWh    (model output)
```

Sanity check, decomposed:

| Driver shift     | Modelled Δ | Note                                       |
| ---------------- | ---------- | ------------------------------------------ |
| Production +5 %  | +168 MWh   | Wort-cooling load scales ~linearly         |
| Weather +8 % CDD | +94 MWh    | Higher condenser lift, lower tower benefit |
| **Total**        | **+262 MWh** vs baseline calibrated 4,158 → 4,420 |

### Step 2 — Compute savings

```
Savings = E_baseline_adjusted − E_reporting_measured
        = 4,420,000 − 3,150,000
        = 1,270,000 kWh
```

### Step 3 — Convert to cost and carbon

At €0.165/kWh (Irish industrial 2025/26 forward) and Irish grid intensity 244 gCO₂/kWh:

```
Cost savings   = 1,270,000 × 0.165   = €209,550 / yr
CO₂ avoided    = 1,270,000 × 0.000244 = 310 tCO₂ / yr
```

### Step 4 — Uncertainty band

Per ASHRAE G14, combine model and measurement uncertainty in quadrature:

- Model relative uncertainty (from CV(RMSE) hourly = 11.4 %, t = 1.96, n_eff ≈ 8760/24): ~3.0 %
- Sub-meter uncertainty (RSS of E1+E2+E3 at ±0.5 %): ~0.9 %
- Production driver uncertainty: ~1.5 %

```
U_total ≈ √(3.0² + 0.9² + 1.5²) ≈ 3.5 %
Savings: 1,270,000 ± 44,000 kWh  (90 % CI)
```

Reported savings exceed 2× total uncertainty → **statistically significant** under G14.

---

## 9. Reporting deliverables

Each reporting period:

1. Updated EnergyPlus IDF + AMY weather (archived in repo under `models/guinness_chiller/<year>/`)
2. Calibration statistics (NMBE, CV(RMSE)) per month
3. Savings table (kWh, €, tCO₂) with uncertainty
4. Driver decomposition (production vs. weather vs. ECM)
5. Anomaly log (any non-routine adjustments)

## 10. Roles

| Role            | Party                                           |
| --------------- | ----------------------------------------------- |
| M&V engineer    | (this team) — owns model, calibration, report   |
| Site contact    | Guinness utilities supervisor                   |
| Data owner      | Diageo OT/SCADA team                            |
| Independent QA  | CIBSE-accredited reviewer, annual sign-off      |

---

*References: IPMVP Core Concepts 2022; ASHRAE Guideline 14-2023; DOE Commercial Prototype Building Models v24.2; EnergyPlus Engineering Reference §16 (Plant Equipment).*
