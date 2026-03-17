# Market Sim: Against the Coasean Singularity

## What this is
A simulation framework comparing four institutional forms — fragmented market, platform router, data-isolated router, and vertically integrated rollup — over a directed graph economy. The paper argues that ownership generates more economic surplus than intermediation because firms rationally reveal more context to an entity they own than to a platform that might redistribute their intelligence to competitors.

## Key files
- `simulation.py` — Full simulation engine. `SimulationSettings` dataclass has all parameters. `SimulationRunner` runs parallel worlds (4 regimes independently). `CompetingWorldRunner` runs all 4 regimes in a single economy with acquisition dynamics.
- `ablations.py` — All experiment sweeps: Shapley decomposition, density/cost/visibility sweeps, subscription cost sweep, competing-world scenarios (3 router strategies), and the 35-industry parameter sweep.
- `paper/cybernetic_arbitrage_short.tex` — The 29-page paper (short version). `cybernetic_arbitrage.tex` is the full 51-page version.

## How to run
```bash
python3 simulation.py                    # Parallel world, 4 regimes
python3 simulation.py --competing        # Competing world, 4 regimes
python3 ablations.py                     # Full ablation + sweep suite
```

## The three parameters that matter for industry calibration
These are in the `industries` dict in `ablations.py` (~line 340):
- `rho_L` (0-1): **Durability** — how long does leaked information stay exploitable? Legal precedent = 0.95, patched vulnerability = 0.25.
- `leakage_sensitivity_low/high` (0-1): **Specificity** — how much competitive damage does revealing context cause? M&A strategy = 0.6-0.95, IT provisioning = 0.05-0.25.
- `transfer_rate` (0-0.05): **Transferability** — does operational knowledge at one firm improve another? Medical coding = 0.04 (same codes everywhere), bespoke litigation = 0.005.

To recalibrate an industry, change these values in the dict and run:
```python
from ablations import run_industry_sweep, build_settings
from simulation import SimulationSettings
run_industry_sweep(SimulationSettings())
```

## Key calibration choices
- `lambda_L = 2.5` — Leakage severity. Calibrated so the revelation-leakage tradeoff binds (~20% of market/router events choose partial revelation).
- `router_learning_leakage = 0.15` — How aggressively the platform redistributes client intelligence. This is the paper's core empirical question, not a settled parameter. See the lambda_R sweep table in the paper.
- `visibility_rollup_external = 0.85` — Rollup's external interactions have router-equivalent visibility (the parent provides governance comparable to platform shielding). The rollup's advantage comes entirely from internal interactions (visibility = 0.1).
