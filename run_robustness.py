"""Run 50-seed robustness at 200 nodes for both parallel and competing worlds."""
import json
import numpy as np
import time
from simulation import SimulationSettings, run_test_f, run_competing_world

SEEDS = range(42, 92)  # 50 seeds
N_NODES = 200
N_VERTICALS = 10
EDGE_DENSITY = 0.05
OPP_RATE = 0.3
INITIAL_OWNED = 10

results = {"parallel": [], "competing": []}

# Parallel world: 50 seeds, 200 nodes
print("=" * 60)
print(f"  PARALLEL WORLD: {len(list(SEEDS))} seeds, {N_NODES} nodes")
print("=" * 60)
start = time.time()
for seed in SEEDS:
    s = SimulationSettings(
        num_nodes=N_NODES, num_verticals=N_VERTICALS, edge_density=EDGE_DENSITY,
        opportunity_rate=OPP_RATE, initial_owned_count=INITIAL_OWNED,
        time_steps=50, seed=seed,
    )
    r = run_test_f(s, write_artifacts=False)
    rr = r["regime_results"]
    ratio = rr["rollup"]["total_surplus"] / rr["router"]["total_surplus"]
    p1 = r["propositions"]["P1_rollup_highest_surplus"]
    results["parallel"].append({"seed": seed, "ratio": round(ratio, 4), "P1": p1,
        "rollup_net": rr["rollup"]["total_surplus"], "router_net": rr["router"]["total_surplus"],
        "market_net": rr["market"]["total_surplus"]})
    print(f"  seed={seed}: ratio={ratio:.3f}  P1={p1}")
elapsed_p = time.time() - start
ratios_p = [r["ratio"] for r in results["parallel"]]
print(f"\n  Parallel: mean={np.mean(ratios_p):.3f}  std={np.std(ratios_p):.3f}  "
      f"min={min(ratios_p):.3f}  max={max(ratios_p):.3f}  "
      f"pass={sum(1 for r in ratios_p if r > 1)}/50  ({elapsed_p:.0f}s)")

# Competing world: 50 seeds, 200 nodes
print("\n" + "=" * 60)
print(f"  COMPETING WORLD: {len(list(SEEDS))} seeds, {N_NODES} nodes")
print("=" * 60)
start = time.time()
for seed in SEEDS:
    s = SimulationSettings(
        num_nodes=N_NODES, num_verticals=N_VERTICALS, edge_density=EDGE_DENSITY,
        opportunity_rate=OPP_RATE, initial_owned_count=INITIAL_OWNED,
        time_steps=100, seed=seed,
    )
    r = run_competing_world(s)
    alloc = r["final_allocation"]
    ru = r["rollup"]["total_surplus"]
    ro = r["router"]["total_surplus"]
    ratio = ru / ro if ro != 0 else float("inf")
    results["competing"].append({"seed": seed, "ratio": round(ratio, 4),
        "rollup_nodes": alloc["rollup_owned"], "router_nodes": alloc["router_clients"],
        "market_nodes": alloc["market_nodes"],
        "rollup_net": ru, "router_net": ro})
    print(f"  seed={seed}: rollup={alloc['rollup_owned']:>3}  router={alloc['router_clients']:>3}  "
          f"market={alloc['market_nodes']:>3}  ratio={ratio:.2f}")
elapsed_c = time.time() - start
ratios_c = [r["ratio"] for r in results["competing"]]
router_final = [r["router_nodes"] for r in results["competing"]]
print(f"\n  Competing: mean_ratio={np.mean(ratios_c):.3f}  "
      f"router_extinct={sum(1 for n in router_final if n <= 1)}/50  "
      f"mean_router_nodes={np.mean(router_final):.1f}  ({elapsed_c:.0f}s)")

# Save
with open("output/robustness_50seeds_200nodes.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nTotal time: {elapsed_p + elapsed_c:.0f}s")
print("Results saved to output/robustness_50seeds_200nodes.json")
