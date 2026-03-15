"""Test F Ablation Runner

Ablation experiments + additional experiments (ownership density sweep, router visibility
sensitivity) comparing three institutional forms under different configurations.
"""
from __future__ import annotations

import argparse
import json
import os
from dataclasses import replace
from typing import Dict, List

from simulation import (
    OUTPUT_DIR,
    SimulationSettings,
    run_test_f,
)


# ---------------------------------------------------------------------------
# Experiment Definitions
# ---------------------------------------------------------------------------

EXPERIMENTS: Dict[str, Dict] = {
    "baseline": {
        "description": "All channels on (except complementarity)",
        "overrides": {},
    },
    "low_tx_costs": {
        "description": "Market/router actuator multipliers raised near rollup level",
        "overrides": {
            "actuator_mult_market": 0.9,
            "actuator_mult_router": 0.95,
        },
    },
    "leakage_off": {
        "description": "Leakage channel disabled",
        "overrides": {"leakage_on": False},
    },
    "trust_context_off": {
        "description": "Trust-generated context disabled",
        "overrides": {"trust_generated_context_on": False},
    },
    "actuator_off": {
        "description": "Actuator access equalized across regimes",
        "overrides": {"actuator_access_on": False},
    },
    "learning_off": {
        "description": "Cross-node learning disabled (rollup learns at router speed)",
        "overrides": {"cross_node_learning_on": False},
    },
    "complementarity_on": {
        "description": "Complementarity channel enabled (a5=0.5)",
        "overrides": {
            "complementarity_on": True,
            "a5": 0.5,
        },
    },
    "all_off": {
        "description": "All channels off — sanity check (regimes should converge)",
        "overrides": {
            "leakage_on": False,
            "trust_generated_context_on": False,
            "actuator_access_on": False,
            "cross_node_learning_on": False,
            "complementarity_on": False,
            "endogenous_acquisition_on": False,
            "initial_owned_count": 0,
        },
    },
    "router_no_shielding": {
        "description": "Router visibility = market (platforms don't shield info at all)",
        "overrides": {"visibility_router": 1.0},
    },
}


def run_density_sweep(base: SimulationSettings) -> Dict:
    """Sweep ownership density from 10% to 70% with fixed owned sets (no acquisition)."""
    n = base.num_nodes
    densities = [0.1, 0.2, 0.3, 0.5, 0.7]
    rows = []

    print("\n" + "=" * 60)
    print("  OWNERSHIP DENSITY SWEEP")
    print("=" * 60)

    for frac in densities:
        owned_count = max(1, round(n * frac))
        settings = build_settings(base, {
            "initial_owned_count": owned_count,
            "endogenous_acquisition_on": False,
        })
        results = run_test_f(settings, write_artifacts=True, prefix=f"test_f_density_{int(frac*100)}")
        rr = results["regime_results"]

        rollup_s = rr["rollup"]["total_surplus"]
        router_s = rr["router"]["total_surplus"]
        market_s = rr["market"]["total_surplus"]

        rows.append({
            "ownership_pct": int(frac * 100),
            "owned_count": owned_count,
            "market_surplus": market_s,
            "router_surplus": router_s,
            "rollup_surplus": rollup_s,
            "rollup_vs_router": round(rollup_s / router_s, 4) if router_s != 0 else None,
            "rollup_vs_market": round(rollup_s / market_s, 4) if market_s != 0 else None,
            "rollup_leakage": rr["rollup"]["avg_leakage_cost"],
            "superlinearity": results["superlinearity"].get("superlinearity_ratio"),
            "P1": results["propositions"]["P1_rollup_highest_surplus"],
        })

        print(f"  {int(frac*100)}% owned ({owned_count} nodes): "
              f"rollup/router={rows[-1]['rollup_vs_router']}")

    return {"density_sweep": rows}


def run_ownership_cost_sweep(base: SimulationSettings) -> Dict:
    """Sweep ownership costs to find break-even point."""
    costs = [0.0, 0.025, 0.05, 0.075, 0.10, 0.15, 0.20, 0.30]
    rows = []

    print("\n" + "=" * 60)
    print("  OWNERSHIP COST SWEEP")
    print("=" * 60)

    for cost in costs:
        settings = build_settings(base, {"ownership_cost_per_node": cost})
        results = run_test_f(settings, write_artifacts=False)
        rr = results["regime_results"]
        rollup_net = rr["rollup"]["total_surplus"]
        rollup_gross = rr["rollup"]["gross_surplus"]
        own_cost = rr["rollup"]["ownership_cost"]
        router_s = rr["router"]["total_surplus"]

        rows.append({
            "cost_per_node": cost,
            "rollup_gross": rollup_gross,
            "ownership_cost": own_cost,
            "rollup_net": rollup_net,
            "router_surplus": router_s,
            "rollup_vs_router": round(rollup_net / router_s, 4) if router_s != 0 else None,
            "P1": results["propositions"]["P1_rollup_highest_surplus"],
        })

        status = "PASS" if rollup_net > router_s else "FAIL"
        print(f"  cost={cost:.3f}  rollup_net={rollup_net:>8.1f}  router={router_s:>8.1f}  {status}")

    return {"ownership_cost_sweep": rows}


def build_settings(base: SimulationSettings, overrides: Dict) -> SimulationSettings:
    """Create a new SimulationSettings with overrides applied."""
    params = {k: v for k, v in base.__dict__.items()}
    params.update(overrides)
    return SimulationSettings(**params)


def run_ablations(
    base_settings: SimulationSettings | None = None,
    experiments: Dict[str, Dict] | None = None,
) -> Dict:
    """Run all ablation experiments and return cross-experiment comparison."""
    base = base_settings or SimulationSettings()
    exps = experiments or EXPERIMENTS

    all_results = {}
    summary_rows = []

    for name, config in exps.items():
        print(f"\n{'='*60}")
        print(f"  Experiment: {name}")
        print(f"  {config['description']}")
        print(f"{'='*60}")

        settings = build_settings(base, config["overrides"])
        results = run_test_f(settings, write_artifacts=True, prefix=f"test_f_{name}")
        all_results[name] = results

        # Collect summary row
        rr = results["regime_results"]
        for regime in ["market", "router", "rollup"]:
            summary_rows.append({
                "experiment": name,
                "regime": regime,
                "total_surplus": rr[regime]["total_surplus"],
                "avg_match_quality": rr[regime]["avg_match_quality"],
                "avg_leakage_cost": rr[regime]["avg_leakage_cost"],
                "final_policy_quality": rr[regime]["final_policy_quality"],
                "num_owned": rr[regime]["num_owned"],
            })

    # Cross-experiment analysis
    analysis = _analyze_ablations(all_results)

    # Density sweep
    density_results = run_density_sweep(base)

    # Ownership cost sweep
    cost_results = run_ownership_cost_sweep(base)

    output = {
        "experiments": {
            name: {
                "description": exps.get(name, {}).get("description", ""),
                "regime_results": all_results[name]["regime_results"],
                "comparisons": all_results[name]["comparisons"],
                "propositions": all_results[name]["propositions"],
                "superlinearity": all_results[name]["superlinearity"],
            }
            for name in all_results
        },
        "summary_rows": summary_rows,
        "analysis": analysis,
        "density_sweep": density_results["density_sweep"],
        "ownership_cost_sweep": cost_results["ownership_cost_sweep"],
    }

    # Write combined output
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    json_path = os.path.join(OUTPUT_DIR, "test_f_ablations.json")
    with open(json_path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    md = _render_ablation_markdown(output)
    md_path = os.path.join(OUTPUT_DIR, "test_f_ablations.md")
    with open(md_path, "w") as f:
        f.write(md)

    print(f"\nResults written to {json_path} and {md_path}")
    return output


def _analyze_ablations(all_results: Dict) -> Dict:
    """Analyze cross-experiment patterns."""
    analysis = {}

    baseline = all_results.get("baseline")
    if not baseline:
        return analysis

    bl_rr = baseline["regime_results"]
    bl_rollup = bl_rr["rollup"]["total_surplus"]
    bl_router = bl_rr["router"]["total_surplus"]
    bl_market = bl_rr["market"]["total_surplus"]

    bl_ratio = bl_rollup / bl_router if bl_router != 0 else None

    # For each ablation, compute how rollup-vs-router ratio changes
    ratio_changes = {}
    for name, results in all_results.items():
        if name == "baseline":
            continue
        rr = results["regime_results"]
        rollup_s = rr["rollup"]["total_surplus"]
        router_s = rr["router"]["total_surplus"]
        ratio = rollup_s / router_s if router_s != 0 else None
        ratio_changes[name] = {
            "rollup_vs_router_ratio": round(ratio, 4) if ratio else None,
            "ratio_change_from_baseline": round(ratio - bl_ratio, 4) if ratio and bl_ratio else None,
        }

    analysis["ratio_changes"] = ratio_changes

    # Sanity check: all_off should produce similar surplus
    all_off = all_results.get("all_off")
    if all_off:
        ao_rr = all_off["regime_results"]
        surpluses = [ao_rr[r]["total_surplus"] for r in ["market", "router", "rollup"]]
        if min(surpluses) > 0:
            max_ratio = max(surpluses) / min(surpluses)
            analysis["all_off_sanity"] = {
                "max_min_ratio": round(max_ratio, 4),
                "pass": max_ratio < 1.3,  # Within 30% is reasonable convergence
            }

    # Complementarity effect
    comp_on = all_results.get("complementarity_on")
    if comp_on:
        comp_sup = comp_on["superlinearity"]
        bl_sup = baseline["superlinearity"]
        analysis["complementarity_effect"] = {
            "baseline_superlinearity": bl_sup.get("superlinearity_ratio"),
            "with_complementarity_superlinearity": comp_sup.get("superlinearity_ratio"),
        }

    return analysis


def _render_ablation_markdown(output: Dict) -> str:
    """Render ablation results as markdown."""
    lines = ["# Test F: Ablation Results\n"]

    # Summary table
    lines.append("## Cross-Experiment Surplus Comparison\n")
    lines.append("| Experiment | Market | Router | Rollup | Rollup/Router |")
    lines.append("|---|---|---|---|---|")

    for name, exp in output["experiments"].items():
        rr = exp["regime_results"]
        m = rr["market"]["total_surplus"]
        ro = rr["router"]["total_surplus"]
        ru = rr["rollup"]["total_surplus"]
        ratio = round(ru / ro, 4) if ro != 0 else "N/A"
        lines.append(f"| {name} | {m} | {ro} | {ru} | {ratio} |")

    # Proposition verdicts across experiments
    lines.append("\n## Proposition Verdicts Across Experiments\n")
    prop_keys = ["P1_rollup_highest_surplus", "P2_leakage_advantage",
                 "P3_trust_context_ownership", "P4_cross_node_learning",
                 "P5_superlinearity_emergent"]
    header = "| Experiment | " + " | ".join(k.split("_", 1)[0] for k in prop_keys) + " |"
    lines.append(header)
    lines.append("|---" * (len(prop_keys) + 1) + "|")
    for name, exp in output["experiments"].items():
        props = exp["propositions"]
        vals = " | ".join("PASS" if props.get(k) else "FAIL" for k in prop_keys)
        lines.append(f"| {name} | {vals} |")

    # Analysis
    analysis = output.get("analysis", {})
    if analysis.get("ratio_changes"):
        lines.append("\n## Rollup/Router Ratio Changes from Baseline\n")
        lines.append("| Experiment | Ratio | Change |")
        lines.append("|---|---|---|")
        for name, rc in analysis["ratio_changes"].items():
            lines.append(f"| {name} | {rc['rollup_vs_router_ratio']} | {rc['ratio_change_from_baseline']} |")

    if analysis.get("all_off_sanity"):
        san = analysis["all_off_sanity"]
        lines.append(f"\n## All-Off Sanity Check\n")
        lines.append(f"- Max/min surplus ratio: {san['max_min_ratio']}")
        lines.append(f"- Pass (< 1.3): {'YES' if san['pass'] else 'NO'}")

    if analysis.get("complementarity_effect"):
        ce = analysis["complementarity_effect"]
        lines.append(f"\n## Complementarity Effect on Superlinearity\n")
        lines.append(f"- Baseline superlinearity ratio: {ce['baseline_superlinearity']}")
        lines.append(f"- With complementarity: {ce['with_complementarity_superlinearity']}")

    # Density sweep
    density = output.get("density_sweep", [])
    if density:
        lines.append("\n## Ownership Density Sweep\n")
        lines.append("| Ownership % | Nodes | Rollup | Router | Market | Rollup/Router | Rollup/Market | Leakage | Superlinearity | P1 |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|")
        for row in density:
            lines.append(
                f"| {row['ownership_pct']}% | {row['owned_count']} "
                f"| {row['rollup_surplus']} | {row['router_surplus']} | {row['market_surplus']} "
                f"| {row['rollup_vs_router']} | {row['rollup_vs_market']} "
                f"| {row['rollup_leakage']} | {row['superlinearity']} "
                f"| {'PASS' if row['P1'] else 'FAIL'} |"
            )

    # Ownership cost sweep
    cost_sweep = output.get("ownership_cost_sweep", [])
    if cost_sweep:
        lines.append("\n## Ownership Cost Sensitivity\n")
        lines.append("| Cost/Node/Step | Rollup Gross | Ownership Cost | Rollup Net | Router | Rollup/Router | P1 |")
        lines.append("|---|---|---|---|---|---|---|")
        for row in cost_sweep:
            lines.append(
                f"| {row['cost_per_node']} | {row['rollup_gross']} | {row['ownership_cost']} "
                f"| {row['rollup_net']} | {row['router_surplus']} "
                f"| {row['rollup_vs_router']} | {'PASS' if row['P1'] else 'FAIL'} |"
            )

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test F Ablation Runner")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--time-steps", type=int, default=50)
    parser.add_argument("--num-nodes", type=int, default=30)
    args = parser.parse_args()

    base = SimulationSettings(
        seed=args.seed,
        time_steps=args.time_steps,
        num_nodes=args.num_nodes,
    )
    results = run_ablations(base)

    # Print summary
    print("\n" + "=" * 70)
    print("ABLATION SUMMARY")
    print("=" * 70)
    for name, exp in results["experiments"].items():
        rr = exp["regime_results"]
        ru = rr["rollup"]["total_surplus"]
        ro = rr["router"]["total_surplus"]
        ratio = round(ru / ro, 3) if ro != 0 else "N/A"
        print(f"  {name:<25s}  rollup={ru:>10.1f}  router={ro:>10.1f}  ratio={ratio}")
