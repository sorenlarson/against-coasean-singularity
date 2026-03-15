# Against the Coasean Singularity

Simulation and paper code for "Against the Coasean Singularity" (Larson, 2026).

## Quick start

```bash
pip install -r requirements.txt

# Run parallel-world simulation
python simulation.py

# Run competing-world simulation
python simulation.py --competing

# Run ablation experiments
python ablations.py
```

## Structure

- `paper/` — LaTeX source and compiled PDF
- `simulation.py` — Main simulation: graph economy, three institutional forms, all economic functions
- `ablations.py` — Ablation runner: channel decomposition, density sweep, ownership cost sensitivity
- `output/` — Generated results (JSON + Markdown)

## Paper

The paper compares three institutional forms over a directed graph economy:

- **Market** (Coasean singularity): AI agents transact freely
- **Router** (SaaS platform): platform intermediary coordinates without owning
- **Rollup** (cybernetic rollup): holding company owns nodes, coordinates internally

Central finding: platform intermediation amplifies information leakage rather than reducing it. The rollup generates 25% higher net surplus than the router (mean across 10 seeds). Under passive-router assumptions in a competing-world simulation, this advantage compounds into router extinction across all tested seeds.
