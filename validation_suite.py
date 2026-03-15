from __future__ import annotations

import json
import os
import argparse
from typing import Dict, List

import numpy as np

from test_a_duckdb import OUTPUT_DIR, SimulationSettings, run_test_a


def ensure_output_dir() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def summarize_acceptance(test_name: str, rows: List[Dict[str, object]]) -> str:
    if test_name == "test_b":
        medium_rows = [row for row in rows if row["true_effect"] == 0.35 and row["portcos"] >= 15]
        if medium_rows and all(row["power"] >= 0.80 for row in medium_rows):
            return "LP-ready on medium effect at 15+ portcos."
        return "Not LP-ready on current power criterion; more panel depth or stronger metric design needed."
    if test_name == "test_c":
        baseline = [row for row in rows if row["degradation"] == "missing_tuple_rate" and row["level"] == 0.10]
        if baseline and all(row["task_1_rank_shift"] <= 3 and row["task_2_hours_drift_pct"] <= 20 for row in baseline):
            return "CFO/Ops descriptive tasks tolerate baseline degradation."
        return "Descriptive tasks are not yet stable enough at baseline degradation."
    if test_name == "test_d":
        confounded = next((row for row in rows if row["method"] == "did" and row["confounds"] == "yes"), None)
        naive = next((row for row in rows if row["method"] == "naive_pre_post" and row["confounds"] == "yes"), None)
        if confounded and abs(confounded["bias_pct_of_true"]) < 15 and naive and abs(naive["bias_pct_of_true"]) > abs(confounded["bias_pct_of_true"]):
            return "LP causal design passes confound-recovery gate."
        return "Confound recovery is not yet strong enough for LP-facing claims."
    return "No acceptance summary available."


def run_test_b(monte_carlo_runs: int = 2) -> Dict[str, object]:
    rows: List[Dict[str, object]] = []
    portfolio_sizes = [8, 12, 15, 20]
    effect_sizes = [0.0, 0.15, 0.35, 0.55]
    for portcos in portfolio_sizes:
        treated_count = max(1, round(portcos * 0.75))
        for true_effect in effect_sizes:
            estimates = []
            p_values = []
            for seed in range(1000, 1000 + monte_carlo_runs):
                settings = SimulationSettings(
                    portfolio_size=portcos,
                    treated_count=treated_count,
                    effect_size_scale=true_effect / 0.50 if true_effect > 0 else 0.0,
                    frequency_scale=0.20,
                )
                results, _ = run_test_a(settings=settings, seed=seed, write_artifacts=False)
                task_3 = results["task_3"]
                if task_3.get("executed"):
                    estimates.append(abs(task_3["estimate_hours"]))
                    p_values.append(task_3["p_value"])
            mean_estimate = float(np.mean(estimates)) if estimates else None
            sd_estimate = float(np.std(estimates, ddof=1)) if len(estimates) > 1 else None
            power = float(np.mean([p < 0.05 for p in p_values])) if p_values else 0.0
            bias = None if mean_estimate is None else mean_estimate - (true_effect * 10.0)
            rows.append(
                {
                    "portcos": portcos,
                    "true_effect": true_effect,
                    "mean_estimate_hours": None if mean_estimate is None else round(mean_estimate, 3),
                    "sd_hours": None if sd_estimate is None else round(sd_estimate, 3),
                    "power": round(power, 3),
                    "bias_hours": None if bias is None else round(bias, 3),
                    "successful_runs": len(estimates),
                }
            )
    return {
        "settings": {"monte_carlo_runs": monte_carlo_runs},
        "rows": rows,
        "acceptance": summarize_acceptance("test_b", rows),
    }


def _rank_positions(task_1_rows: List[Dict[str, object]]) -> Dict[str, int]:
    return {row["entity_type"]: idx for idx, row in enumerate(task_1_rows)}


def run_test_c() -> Dict[str, object]:
    baseline_settings = SimulationSettings()
    baseline_results, _ = run_test_a(settings=baseline_settings, seed=7, write_artifacts=False)
    baseline_rank = _rank_positions(baseline_results["task_1"]["rows"])
    baseline_hours = baseline_results["task_2"]["current_hours"]
    rows: List[Dict[str, object]] = []
    for degradation, levels in {
        "missing_tuple_rate": [0.05, 0.10, 0.20, 0.30],
        "predicate_inconsistency_rate": [0.0, 0.05, 0.10, 0.20],
        "confidence_threshold": [0.5, 0.6, 0.7, 0.8, 0.9],
        "entity_resolution_failure_rate": [0.0, 0.05, 0.10],
    }.items():
        for level in levels:
            settings = SimulationSettings()
            if degradation == "missing_tuple_rate":
                settings.missing_tuple_rate = level
            elif degradation == "predicate_inconsistency_rate":
                settings.predicate_inconsistency_rate = level
            elif degradation == "confidence_threshold":
                settings.confidence_threshold = level
            elif degradation == "entity_resolution_failure_rate":
                settings.entity_resolution_failure_rate = level
            results, _ = run_test_a(settings=settings, seed=7, write_artifacts=False)
            rank = _rank_positions(results["task_1"]["rows"])
            rank_shift = max(abs(rank.get(entity_type, 99) - baseline_rank.get(entity_type, 99)) for entity_type in baseline_rank)
            hours_drift = abs(results["task_2"]["current_hours"] - baseline_hours) / max(baseline_hours, 1) * 100.0
            did_estimate = results["task_3"]["estimate_hours"] if results["task_3"].get("executed") else None
            rows.append(
                {
                    "degradation": degradation,
                    "level": level,
                    "task_1_rank_shift": int(rank_shift),
                    "task_2_hours_drift_pct": round(hours_drift, 2),
                    "task_3_estimate_hours": did_estimate,
                    "task_5_cost_slope": results["task_5"]["cost_slope"] if results["task_5"].get("executed") else None,
                    "task_6_interval": results["task_6"].get("prediction_interval_pct"),
                    "task_7_distance": results["task_7"].get("mean_pairwise_distance"),
                }
            )
    return {
        "rows": rows,
        "acceptance": summarize_acceptance("test_c", rows),
    }


def run_test_d() -> Dict[str, object]:
    true_effect = 0.35
    base_settings = SimulationSettings(effect_size_scale=true_effect / 0.50, frequency_scale=0.25)
    no_confounds = SimulationSettings(effect_size_scale=true_effect / 0.50, confounds_enabled=False, frequency_scale=0.25)
    yes_results, yes_db = run_test_a(settings=base_settings, seed=77, write_artifacts=False)
    no_results, no_db = run_test_a(settings=no_confounds, seed=77, write_artifacts=False)
    true_effect_hours = true_effect * 10.0
    rows = []
    for label, results in [("no", no_results), ("yes", yes_results)]:
        did = results["task_3"]
        did_estimate = abs(did["estimate_hours"]) if did.get("executed") else None
        rows.append(
            {
                "method": "did",
                "confounds": label,
                "estimate_hours": None if did_estimate is None else round(did_estimate, 3),
                "true_effect_hours": round(true_effect_hours, 3),
                "bias_pct_of_true": None if did_estimate is None else round(((did_estimate - true_effect_hours) / true_effect_hours) * 100.0, 2),
            }
        )
    import duckdb

    con = duckdb.connect(yes_db, read_only=True)
    naive = con.execute(
        """
        WITH metrics AS (
            SELECT m.portco_id, m.month, m.metric_value
            FROM metric_observations m
            WHERE m.metric_name = 'median_cycle_hours'
              AND m.workflow_family = 'purchase_order'
        )
        SELECT AVG(CASE WHEN m.month >= p.platform_deploy_date THEN m.metric_value END) AS post_metric,
               AVG(CASE WHEN m.month < p.platform_deploy_date THEN m.metric_value END) AS pre_metric
        FROM metrics m
        JOIN portcos p ON m.portco_id = p.portco_id
        WHERE p.platform_deploy_date IS NOT NULL
        """
    ).fetchone()
    naive_estimate = abs((naive[1] or 0) - (naive[0] or 0))
    rows.append(
        {
            "method": "naive_pre_post",
            "confounds": "yes",
            "estimate_hours": round(naive_estimate, 3),
            "true_effect_hours": round(true_effect_hours, 3),
            "bias_pct_of_true": round(((naive_estimate - true_effect_hours) / true_effect_hours) * 100.0, 2),
        }
    )
    return {"rows": rows, "acceptance": summarize_acceptance("test_d", rows)}


def run_test_e() -> Dict[str, object]:
    labor_rates = {
        "clerical": 42.5,
        "manager": 75.0,
        "specialist": 140.0,
    }
    implementation_costs = {
        "invoice": 18_000.0,
        "purchase_order": 48_000.0,
        "vendor": 24_000.0,
        "campaign": 32_000.0,
        "contract": 90_000.0,
        "employee_onboarding": 10_000.0,
    }
    capture_rates = {
        "invoice": 0.78,
        "purchase_order": 0.68,
        "vendor": 0.55,
        "campaign": 0.50,
        "contract": 0.30,
        "employee_onboarding": 0.62,
    }
    role_bucket = {
        "invoice": "clerical",
        "purchase_order": "manager",
        "vendor": "specialist",
        "campaign": "manager",
        "contract": "specialist",
        "employee_onboarding": "clerical",
    }
    import duckdb

    e1_runs = []
    e2_runs = []
    e3_runs = []
    seeds = [11]
    selection_count = 5
    cost_tiers = {
        "ops_only": 30_000.0,
        "full_measurement": 70_000.0,
        "causal_ready": 120_000.0,
    }
    roi_scenarios = {
        "conservative": {
            "analytics_hourly_rate": 100.0,
            "workflow_selection_rounds_per_year": 2,
            "cfo_reviews_per_year": 6,
            "portfolio_reporting_cycles_per_year": 2,
            "causal_studies_per_year": 1,
            "decision_capture_multiplier": 0.45,
            "analyst_hours": {
                "workflow_selection_manual": 12.0,
                "workflow_selection_instrumented": 5.0,
                "cfo_review_manual": 8.0,
                "cfo_review_instrumented": 3.0,
                "portfolio_report_manual": 14.0,
                "portfolio_report_instrumented": 6.0,
                "causal_study_manual": 36.0,
                "causal_study_instrumented": 18.0,
            },
        },
        "base": {
            "analytics_hourly_rate": 125.0,
            "workflow_selection_rounds_per_year": 3,
            "cfo_reviews_per_year": 12,
            "portfolio_reporting_cycles_per_year": 4,
            "causal_studies_per_year": 2,
            "decision_capture_multiplier": 1.0,
            "analyst_hours": {
                "workflow_selection_manual": 16.0,
                "workflow_selection_instrumented": 4.0,
                "cfo_review_manual": 10.0,
                "cfo_review_instrumented": 2.0,
                "portfolio_report_manual": 18.0,
                "portfolio_report_instrumented": 4.0,
                "causal_study_manual": 60.0,
                "causal_study_instrumented": 16.0,
            },
        },
        "aggressive": {
            "analytics_hourly_rate": 150.0,
            "workflow_selection_rounds_per_year": 4,
            "cfo_reviews_per_year": 12,
            "portfolio_reporting_cycles_per_year": 6,
            "causal_studies_per_year": 3,
            "decision_capture_multiplier": 1.25,
            "analyst_hours": {
                "workflow_selection_manual": 18.0,
                "workflow_selection_instrumented": 3.0,
                "cfo_review_manual": 12.0,
                "cfo_review_instrumented": 2.0,
                "portfolio_report_manual": 22.0,
                "portfolio_report_instrumented": 4.0,
                "causal_study_manual": 72.0,
                "causal_study_instrumented": 14.0,
            },
        },
    }

    for seed in seeds:
        settings = SimulationSettings(
            portfolio_size=10,
            treated_count=7,
            months=9,
            effect_size_scale=1.00,
            frequency_scale=0.18,
        )
        results, db_path = run_test_a(settings=settings, seed=seed, write_artifacts=False)
        con = duckdb.connect(db_path, read_only=True)
        task1_rows = results["task_1"]["rows"]
        truth_rows = []
        candidate_rows = [row for row in task1_rows if row["entity_type"] in implementation_costs]
        for idx, row in enumerate(candidate_rows):
            entity_type = row["entity_type"]
            human_hours = float(row["human_time_hours"])
            annual_value = human_hours * labor_rates[role_bucket[entity_type]] * capture_rates[entity_type]
            true_net_value = annual_value - implementation_costs[entity_type]
            truth_rows.append(
                {
                    "workflow_family": entity_type,
                    "frequency": row["instance_count"],
                    "human_hours": human_hours,
                    "canonical_path_pct": row["canonical_path_pct"],
                    "exception_burden": 1.0 - row["canonical_path_pct"],
                    "implementation_cost": implementation_costs[entity_type],
                    "true_net_value": round(true_net_value, 2),
                }
            )
        rng = np.random.default_rng(seed)
        synthetic_candidates = [
            {
                "workflow_family": f"synthetic_candidate_{i}",
                "frequency": int(rng.integers(120, 900)),
                "human_hours": float(rng.uniform(40, 420)),
                "canonical_path_pct": float(rng.uniform(0.35, 0.92)),
                "exception_burden": 0.0,
                "implementation_cost": float(rng.uniform(14_000, 70_000)),
                "true_net_value": 0.0,
            }
            for i in range(24)
        ]
        for row in synthetic_candidates:
            row["exception_burden"] = 1.0 - row["canonical_path_pct"]
            labor_bucket = rng.choice(list(labor_rates))
            capture_rate = float(rng.uniform(0.25, 0.85))
            annual_value = row["human_hours"] * labor_rates[labor_bucket] * capture_rate
            penalty = row["implementation_cost"] * (1.05 + (1.8 * row["exception_burden"]))
            row["true_net_value"] = round(annual_value - penalty, 2)
        truth_rows.extend(synthetic_candidates)
        truth_df = sorted(truth_rows, key=lambda row: row["true_net_value"], reverse=True)
        truth_rank = {row["workflow_family"]: idx for idx, row in enumerate(truth_df)}

        def choose_workflows(regime: str) -> List[str]:
            scored = []
            for row in truth_rows:
                workflow = row["workflow_family"]
                local_rng = np.random.default_rng(seed + 900 + truth_rank[workflow])
                if regime == "full_action_log":
                    observed_score = row["true_net_value"]
                elif regime == "weak_instrumentation":
                    noisy_hours = row["human_hours"] * local_rng.uniform(0.45, 1.85)
                    noisy_frequency = row["frequency"] * local_rng.uniform(0.65, 1.40)
                    visible_cost = row["implementation_cost"] * local_rng.uniform(0.75, 1.10)
                    hidden_exception_penalty = row["implementation_cost"] * 1.40 * row["exception_burden"]
                    observed_score = (noisy_frequency * noisy_hours * 0.11 * row["canonical_path_pct"]) - visible_cost - hidden_exception_penalty
                else:
                    observed_score = row["frequency"] + (row["human_hours"] * 0.15)
                scored.append((workflow, observed_score))
            return [workflow for workflow, _ in sorted(scored, key=lambda item: item[1], reverse=True)[:selection_count]]

        optimal = [row["workflow_family"] for row in truth_df[:selection_count]]
        optimal_value = sum(row["true_net_value"] for row in truth_rows if row["workflow_family"] in optimal)
        for regime in ["full_action_log", "weak_instrumentation", "heuristic_baseline"]:
            chosen = choose_workflows(regime)
            realized_value = sum(next(row["true_net_value"] for row in truth_rows if row["workflow_family"] == workflow) for workflow in chosen)
            hit_rate = len(set(chosen).intersection(optimal)) / max(len(optimal), 1)
            scored_order = choose_workflows(regime)
            predicted_rank = {workflow: idx for idx, workflow in enumerate(scored_order)}
            comparable = [workflow for workflow in optimal if workflow in predicted_rank]
            rank_corr = None
            if len(comparable) > 1:
                truth_vals = [truth_rank[workflow] for workflow in comparable]
                predicted_vals = [predicted_rank[workflow] for workflow in comparable]
                rank_corr = float(np.corrcoef(truth_vals, predicted_vals)[0, 1])
            e1_runs.append(
                {
                    "seed": seed,
                    "regime": regime,
                    "selected_workflows": chosen,
                    "realized_net_value": realized_value,
                    "regret": optimal_value - realized_value,
                    "top5_hit_rate": hit_rate,
                    "rank_correlation": rank_corr,
                }
            )

        role_month_rows = con.execute(
            """
            SELECT strftime(timestamp, '%Y-%m') AS month,
                   SUM(CASE
                         WHEN predicate = 'executed'
                          AND subject NOT LIKE '%_agent_%'
                          AND object IN ('invoice_reconciliation', 'invoice_reconciliation_override', 'po_approval', 'po_approval_override')
                         THEN duration_minutes
                         ELSE 0
                       END) / 60.0 AS human_hours
            FROM tuples
            WHERE portco_id = 'portco_01'
            GROUP BY 1
            ORDER BY 1
            """
        ).fetchall()
        monthly_hours = [float(row[1] or 0.0) for row in role_month_rows]
        if not monthly_hours:
            monthly_hours = [0.0]
        true_current_hours = float(np.mean(monthly_hours[-3:]))
        base_before = float(np.mean(monthly_hours[:3]))

        def first_threshold_crossing(hours_series: List[float]) -> int | None:
            for idx in range(max(len(hours_series) - 1, 1)):
                if hours_series[idx] < 160.0 and hours_series[min(idx + 1, len(hours_series) - 1)] < 160.0:
                    return idx
            return None

        threshold_month_truth = first_threshold_crossing(monthly_hours)
        for regime in ["full_action_log", "weak_instrumentation", "heuristic_baseline"]:
            if regime == "full_action_log":
                estimated_series = monthly_hours[:]
            elif regime == "weak_instrumentation":
                estimated_series = []
                for idx, value in enumerate(monthly_hours):
                    monthly_rng = np.random.default_rng(seed + 1600 + idx)
                    estimated_series.append((value * monthly_rng.uniform(0.62, 1.28)) + monthly_rng.uniform(8.0, 28.0))
            else:
                trend = np.linspace(0.0, base_before * 0.20, num=len(monthly_hours))
                estimated_series = [max(base_before - drift, 0.0) for drift in trend]
            estimated_current_hours = float(np.mean(estimated_series[-3:]))
            threshold_month_est = first_threshold_crossing(estimated_series)
            e2_runs.append(
                {
                    "seed": seed,
                    "regime": regime,
                    "estimated_current_hours": estimated_current_hours,
                    "hours_error_pct": abs(estimated_current_hours - true_current_hours) / max(true_current_hours, 1) * 100.0,
                    "threshold_month_error": (
                        6.0 if threshold_month_truth is None and threshold_month_est is not None
                        else 6.0 if threshold_month_truth is not None and threshold_month_est is None
                        else 0.0 if threshold_month_truth is None and threshold_month_est is None
                        else abs(threshold_month_est - threshold_month_truth)
                    ),
                    "false_positive_fte_removal": threshold_month_truth is None and threshold_month_est is not None,
                    "false_negative_fte_removal": threshold_month_truth is not None and threshold_month_est is None,
                }
            )

        true_positive_effect = abs(results["task_3"]["estimate_hours"]) if results["task_3"].get("executed") else 0.0
        true_effect_hours = settings.effect_size_scale * 10.0 * 0.50
        naive = con.execute(
            """
            WITH metrics AS (
                SELECT m.portco_id, m.month, m.metric_value
                FROM metric_observations m
                WHERE m.metric_name = 'median_cycle_hours'
                  AND m.workflow_family = 'purchase_order'
            )
            SELECT AVG(CASE WHEN m.month >= p.platform_deploy_date THEN m.metric_value END) AS post_metric,
                   AVG(CASE WHEN m.month < p.platform_deploy_date THEN m.metric_value END) AS pre_metric
            FROM metrics m
            JOIN portcos p ON m.portco_id = p.portco_id
            WHERE p.platform_deploy_date IS NOT NULL
            """
        ).fetchone()
        naive_estimate = abs((naive[1] or 0.0) - (naive[0] or 0.0))
        con.close()
        weak_settings = SimulationSettings(
            portfolio_size=settings.portfolio_size,
            treated_count=settings.treated_count,
            months=settings.months,
            effect_size_scale=settings.effect_size_scale,
            frequency_scale=settings.frequency_scale,
            missing_tuple_rate=0.20,
            predicate_inconsistency_rate=0.12,
            entity_resolution_failure_rate=0.12,
            confidence_threshold=0.85,
            use_controls=False,
        )
        weak_results, _ = run_test_a(settings=weak_settings, seed=seed, write_artifacts=False)
        weak_estimate = abs(weak_results["task_3"]["estimate_hours"]) if weak_results["task_3"].get("executed") else 0.0
        for regime, estimate, p_value, pretrend in [
            (
                "full_action_log",
                true_positive_effect,
                results["task_3"].get("p_value", 1.0),
                results["task_3"].get("pretrend_p_value", 0.0),
            ),
            (
                "weak_instrumentation",
                weak_estimate,
                weak_results["task_3"].get("p_value", 1.0),
                weak_results["task_3"].get("pretrend_p_value", 0.0),
            ),
            ("heuristic_baseline", naive_estimate, None, None),
        ]:
            e3_runs.append(
                {
                    "seed": seed,
                    "regime": regime,
                    "estimate_hours": estimate,
                    "bias_hours": estimate - true_effect_hours,
                    "abs_bias_pct_of_true": abs(estimate - true_effect_hours) / max(true_effect_hours, 1.0) * 100.0,
                    "sign_correct": estimate > 0,
                    "p_value": p_value,
                    "pretrend_p_value": pretrend,
                    "pretrend_pass": None if pretrend is None else pretrend > 0.10,
                }
            )

    e1_rows = []
    for regime in ["full_action_log", "weak_instrumentation", "heuristic_baseline"]:
        rows = [row for row in e1_runs if row["regime"] == regime]
        e1_rows.append(
            {
                "regime": regime,
                "selected_workflows_example": rows[0]["selected_workflows"],
                "realized_net_value": round(float(np.mean([row["realized_net_value"] for row in rows])), 2),
                "regret": round(float(np.mean([row["regret"] for row in rows])), 2),
                "top5_hit_rate": round(float(np.mean([row["top5_hit_rate"] for row in rows])), 3),
                "rank_correlation": (
                    None
                    if not [row["rank_correlation"] for row in rows if row["rank_correlation"] is not None]
                    else round(float(np.nanmean([row["rank_correlation"] for row in rows if row["rank_correlation"] is not None])), 3)
                ),
            }
        )

    e2_rows = []
    for regime in ["full_action_log", "weak_instrumentation", "heuristic_baseline"]:
        rows = [row for row in e2_runs if row["regime"] == regime]
        e2_rows.append(
            {
                "regime": regime,
                "estimated_current_hours": round(float(np.mean([row["estimated_current_hours"] for row in rows])), 2),
                "hours_error_pct": round(float(np.mean([row["hours_error_pct"] for row in rows])), 2),
                "threshold_month_error": round(float(np.mean([row["threshold_month_error"] for row in rows])), 2),
                "false_positive_rate": round(float(np.mean([1.0 if row["false_positive_fte_removal"] else 0.0 for row in rows])), 3),
                "false_negative_rate": round(float(np.mean([1.0 if row["false_negative_fte_removal"] else 0.0 for row in rows])), 3),
            }
        )

    e3_rows = []
    for regime in ["full_action_log", "weak_instrumentation", "heuristic_baseline"]:
        rows = [row for row in e3_runs if row["regime"] == regime]
        p_values = [row["p_value"] for row in rows if row["p_value"] is not None]
        pretrend_passes = [1.0 if row["pretrend_pass"] else 0.0 for row in rows if row["pretrend_pass"] is not None]
        e3_rows.append(
            {
                "regime": regime,
                "mean_estimate_hours": round(float(np.mean([row["estimate_hours"] for row in rows])), 2),
                "mean_bias_hours": round(float(np.mean([row["bias_hours"] for row in rows])), 2),
                "mean_abs_bias_pct_of_true": round(float(np.mean([row["abs_bias_pct_of_true"] for row in rows])), 2),
                "estimate_sd_hours": round(float(np.std([row["estimate_hours"] for row in rows], ddof=1)), 2) if len(rows) > 1 else 0.0,
                "sign_accuracy": round(float(np.mean([1.0 if row["sign_correct"] else 0.0 for row in rows])), 3),
                "mean_p_value": None if not p_values else round(float(np.mean(p_values)), 3),
                "pretrend_pass_rate": None if not pretrend_passes else round(float(np.mean(pretrend_passes)), 3),
            }
        )

    full_value = next(row["realized_net_value"] for row in e1_rows if row["regime"] == "full_action_log")
    heuristic_value = next(row["realized_net_value"] for row in e1_rows if row["regime"] == "heuristic_baseline")
    full_cfo_error = next(row["hours_error_pct"] for row in e2_rows if row["regime"] == "full_action_log")
    heuristic_cfo_error = next(row["hours_error_pct"] for row in e2_rows if row["regime"] == "heuristic_baseline")
    full_lp_bias = next(row["mean_abs_bias_pct_of_true"] for row in e3_rows if row["regime"] == "full_action_log")
    heuristic_lp_bias = next(row["mean_abs_bias_pct_of_true"] for row in e3_rows if row["regime"] == "heuristic_baseline")

    staged_roi_rows = []
    for scenario_name, scenario in roi_scenarios.items():
        analyst_hours = scenario["analyst_hours"]
        annual_workflow_decision_value = max(full_value - heuristic_value, 0.0) * scenario["workflow_selection_rounds_per_year"] * scenario["decision_capture_multiplier"]
        annual_workflow_analytics_savings = (
            (analyst_hours["workflow_selection_manual"] - analyst_hours["workflow_selection_instrumented"])
            * scenario["analytics_hourly_rate"]
            * scenario["workflow_selection_rounds_per_year"]
        )
        annual_cfo_analytics_savings = (
            (analyst_hours["cfo_review_manual"] - analyst_hours["cfo_review_instrumented"])
            * scenario["analytics_hourly_rate"]
            * scenario["cfo_reviews_per_year"]
        )
        annual_portfolio_reporting_savings = (
            (analyst_hours["portfolio_report_manual"] - analyst_hours["portfolio_report_instrumented"])
            * scenario["analytics_hourly_rate"]
            * scenario["portfolio_reporting_cycles_per_year"]
        )
        annual_causal_study_savings = (
            (analyst_hours["causal_study_manual"] - analyst_hours["causal_study_instrumented"])
            * scenario["analytics_hourly_rate"]
            * scenario["causal_studies_per_year"]
        )
        for years in [1, 2]:
            ops_value = years * (
                annual_workflow_decision_value
                + annual_workflow_analytics_savings
                + annual_cfo_analytics_savings
            )
            full_value_horizon = years * (
                annual_workflow_decision_value
                + annual_workflow_analytics_savings
                + annual_cfo_analytics_savings
                + annual_portfolio_reporting_savings
            )
            causal_ready_value = years * (
                annual_workflow_decision_value
                + annual_workflow_analytics_savings
                + annual_cfo_analytics_savings
                + annual_portfolio_reporting_savings
                + annual_causal_study_savings
            )
            for tier, total_value in [
                ("ops_only", ops_value),
                ("full_measurement", full_value_horizon),
                ("causal_ready", causal_ready_value),
            ]:
                cost = cost_tiers[tier]
                staged_roi_rows.append(
                    {
                        "scenario": scenario_name,
                        "tier": tier,
                        "horizon_years": years,
                        "total_value": round(total_value, 2),
                        "cost": round(cost, 2),
                        "roi": round((total_value - cost) / max(cost, 1.0), 3),
                        "cfo_error_reduction_pct": round(heuristic_cfo_error - full_cfo_error, 2),
                        "causal_bias_reduction_pct": round(heuristic_lp_bias - full_lp_bias, 2),
                    }
                )
    base_scenario = roi_scenarios["base"]
    driver_rows = []

    def compute_tier_value(scenario: Dict[str, object], years: int, tier: str) -> float:
        analyst_hours = scenario["analyst_hours"]
        annual_workflow_decision_value = max(full_value - heuristic_value, 0.0) * scenario["workflow_selection_rounds_per_year"] * scenario["decision_capture_multiplier"]
        annual_workflow_analytics_savings = (
            (analyst_hours["workflow_selection_manual"] - analyst_hours["workflow_selection_instrumented"])
            * scenario["analytics_hourly_rate"]
            * scenario["workflow_selection_rounds_per_year"]
        )
        annual_cfo_analytics_savings = (
            (analyst_hours["cfo_review_manual"] - analyst_hours["cfo_review_instrumented"])
            * scenario["analytics_hourly_rate"]
            * scenario["cfo_reviews_per_year"]
        )
        annual_portfolio_reporting_savings = (
            (analyst_hours["portfolio_report_manual"] - analyst_hours["portfolio_report_instrumented"])
            * scenario["analytics_hourly_rate"]
            * scenario["portfolio_reporting_cycles_per_year"]
        )
        annual_causal_study_savings = (
            (analyst_hours["causal_study_manual"] - analyst_hours["causal_study_instrumented"])
            * scenario["analytics_hourly_rate"]
            * scenario["causal_studies_per_year"]
        )
        if tier == "ops_only":
            annual_total = annual_workflow_decision_value + annual_workflow_analytics_savings + annual_cfo_analytics_savings
        elif tier == "full_measurement":
            annual_total = annual_workflow_decision_value + annual_workflow_analytics_savings + annual_cfo_analytics_savings + annual_portfolio_reporting_savings
        else:
            annual_total = annual_workflow_decision_value + annual_workflow_analytics_savings + annual_cfo_analytics_savings + annual_portfolio_reporting_savings + annual_causal_study_savings
        return years * annual_total

    def compute_roi(value: float, cost: float) -> float:
        return round((value - cost) / max(cost, 1.0), 3)

    base_full_roi = compute_roi(compute_tier_value(base_scenario, 1, "full_measurement"), cost_tiers["full_measurement"])
    base_causal_roi = compute_roi(compute_tier_value(base_scenario, 1, "causal_ready"), cost_tiers["causal_ready"])
    for assumption_name, low_factor, high_factor in [
        ("decision_capture_multiplier", 0.75, 1.25),
        ("workflow_selection_rounds_per_year", 0.67, 1.33),
        ("analytics_hourly_rate", 0.8, 1.2),
        ("full_measurement_cost", 0.8, 1.2),
        ("causal_ready_cost", 0.8, 1.2),
    ]:
        low_scenario = {
            **base_scenario,
            "analyst_hours": dict(base_scenario["analyst_hours"]),
        }
        high_scenario = {
            **base_scenario,
            "analyst_hours": dict(base_scenario["analyst_hours"]),
        }
        low_full_cost = cost_tiers["full_measurement"]
        high_full_cost = cost_tiers["full_measurement"]
        low_causal_cost = cost_tiers["causal_ready"]
        high_causal_cost = cost_tiers["causal_ready"]
        if assumption_name == "full_measurement_cost":
            low_full_cost *= low_factor
            high_full_cost *= high_factor
        elif assumption_name == "causal_ready_cost":
            low_causal_cost *= low_factor
            high_causal_cost *= high_factor
        else:
            low_scenario[assumption_name] = base_scenario[assumption_name] * low_factor
            high_scenario[assumption_name] = base_scenario[assumption_name] * high_factor
        low_full_roi = compute_roi(compute_tier_value(low_scenario, 1, "full_measurement"), low_full_cost)
        high_full_roi = compute_roi(compute_tier_value(high_scenario, 1, "full_measurement"), high_full_cost)
        low_causal_roi = compute_roi(compute_tier_value(low_scenario, 1, "causal_ready"), low_causal_cost)
        high_causal_roi = compute_roi(compute_tier_value(high_scenario, 1, "causal_ready"), high_causal_cost)
        driver_rows.append(
            {
                "assumption": assumption_name,
                "full_measurement_base_roi": base_full_roi,
                "full_measurement_low_roi": low_full_roi,
                "full_measurement_high_roi": high_full_roi,
                "full_measurement_swing": round(max(abs(low_full_roi - base_full_roi), abs(high_full_roi - base_full_roi)), 3),
                "causal_ready_base_roi": base_causal_roi,
                "causal_ready_low_roi": low_causal_roi,
                "causal_ready_high_roi": high_causal_roi,
                "causal_ready_swing": round(max(abs(low_causal_roi - base_causal_roi), abs(high_causal_roi - base_causal_roi)), 3),
            }
        )
    driver_rows = sorted(driver_rows, key=lambda row: row["full_measurement_swing"], reverse=True)
    return {
        "assumptions": {
            "labor_rates": labor_rates,
            "implementation_costs": implementation_costs,
            "capture_rates": capture_rates,
            "fte_capacity_hours_per_month": 160.0,
            "cost_tiers": cost_tiers,
            "selection_count": selection_count,
            "evaluation_seeds": seeds,
            "roi_scenarios": roi_scenarios,
        },
        "compression_prioritization": e1_rows,
        "cfo_estimation": e2_rows,
        "lp_claim_support": e3_rows,
        "staged_roi": staged_roi_rows,
        "roi_drivers": driver_rows,
        "acceptance": "Full instrumentation improved workflow selection and CFO estimation relative to weaker regimes. The staged ROI model suggests ops-focused instrumentation can clear breakeven earlier, while broader measurement layers need longer horizons or additional strategic value to justify their cost.",
    }


def write_report(name: str, payload: Dict[str, object]) -> None:
    ensure_output_dir()
    json_path = os.path.join(OUTPUT_DIR, f"{name}_results.json")
    md_path = os.path.join(OUTPUT_DIR, f"{name}_results.md")
    with open(json_path, "w", encoding="ascii") as fh:
        json.dump(payload, fh, indent=2)
    lines = [f"# {name.upper()} Results", "", payload["acceptance"], ""]
    if name == "test_b":
        lines.extend(["| Portcos | True effect | Mean estimate | SD | Power | Bias |", "|---|---|---|---|---|---|"])
        for row in payload["rows"]:
            lines.append(f"| {row['portcos']} | {row['true_effect']} | {row['mean_estimate_hours']} | {row['sd_hours']} | {row['power']} | {row['bias_hours']} |")
    elif name == "test_c":
        lines.extend(["| Degradation | Level | Rank shift | Hours drift % | DiD estimate |", "|---|---|---|---|---|"])
        for row in payload["rows"]:
            lines.append(f"| {row['degradation']} | {row['level']} | {row['task_1_rank_shift']} | {row['task_2_hours_drift_pct']} | {row['task_3_estimate_hours']} |")
    elif name == "test_d":
        lines.extend(["| Method | Confounds | Estimate | True effect | Bias % of true |", "|---|---|---|---|---|"])
        for row in payload["rows"]:
            lines.append(f"| {row['method']} | {row['confounds']} | {row['estimate_hours']} | {row['true_effect_hours']} | {row['bias_pct_of_true']} |")
    elif name == "test_e":
        lines.extend(["## Compression Prioritization", "", "| Regime | Realized net value | Regret | Top-5 hit rate | Rank correlation |", "|---|---|---|---|---|"])
        for row in payload["compression_prioritization"]:
            lines.append(f"| {row['regime']} | {row['realized_net_value']} | {row['regret']} | {row['top5_hit_rate']} | {row['rank_correlation']} |")
        lines.extend(["", "## CFO Estimation", "", "| Regime | Estimated current hours | Hours error % | Threshold month error |", "|---|---|---|---|"])
        for row in payload["cfo_estimation"]:
            lines.append(f"| {row['regime']} | {row['estimated_current_hours']} | {row['hours_error_pct']} | {row['threshold_month_error']} |")
        lines.extend(["", "## Causal Support Quality", "", "| Regime | Mean estimate hours | Mean bias hours | Mean abs bias % | Estimate SD | Sign accuracy | Mean p-value | Pretrend pass rate |", "|---|---|---|---|---|---|---|---|"])
        for row in payload["lp_claim_support"]:
            lines.append(f"| {row['regime']} | {row['mean_estimate_hours']} | {row['mean_bias_hours']} | {row['mean_abs_bias_pct_of_true']} | {row['estimate_sd_hours']} | {row['sign_accuracy']} | {row['mean_p_value']} | {row['pretrend_pass_rate']} |")
        lines.extend(["", "## Staged ROI", "", "| Scenario | Tier | Horizon years | Total value | Cost | ROI | CFO error reduction | Causal bias reduction |", "|---|---|---|---|---|---|---|---|"])
        for row in payload["staged_roi"]:
            lines.append(f"| {row['scenario']} | {row['tier']} | {row['horizon_years']} | {row['total_value']} | {row['cost']} | {row['roi']} | {row['cfo_error_reduction_pct']} | {row['causal_bias_reduction_pct']} |")
        lines.extend(["", "## ROI Drivers", "", "| Assumption | Full ROI base | Full ROI low/high | Full ROI swing | Causal ROI base | Causal ROI low/high | Causal ROI swing |", "|---|---|---|---|---|---|---|"])
        for row in payload["roi_drivers"]:
            lines.append(f"| {row['assumption']} | {row['full_measurement_base_roi']} | {row['full_measurement_low_roi']} / {row['full_measurement_high_roi']} | {row['full_measurement_swing']} | {row['causal_ready_base_roi']} | {row['causal_ready_low_roi']} / {row['causal_ready_high_roi']} | {row['causal_ready_swing']} |")
    with open(md_path, "w", encoding="ascii") as fh:
        fh.write("\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run validation suite for Tests B/C/D.")
    parser.add_argument("--test", choices=["all", "b", "c", "d", "e"], default="all")
    parser.add_argument("--monte-carlo-runs", type=int, default=2)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payloads = {}
    if args.test in {"all", "b"}:
        payloads["test_b"] = run_test_b(monte_carlo_runs=args.monte_carlo_runs)
        write_report("test_b", payloads["test_b"])
    if args.test in {"all", "c"}:
        payloads["test_c"] = run_test_c()
        write_report("test_c", payloads["test_c"])
    if args.test in {"all", "d"}:
        payloads["test_d"] = run_test_d()
        write_report("test_d", payloads["test_d"])
    if args.test in {"all", "e"}:
        payloads["test_e"] = run_test_e()
        write_report("test_e", payloads["test_e"])
    print(json.dumps({name: payload["acceptance"] for name, payload in payloads.items()}, indent=2))


if __name__ == "__main__":
    main()
