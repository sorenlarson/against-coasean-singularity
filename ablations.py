"""Test F Ablation Runner

Ablation experiments + additional experiments (ownership density sweep, router visibility
sensitivity, subscription cost sweep, competing-world scenarios, industry parameter sweep)
comparing four institutional forms under different configurations.
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
    run_competing_world,
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


def run_shapley_decomposition(base: SimulationSettings) -> Dict:
    """Shapley value decomposition of channel contributions.

    Instead of pure ablation (remove one channel, measure change), Shapley
    computes each channel's marginal contribution averaged over ALL possible
    orderings of channel addition. This properly handles interaction effects
    and the contributions sum exactly to the total difference.
    """
    import itertools
    import math

    # Define channels and their on/off settings
    channels = {
        "learning": {"cross_node_learning_on": True},
        "leakage": {"leakage_on": True},
        "trust": {"trust_generated_context_on": True},
        "actuator": {"actuator_access_on": True},
        "foreclosure": {"foreclosure_blend_scale": 0.4},
        "router_leak": {"router_learning_leakage": 0.15},
    }
    off_values = {
        "learning": {"cross_node_learning_on": False},
        "leakage": {"leakage_on": False},
        "trust": {"trust_generated_context_on": False},
        "actuator": {"actuator_access_on": False},
        "foreclosure": {"foreclosure_blend_scale": 0.0},
        "router_leak": {"router_learning_leakage": 0.0},
    }

    channel_names = list(channels.keys())
    n = len(channel_names)

    print("\n" + "=" * 60)
    print("  SHAPLEY VALUE DECOMPOSITION")
    print(f"  {n} channels, {2**n} coalitions")
    print("=" * 60)

    # Evaluate all 2^n coalitions
    coalition_values = {}
    for i in range(2**n):
        # Which channels are on?
        active = set()
        for j, name in enumerate(channel_names):
            if i & (1 << j):
                active.add(name)

        # Build settings: start with all off, turn on active channels
        overrides = {}
        for name in channel_names:
            if name in active:
                overrides.update(channels[name])
            else:
                overrides.update(off_values[name])
        # Also disable acquisition and set initial_owned_count=0 for all-off base
        overrides["initial_owned_count"] = base.initial_owned_count
        overrides["endogenous_acquisition_on"] = base.endogenous_acquisition_on

        settings = build_settings(base, overrides)
        results = run_test_f(settings, write_artifacts=False)
        rr = results["regime_results"]

        rollup = rr["rollup"]["total_surplus"]
        router = rr["router"]["total_surplus"]
        ratio = rollup / router if router != 0 else 0.0

        coalition_key = frozenset(active)
        coalition_values[coalition_key] = ratio

        active_str = ",".join(sorted(active)) if active else "(none)"
        print(f"  [{i+1:>2}/{2**n}] {active_str:<50s} ratio={ratio:.4f}")

    # Compute Shapley values
    shapley = {}
    for name in channel_names:
        sv = 0.0
        others = [c for c in channel_names if c != name]
        # Iterate over all subsets of other channels
        for size in range(n):
            for subset in itertools.combinations(others, size):
                S = frozenset(subset)
                S_with = S | {name}
                # Marginal contribution of adding this channel to S
                marginal = coalition_values[S_with] - coalition_values[S]
                # Weight: |S|!(n-|S|-1)! / n!
                weight = math.factorial(len(S)) * math.factorial(n - len(S) - 1) / math.factorial(n)
                sv += weight * marginal
        shapley[name] = round(sv, 4)

    # Verify: sum should equal total effect
    all_on = coalition_values[frozenset(channel_names)]
    all_off = coalition_values[frozenset()]
    total_effect = round(all_on - all_off, 4)
    shapley_sum = round(sum(shapley.values()), 4)

    print(f"\n  Shapley values (sum to total effect):")
    for name in sorted(shapley, key=lambda k: shapley[k], reverse=True):
        print(f"    {name:<15s} {shapley[name]:>+.4f}")
    print(f"    {'---':<15s} {'---':>6s}")
    print(f"    {'SUM':<15s} {shapley_sum:>+.4f}")
    print(f"    {'Total effect':<15s} {total_effect:>+.4f}")
    print(f"    {'All-on ratio':<15s} {all_on:.4f}")
    print(f"    {'All-off ratio':<15s} {all_off:.4f}")

    return {
        "shapley_values": shapley,
        "total_effect": total_effect,
        "shapley_sum": shapley_sum,
        "all_on_ratio": round(all_on, 4),
        "all_off_ratio": round(all_off, 4),
    }


def run_subscription_cost_sweep(base: SimulationSettings) -> Dict:
    """Sweep subscription cost for isolated router to find crossover with router."""
    costs = [0.0, 0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15]
    rows = []

    print("\n" + "=" * 60)
    print("  SUBSCRIPTION COST SWEEP (Isolated Router)")
    print("=" * 60)

    for cost in costs:
        settings = build_settings(base, {"subscription_cost_per_node": cost})
        results = run_test_f(settings, write_artifacts=False)
        rr = results["regime_results"]
        iso_s = rr["isolated_router"]["total_surplus"]
        router_s = rr["router"]["total_surplus"]
        rollup_s = rr["rollup"]["total_surplus"]

        rows.append({
            "subscription_cost": cost,
            "isolated_router_surplus": iso_s,
            "router_surplus": router_s,
            "rollup_surplus": rollup_s,
            "iso_vs_router": round(iso_s / router_s, 4) if router_s != 0 else None,
            "iso_vs_rollup": round(iso_s / rollup_s, 4) if rollup_s != 0 else None,
        })

        status = "BEATS_ROUTER" if iso_s > router_s else "BELOW_ROUTER"
        print(f"  cost={cost:.3f}  iso={iso_s:>8.1f}  router={router_s:>8.1f}  rollup={rollup_s:>8.1f}  {status}")

    return {"subscription_cost_sweep": rows}


def run_competing_scenarios(base: SimulationSettings) -> Dict:
    """Run competing-world simulation under three router strategies."""
    strategies = ["passive", "data_isolation", "full_defensive"]
    results = {}

    print("\n" + "=" * 60)
    print("  COMPETING-WORLD SCENARIOS")
    print("=" * 60)

    for strategy in strategies:
        settings = build_settings(base, {"router_strategy": strategy})
        scenario = run_competing_world(settings)

        results[strategy] = {
            "regimes": {
                name: scenario[name] for name in ["market", "router", "isolated_router", "rollup"]
            },
            "final_allocation": scenario["final_allocation"],
        }

        print(f"\n  Strategy: {strategy}")
        for name in ["market", "router", "isolated_router", "rollup"]:
            r = scenario[name]
            print(f"    {name:<17} surplus={r['total_surplus']:>8.1f}  coords={r['total_coordinations']:>5}  nodes={r['num_nodes']:>3}")
        alloc = scenario["final_allocation"]
        print(f"    Final: rollup={alloc['rollup_owned']} router={alloc['router_clients']} "
              f"iso={alloc['isolated_router_clients']} market={alloc['market_nodes']}")

    return {"competing_scenarios": results}


def run_industry_sweep(base: SimulationSettings) -> Dict:
    """Sweep industry-specific parameters to map parameter space to regime dominance.

    Full services taxonomy from Bek (2026), "Services: The New Software" (Sequoia),
    organized by quadrant: autopilot territory, copilot territory, watch, and next wave.
    Parameters vary leakage persistence (rho_L), leakage sensitivity bounds, and
    cross-node transfer rate, calibrated from industry characteristics.
    """
    industries = {
        # === AUTOPILOT TERRITORY (outsourced, high intelligence) ===
        "legal_transactional": {
            "quadrant": "autopilot",
            "tam": "$20-25B",
            "description": "NDAs, contracts, reg filings — high durability, high specificity, low transfer",
            "overrides": {"rho_L": 0.95, "leakage_sensitivity_low": 0.60, "leakage_sensitivity_high": 0.95, "transfer_rate": 0.005},
        },
        "paralegal_lpo": {
            "quadrant": "autopilot",
            "tam": "$36B",
            "description": "Document review, discovery — high durability, high specificity, low transfer",
            "overrides": {"rho_L": 0.90, "leakage_sensitivity_low": 0.55, "leakage_sensitivity_high": 0.90, "transfer_rate": 0.008},
        },
        "tax_advisory": {
            "quadrant": "autopilot",
            "tam": "$30-35B",
            "description": "Multi-jurisdiction compliance, planning — high durability, high specificity",
            "overrides": {"rho_L": 0.90, "leakage_sensitivity_low": 0.50, "leakage_sensitivity_high": 0.85, "transfer_rate": 0.01},
        },
        "accounting_audit": {
            "quadrant": "autopilot",
            "tam": "$50-80B",
            "description": "Book closing, financial statements, audit — high durability, high specificity",
            "overrides": {"rho_L": 0.85, "leakage_sensitivity_low": 0.45, "leakage_sensitivity_high": 0.80, "transfer_rate": 0.015},
        },
        "kyc_aml": {
            "quadrant": "autopilot",
            "tam": "$30-50B",
            "description": "Identity verification, sanctions screening, SAR — high durability, high specificity",
            "overrides": {"rho_L": 0.80, "leakage_sensitivity_low": 0.40, "leakage_sensitivity_high": 0.75, "transfer_rate": 0.02},
        },
        "cost_estimation": {
            "quadrant": "autopilot",
            "tam": "$16B",
            "description": "Project cost estimates, material pricing — moderate durability, moderate specificity",
            "overrides": {"rho_L": 0.60, "leakage_sensitivity_low": 0.30, "leakage_sensitivity_high": 0.60, "transfer_rate": 0.025},
        },
        "insurance_brokerage": {
            "quadrant": "autopilot",
            "tam": "$140-200B",
            "description": "Carrier shopping, form-filling — moderate durability, moderate specificity, high transfer",
            "overrides": {"rho_L": 0.60, "leakage_sensitivity_low": 0.20, "leakage_sensitivity_high": 0.50, "transfer_rate": 0.035},
        },
        "claims_adjusting": {
            "quadrant": "autopilot",
            "tam": "$50-80B",
            "description": "Policy interpretation, damage schedules, reserves — moderate durability, moderate specificity",
            "overrides": {"rho_L": 0.55, "leakage_sensitivity_low": 0.25, "leakage_sensitivity_high": 0.55, "transfer_rate": 0.035},
        },
        "mortgage_origination": {
            "quadrant": "autopilot",
            "tam": "$30-50B",
            "description": "Application processing, underwriting, docs — moderate durability, moderate specificity",
            "overrides": {"rho_L": 0.55, "leakage_sensitivity_low": 0.25, "leakage_sensitivity_high": 0.55, "transfer_rate": 0.035},
        },
        "healthcare_rev_cycle": {
            "quadrant": "autopilot",
            "tam": "$50-80B",
            "description": "Medical coding (ICD-10), billing, denials — moderate durability, low-mod specificity, high transfer",
            "overrides": {"rho_L": 0.50, "leakage_sensitivity_low": 0.15, "leakage_sensitivity_high": 0.45, "transfer_rate": 0.04},
        },
        "payroll_compliance": {
            "quadrant": "autopilot",
            "tam": "$50-70B",
            "description": "Payroll processing, tax withholding, filings — moderate durability, moderate specificity, high transfer",
            "overrides": {"rho_L": 0.50, "leakage_sensitivity_low": 0.15, "leakage_sensitivity_high": 0.40, "transfer_rate": 0.04},
        },
        "real_estate_closing": {
            "quadrant": "autopilot",
            "tam": "$20-25B",
            "description": "Title search, escrow, closing — moderate durability, moderate specificity, high transfer",
            "overrides": {"rho_L": 0.50, "leakage_sensitivity_low": 0.20, "leakage_sensitivity_high": 0.50, "transfer_rate": 0.035},
        },
        "it_managed_services": {
            "quadrant": "autopilot",
            "tam": "$100B+",
            "description": "Patching, monitoring, provisioning — low durability, low specificity, very high transfer",
            "overrides": {"rho_L": 0.30, "leakage_sensitivity_low": 0.05, "leakage_sensitivity_high": 0.25, "transfer_rate": 0.045},
        },
        # === COPILOT TERRITORY (insourced, high judgement) ===
        "management_consulting": {
            "quadrant": "copilot",
            "tam": "$300B+",
            "description": "Strategy, org design — high durability, high specificity, low transfer",
            "overrides": {"rho_L": 0.85, "leakage_sensitivity_low": 0.50, "leakage_sensitivity_high": 0.85, "transfer_rate": 0.01},
        },
        "executive_search": {
            "quadrant": "copilot",
            "tam": "$20B+",
            "description": "C-suite recruitment, board placement — high durability, high specificity",
            "overrides": {"rho_L": 0.80, "leakage_sensitivity_low": 0.50, "leakage_sensitivity_high": 0.80, "transfer_rate": 0.01},
        },
        "pr_comms": {
            "quadrant": "copilot",
            "tam": "$20B+",
            "description": "Media relations, crisis mgmt, messaging — moderate durability, moderate specificity",
            "overrides": {"rho_L": 0.50, "leakage_sensitivity_low": 0.25, "leakage_sensitivity_high": 0.55, "transfer_rate": 0.025},
        },
        "graphic_ux_design": {
            "quadrant": "copilot",
            "tam": "$30B+",
            "description": "Visual design, user experience — low durability, low specificity, high transfer",
            "overrides": {"rho_L": 0.30, "leakage_sensitivity_low": 0.10, "leakage_sensitivity_high": 0.30, "transfer_rate": 0.04},
        },
        # === WATCH (mixed, medium intelligence) ===
        "recruitment_staffing": {
            "quadrant": "watch",
            "tam": "$200B+",
            "description": "Screening, matching, outreach — moderate durability, moderate specificity, high transfer",
            "overrides": {"rho_L": 0.50, "leakage_sensitivity_low": 0.20, "leakage_sensitivity_high": 0.50, "transfer_rate": 0.035},
        },
        "freight_brokerage": {
            "quadrant": "watch",
            "tam": "$100B+",
            "description": "Load matching, rate negotiation — low durability, moderate specificity, high transfer",
            "overrides": {"rho_L": 0.35, "leakage_sensitivity_low": 0.20, "leakage_sensitivity_high": 0.50, "transfer_rate": 0.04},
        },
        "advertising": {
            "quadrant": "watch",
            "tam": "$100B+",
            "description": "Media buying, campaign optimization — low durability, moderate specificity, high transfer",
            "overrides": {"rho_L": 0.35, "leakage_sensitivity_low": 0.15, "leakage_sensitivity_high": 0.45, "transfer_rate": 0.035},
        },
        "clinical_trials_cro": {
            "quadrant": "watch",
            "tam": "$80B+",
            "description": "Protocol execution, data mgmt — high durability, high specificity, moderate transfer",
            "overrides": {"rho_L": 0.85, "leakage_sensitivity_low": 0.45, "leakage_sensitivity_high": 0.80, "transfer_rate": 0.015},
        },
        "admin_assistants": {
            "quadrant": "watch",
            "tam": "$80B+",
            "description": "Scheduling, email, travel — low durability, low specificity, very high transfer",
            "overrides": {"rho_L": 0.25, "leakage_sensitivity_low": 0.05, "leakage_sensitivity_high": 0.20, "transfer_rate": 0.045},
        },
        "erp_implementation": {
            "quadrant": "watch",
            "tam": "$50B+",
            "description": "System configuration, data migration — high durability, high specificity, moderate transfer",
            "overrides": {"rho_L": 0.75, "leakage_sensitivity_low": 0.40, "leakage_sensitivity_high": 0.70, "transfer_rate": 0.02},
        },
        "seo_sem": {
            "quadrant": "watch",
            "tam": "$50B+",
            "description": "Keyword research, bid management — low durability, moderate specificity, high transfer",
            "overrides": {"rho_L": 0.35, "leakage_sensitivity_low": 0.20, "leakage_sensitivity_high": 0.45, "transfer_rate": 0.04},
        },
        "corporate_training": {
            "quadrant": "watch",
            "tam": "$50B+",
            "description": "Course design, delivery — low durability, low specificity, very high transfer",
            "overrides": {"rho_L": 0.30, "leakage_sensitivity_low": 0.05, "leakage_sensitivity_high": 0.25, "transfer_rate": 0.045},
        },
        "market_research": {
            "quadrant": "watch",
            "tam": "$45B",
            "description": "Surveys, analysis, reporting — moderate durability, moderate specificity",
            "overrides": {"rho_L": 0.60, "leakage_sensitivity_low": 0.30, "leakage_sensitivity_high": 0.60, "transfer_rate": 0.025},
        },
        "cybersecurity": {
            "quadrant": "watch",
            "tam": "$30B+",
            "description": "Vuln assessment, monitoring, incident response — high durability, high specificity",
            "overrides": {"rho_L": 0.85, "leakage_sensitivity_low": 0.50, "leakage_sensitivity_high": 0.85, "transfer_rate": 0.02},
        },
        "architecture": {
            "quadrant": "watch",
            "tam": "$25B+",
            "description": "Building design, planning — moderate durability, moderate specificity",
            "overrides": {"rho_L": 0.60, "leakage_sensitivity_low": 0.25, "leakage_sensitivity_high": 0.55, "transfer_rate": 0.025},
        },
        "patent_ip": {
            "quadrant": "watch",
            "tam": "$15-20B",
            "description": "Patent drafting, prosecution, IP strategy — high durability, very high specificity",
            "overrides": {"rho_L": 0.95, "leakage_sensitivity_low": 0.60, "leakage_sensitivity_high": 0.95, "transfer_rate": 0.005},
        },
        "travel_management": {
            "quadrant": "watch",
            "tam": "$15B+",
            "description": "Booking, expense management — low durability, low specificity, very high transfer",
            "overrides": {"rho_L": 0.25, "leakage_sensitivity_low": 0.05, "leakage_sensitivity_high": 0.20, "transfer_rate": 0.045},
        },
        # === NEXT WAVE (moving insourced → outsourced) ===
        "supply_chain_procurement": {
            "quadrant": "next_wave",
            "tam": "$200B+",
            "description": "Supplier negotiation, contract mgmt — high durability, high specificity, moderate transfer",
            "overrides": {"rho_L": 0.75, "leakage_sensitivity_low": 0.40, "leakage_sensitivity_high": 0.75, "transfer_rate": 0.02},
        },
        "wealth_mgmt_ops": {
            "quadrant": "next_wave",
            "tam": "$30B+",
            "description": "Portfolio rebalancing, reporting, compliance — high durability, high specificity",
            "overrides": {"rho_L": 0.85, "leakage_sensitivity_low": 0.50, "leakage_sensitivity_high": 0.85, "transfer_rate": 0.01},
        },
        "pharmacy_back_office": {
            "quadrant": "next_wave",
            "tam": "$30B+",
            "description": "Prescription processing, insurance verification — moderate durability, moderate specificity",
            "overrides": {"rho_L": 0.60, "leakage_sensitivity_low": 0.30, "leakage_sensitivity_high": 0.60, "transfer_rate": 0.035},
        },
        "medical_admin": {
            "quadrant": "next_wave",
            "tam": "$20B+",
            "description": "Scheduling, referrals, authorizations — moderate durability, moderate specificity, high transfer",
            "overrides": {"rho_L": 0.55, "leakage_sensitivity_low": 0.25, "leakage_sensitivity_high": 0.55, "transfer_rate": 0.035},
        },
        "fund_administration": {
            "quadrant": "next_wave",
            "tam": "$15-20B",
            "description": "NAV calculation, investor reporting, compliance — high durability, high specificity",
            "overrides": {"rho_L": 0.85, "leakage_sensitivity_low": 0.50, "leakage_sensitivity_high": 0.80, "transfer_rate": 0.01},
        },
    }

    rows = []
    print("\n" + "=" * 60)
    print("  INDUSTRY PARAMETER SWEEP")
    print("=" * 60)

    for name, config in industries.items():
        settings = build_settings(base, config["overrides"])
        results = run_test_f(settings, write_artifacts=False)
        rr = results["regime_results"]

        market_s = rr["market"]["total_surplus"]
        router_s = rr["router"]["total_surplus"]
        iso_s = rr["isolated_router"]["total_surplus"]
        rollup_s = rr["rollup"]["total_surplus"]

        # Determine which regime dominates
        surpluses = {"market": market_s, "router": router_s,
                     "isolated_router": iso_s, "rollup": rollup_s}
        dominant = max(surpluses, key=surpluses.get)

        rows.append({
            "industry": name,
            "quadrant": config.get("quadrant", ""),
            "tam": config.get("tam", ""),
            "description": config["description"],
            "rho_L": config["overrides"]["rho_L"],
            "leakage_sensitivity_low": config["overrides"]["leakage_sensitivity_low"],
            "leakage_sensitivity_high": config["overrides"]["leakage_sensitivity_high"],
            "transfer_rate": config["overrides"]["transfer_rate"],
            "market_surplus": market_s,
            "router_surplus": router_s,
            "isolated_router_surplus": iso_s,
            "rollup_surplus": rollup_s,
            "dominant_regime": dominant,
            "rollup_vs_router": round(rollup_s / router_s, 4) if router_s != 0 else None,
        })

        print(f"  {name:<20s} dominant={dominant:<17s} "
              f"rollup={rollup_s:>8.1f} router={router_s:>8.1f} iso={iso_s:>8.1f} market={market_s:>8.1f}")

    return {"industry_sweep": rows}


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
        for regime in ["market", "router", "isolated_router", "rollup"]:
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

    # Shapley decomposition
    shapley_results = run_shapley_decomposition(base)

    # Subscription cost sweep
    subscription_results = run_subscription_cost_sweep(base)

    # Competing-world scenarios
    competing_results = run_competing_scenarios(base)

    # Industry parameter sweep
    industry_results = run_industry_sweep(base)

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
        "shapley": shapley_results,
        "subscription_cost_sweep": subscription_results["subscription_cost_sweep"],
        "competing_scenarios": competing_results["competing_scenarios"],
        "industry_sweep": industry_results["industry_sweep"],
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
    lines.append("| Experiment | Market | Router | Isolated Router | Rollup | Rollup/Router |")
    lines.append("|---|---|---|---|---|---|")

    for name, exp in output["experiments"].items():
        rr = exp["regime_results"]
        m = rr["market"]["total_surplus"]
        ro = rr["router"]["total_surplus"]
        ir = rr["isolated_router"]["total_surplus"]
        ru = rr["rollup"]["total_surplus"]
        ratio = round(ru / ro, 4) if ro != 0 else "N/A"
        lines.append(f"| {name} | {m} | {ro} | {ir} | {ru} | {ratio} |")

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

    # Shapley decomposition
    shapley = output.get("shapley", {})
    if shapley.get("shapley_values"):
        lines.append("\n## Shapley Value Decomposition\n")
        lines.append("Channel contributions to rollup/router ratio, accounting for interaction effects.\n")
        lines.append("| Channel | Shapley Value |")
        lines.append("|---|---|")
        sv = shapley["shapley_values"]
        for name in sorted(sv, key=lambda k: sv[k], reverse=True):
            lines.append(f"| {name} | {sv[name]:+.4f} |")
        lines.append(f"| **Sum** | **{shapley['shapley_sum']:+.4f}** |")
        lines.append(f"| **Total effect** | **{shapley['total_effect']:+.4f}** |")
        lines.append(f"\n- All-on ratio: {shapley['all_on_ratio']}")
        lines.append(f"- All-off ratio: {shapley['all_off_ratio']}")

    # Subscription cost sweep
    sub_sweep = output.get("subscription_cost_sweep", [])
    if sub_sweep:
        lines.append("\n## Subscription Cost Sweep (Isolated Router)\n")
        lines.append("| Sub Cost | Isolated Router | Router | Rollup | Iso/Router |")
        lines.append("|---|---|---|---|---|")
        for row in sub_sweep:
            lines.append(
                f"| {row['subscription_cost']} | {row['isolated_router_surplus']} "
                f"| {row['router_surplus']} | {row['rollup_surplus']} "
                f"| {row['iso_vs_router']} |"
            )

    # Competing-world scenarios
    scenarios = output.get("competing_scenarios", {})
    if scenarios:
        lines.append("\n## Competing-World Scenarios\n")
        for strategy, data in scenarios.items():
            lines.append(f"\n### Strategy: {strategy}\n")
            lines.append("| Regime | Surplus | Coordinations | Nodes |")
            lines.append("|---|---|---|---|")
            for name in ["market", "router", "isolated_router", "rollup"]:
                r = data["regimes"][name]
                lines.append(f"| {name} | {r['total_surplus']} | {r['total_coordinations']} | {r['num_nodes']} |")
            alloc = data["final_allocation"]
            lines.append(f"\nFinal: rollup={alloc['rollup_owned']} router={alloc['router_clients']} "
                        f"iso={alloc['isolated_router_clients']} market={alloc['market_nodes']}")

    # Industry sweep
    ind_sweep = output.get("industry_sweep", [])
    if ind_sweep:
        lines.append("\n## Industry Parameter Sweep\n")
        lines.append("| Industry | rho_L | Leak Sens | Transfer | Market | Router | Iso Router | Rollup | Dominant |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for row in ind_sweep:
            lines.append(
                f"| {row['industry']} | {row['rho_L']} "
                f"| {row['leakage_sensitivity_low']}-{row['leakage_sensitivity_high']} "
                f"| {row['transfer_rate']} "
                f"| {row['market_surplus']} | {row['router_surplus']} "
                f"| {row['isolated_router_surplus']} | {row['rollup_surplus']} "
                f"| {row['dominant_regime']} |"
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
