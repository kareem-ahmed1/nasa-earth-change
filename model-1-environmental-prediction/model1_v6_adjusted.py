"""
Project: African Environmental Change Analysis
Model 1 (v6 Final, corrected): Next-Month Environmental Condition Prediction
NASA International Space Apps Challenge

Corrections over the original v6 run:
- Temperature live z is NaN (N/A) instead of a fake 0.0 (LogReg produces no z-score).
- Live forecast and model bundle are produced BEFORE the test-lock check. They use only
  labeled data up to the latest observation, never the test evaluation.
- Frozen decisions are written once and compared on every later run.
- The test section runs only if the lock file is absent (or RESET_TEST_LOCK is set).
  A locked run never overwrites summary_v6.json or results_v6.csv.
- The test lock manifest is written before the test starts (to block re-runs after a crash)
  and updated with the results when it finishes.
- Limitations text uses computed values only. The test base rate is no longer confused with the AUC.
- Hard-coded claims removed.
"""

import os
import sys
import json
import hashlib
import datetime
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import joblib
from scipy.stats import norm

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    roc_auc_score, average_precision_score, brier_score_loss, mean_squared_error
)

try:
    from xgboost import XGBClassifier, XGBRegressor
    HAS_XGB = True
except ImportError:
    from sklearn.ensemble import GradientBoostingClassifier as XGBClassifier
    from sklearn.ensemble import GradientBoostingRegressor as XGBRegressor
    HAS_XGB = False

# ==============================================================================
# SECTION 0: CONFIGURATION
# ==============================================================================
RANDOM_STATE = 42
RESET_TEST_LOCK = False              # Only set True for a deliberate, documented re-evaluation

DEV_RUN_LABELS = [
    "v1_initial_exploration",
    "v2_target_alignment",
    "v3_risk_score_framework",
    "v4_zspace_and_units",
    "v5_detrending_rigor",
]
DEV_ITERATIONS = len(DEV_RUN_LABELS)

PRECIP_MIN_REL_SPREAD = 0.20
PRECIP_MAX_ZERO_SHARE = 0.30
EXCLUDE_DEGENERATE_PRECIP = True
USE_LOG_PRECIP = True

LIFT_HIGH = 2.0
LIFT_ELEVATED = 1.0

RIDGE_ALPHA_GRID = [0.01, 0.1, 1.0, 10.0, 100.0]
CLIP_LIMIT = 4.0
MAX_CLIP_FRACTION = 0.01             # Regressor excluded if >1% of validation predictions are clipped
MSESS_FLOOR = -1.0
SIGMA_FLOOR = 0.15
CALIBRATION_SHARE_MAX_AUC_GAP = None # placeholder kept for clarity; not used

FOLDS = [
    {"name": "Fold 1", "train_years": (2005, 2012), "val_years": (2013, 2015)},
    {"name": "Fold 2", "train_years": (2005, 2015), "val_years": (2016, 2018)},
    {"name": "Fold 3", "train_years": (2005, 2018), "val_years": (2019, 2021)},
]
TEST_YEARS = (2022, 2024)
FINAL_TRAIN_END = 2021
VERDICT_MIN_AUC_GAIN = 0.03
BOOTSTRAP_REPS = 2000

DATA_PATH = "africa_climate_featured.csv"
FALLBACK_PATH = "africa_climate_merged_2004_2024.csv"
MERGED_2004_2024_PATH = "africa_climate_merged_2004_2024.csv"

LOCK_FILE = "test_locked_v6.json"
FROZEN_CONFIG_FILE = "frozen_config_v6.json"
RESULTS_CSV_FILE = "results_v6.csv"
SUMMARY_JSON_FILE = "summary_v6.json"
BUNDLE_FILE = "model_bundle_v6.joblib"

results_records = []
summary_json = {
    "config": {
        "random_state": RANDOM_STATE,
        "dev_iterations": DEV_ITERATIONS,
        "dev_run_labels": DEV_RUN_LABELS,
        "reset_test_lock": RESET_TEST_LOCK,
        "precip_min_rel_spread": PRECIP_MIN_REL_SPREAD,
        "precip_max_zero_share": PRECIP_MAX_ZERO_SHARE,
        "exclude_degenerate_precip": EXCLUDE_DEGENERATE_PRECIP,
        "use_log_precip": USE_LOG_PRECIP,
        "lift_high": LIFT_HIGH,
        "lift_elevated": LIFT_ELEVATED,
        "ridge_alpha_grid": RIDGE_ALPHA_GRID,
    }
}

print("=" * 100)
print("     AFRICAN ENVIRONMENTAL CHANGE ANALYSIS: AI MODEL 1 (v6 FINAL, CORRECTED)     ")
print("=" * 100)

script_path = os.path.abspath(__file__) if "__file__" in globals() else os.path.abspath("model1_v6.py")
if os.path.exists(script_path):
    with open(script_path, "rb") as sf:
        script_sha256 = hashlib.sha256(sf.read()).hexdigest()
else:
    script_sha256 = "UNKNOWN"
print(f" -> Source Script SHA-256  : {script_sha256}")
print(f" -> Development Iterations : {DEV_ITERATIONS} ({DEV_RUN_LABELS})")

# ==============================================================================
# SECTION 1: DATA INTEGRITY
# ==============================================================================
print("\n" + "=" * 100)
print("SECTION 1: Data Integrity & Unit Checks")
print("=" * 100)

if os.path.exists(DATA_PATH):
    print(f" -> Loading: {DATA_PATH}")
    df_raw = pd.read_csv(DATA_PATH)
elif os.path.exists(FALLBACK_PATH):
    print(f" -> Loading fallback: {FALLBACK_PATH}")
    df_raw = pd.read_csv(FALLBACK_PATH)
else:
    raise FileNotFoundError("Climate dataset not found in the current folder.")

df_raw = df_raw.sort_values(by=["Region", "Year", "Month"]).reset_index(drop=True)

region_counts = df_raw["Region"].value_counts().to_dict()
print(" -> Rows per region (expected 240 each):")
for r, cnt in sorted(region_counts.items()):
    print(f"    * {r:<16}: {cnt} [{'OK' if cnt == 240 else 'UNEXPECTED'}]")

dup_count = int(df_raw.duplicated(subset=["Region", "Year", "Month"]).sum())
nan_temp = int(df_raw["Temperature_Anomaly"].isna().sum())
nan_precip = int(df_raw["Precipitation_mm"].isna().sum())
print(f" -> Duplicates: {dup_count} | Missing Temperature: {nan_temp} | Missing Precipitation: {nan_precip}")

print("\n[Precipitation_mm describe() | unit: UNCONFIRMED]")
print(df_raw.groupby("Region")["Precipitation_mm"].describe().round(3).to_string())

zero_counts = df_raw.groupby("Region")["Precipitation_mm"].apply(lambda s: int((s == 0.0).sum())).to_dict()
print("\n[Zero-precipitation months per region]")
for r, z in sorted(zero_counts.items()):
    print(f"    * {r:<16}: {z}")

sorted_regions = sorted(df_raw["Region"].unique().tolist())
summary_json["data_integrity"] = {
    "region_counts": region_counts, "duplicate_count": dup_count,
    "nan_temp": nan_temp, "nan_precip": nan_precip,
    "precip_unit_status": "UNCONFIRMED", "zero_counts": zero_counts, "regions": sorted_regions,
}

region_meta = pd.get_dummies(pd.DataFrame({"Region": sorted_regions}), columns=["Region"],
                             prefix="Region", drop_first=True, dtype=int)
region_meta["Region"] = sorted_regions
region_cols = [c for c in region_meta.columns if c.startswith("Region_")]

if os.path.exists(MERGED_2004_2024_PATH):
    df_merged = pd.read_csv(MERGED_2004_2024_PATH)
    df_04 = df_merged[df_merged["Year"] == 2004].copy()
    for col in df_raw.columns:
        if col not in df_04.columns:
            df_04[col] = np.nan
    df_full = (pd.concat([df_04, df_raw], ignore_index=True)
               .sort_values(by=["Region", "Year", "Month"]).reset_index(drop=True))
else:
    df_full = df_raw.copy()

df_full["target_month"] = (df_full["Month"] % 12) + 1
df_full["time_idx"] = (df_full["Year"] - 2005) * 12 + (df_full["Month"] - 1)
df_full["next_temp"] = df_full.groupby("Region")["Temperature_Anomaly"].shift(-1)
df_full["next_precip"] = df_full.groupby("Region")["Precipitation_mm"].shift(-1)

df = df_full[df_full["Year"] >= 2005].copy().reset_index(drop=True)

# ==============================================================================
# SECTION 2: SHARED FUNCTIONS
# ==============================================================================
def risk_from_z(z_pred, sigma, z_hi, z_lo=None):
    """Gaussian-tail risk from a predicted z-score and residual sigma."""
    z_p = np.clip(z_pred, -CLIP_LIMIT, CLIP_LIMIT)
    sig = np.maximum(sigma, SIGMA_FLOOR)
    risk_hi = 1.0 - norm.cdf((z_hi - z_p) / sig)
    if z_lo is not None:
        risk_lo = norm.cdf((z_lo - z_p) / sig)
        return np.clip(risk_hi + risk_lo, 0.0, 1.0)
    return np.clip(risk_hi, 0.0, 1.0)

def get_degenerate_precip_pairs(train_df, max_zero_share=PRECIP_MAX_ZERO_SHARE,
                                min_rel_spread=PRECIP_MIN_REL_SPREAD):
    """Region x target_month pairs that are degenerate on the given training rows."""
    degen_pairs, records = set(), []
    for r in sorted(train_df["Region"].unique()):
        sub_r = train_df[train_df["Region"] == r]
        for m in range(1, 13):
            vals = sub_r[sub_r["Month"] == m]["Precipitation_mm"].dropna().values
            if len(vals) == 0:
                continue
            z_share = float(np.mean(vals == 0.0))
            p10, p90 = float(np.percentile(vals, 10)), float(np.percentile(vals, 90))
            med = float(np.median(vals))
            rel_spr = (p90 - p10) / (med + 1e-9)
            is_deg = bool((z_share > max_zero_share) or (rel_spr < min_rel_spread))
            records.append({"Region": r, "target_month": m, "zero_share": z_share,
                            "p10": p10, "p90": p90, "median": med,
                            "rel_spread": rel_spr, "is_degenerate": is_deg})
            if is_deg:
                degen_pairs.add((r, m))
    return degen_pairs, pd.DataFrame(records)

def detrend_temperature_and_build_features(source_df, train_mask):
    """Per-region linear trend fitted on training rows; temperature features rebuilt on residuals."""
    out_df = source_df.copy()
    tr_slice = out_df[train_mask]
    slopes = {}
    out_df["temp_trend"] = 0.0
    out_df["next_temp_trend"] = 0.0
    for r in sorted(out_df["Region"].unique()):
        r_tr = tr_slice[tr_slice["Region"] == r]
        slope, intercept = np.polyfit(r_tr["time_idx"], r_tr["Temperature_Anomaly"], 1)
        slopes[r] = float(slope * 120.0)  # degrees C per decade
        r_idx = out_df["Region"] == r
        out_df.loc[r_idx, "temp_trend"] = slope * out_df.loc[r_idx, "time_idx"] + intercept
        out_df.loc[r_idx, "next_temp_trend"] = slope * (out_df.loc[r_idx, "time_idx"] + 1) + intercept
    out_df["r_t"] = out_df["Temperature_Anomaly"] - out_df["temp_trend"]
    out_df["r_next"] = out_df["next_temp"] - out_df["next_temp_trend"]
    for lag in [1, 3, 6, 12]:
        out_df[f"temp_lag_{lag}"] = out_df.groupby("Region")["r_t"].shift(lag)
    for w in [3, 6, 12]:
        out_df[f"temp_rolling_mean_{w}"] = out_df.groupby("Region")["r_t"].transform(
            lambda s: s.shift(1).rolling(w).mean())
    out_df["temp_rolling_std_3"] = out_df.groupby("Region")["r_t"].transform(
        lambda s: s.shift(1).rolling(3).std())
    out_df["temp_yoy_change"] = out_df["r_t"] - out_df["temp_lag_12"]
    return out_df, slopes

def smoothed_climatology(train_df, eval_df, y_col):
    """m-estimate smoothed Region x target_month rate; removes ties."""
    global_rate = float(train_df[y_col].mean())
    grouped = train_df.groupby(["Region", "target_month"])[y_col].agg(["sum", "count"]).reset_index()
    grouped["smoothed_rate"] = (grouped["sum"] + 5.0 * global_rate) / (grouped["count"] + 5.0)
    rate_map = {(r, m): rate for r, m, rate in
                zip(grouped["Region"], grouped["target_month"], grouped["smoothed_rate"])}
    return eval_df.apply(lambda row: rate_map.get((row["Region"], row["target_month"]), global_rate),
                         axis=1).values

def raw_tier(lift):
    if lift >= LIFT_HIGH:
        return "High"
    if lift >= LIFT_ELEVATED:
        return "Elevated"
    return "Low"

def tier_label(lift, validated):
    """Displayed tier. Returns NOT VALIDATED when the tier scheme failed its validation."""
    return raw_tier(lift) if validated else "NOT VALIDATED"

def compute_verdict(diff_auc, ci_lower, cv_beat, years_beaten, best_baseline_name, best_baseline_auc):
    cond_a = bool(diff_auc >= VERDICT_MIN_AUC_GAIN)
    cond_b = bool(ci_lower > 0.0)
    cond_c = bool(cv_beat)
    cond_d = bool(years_beaten >= 2)
    all_pass = bool(cond_a and cond_b and cond_c and cond_d)
    if all_pass:
        v_str = (f"SKILL CONFIRMED (+{diff_auc:.3f} ROC-AUC over {best_baseline_name} "
                 f"[{best_baseline_auc:.3f}])")
    else:
        failed = []
        if not cond_a: failed.append(f"Cond A (diff >= {VERDICT_MIN_AUC_GAIN}: {diff_auc:+.3f})")
        if not cond_b: failed.append(f"Cond B (CI 2.5% > 0: {ci_lower:+.3f})")
        if not cond_c: failed.append(f"Cond C (CV beat: {cv_beat})")
        if not cond_d: failed.append(f"Cond D (years beaten >= 2: {years_beaten}/3)")
        v_str = "NO RELIABLE SKILL (" + ", ".join(failed) + ")"
    return {"verdict": v_str, "all_pass": all_pass, "cond_a": cond_a,
            "cond_b": cond_b, "cond_c": cond_c, "cond_d": cond_d}

def construct_fold_dataset(full_source_df, train_end_year, trend_mode="detrended", precip_pool_mode="none"):
    """Builds z-space targets, thresholds and persistence signals using only training rows."""
    train_mask = ((full_source_df["Year"] >= 2005) & (full_source_df["Year"] <= train_end_year)
                  & ~((full_source_df["Year"] == train_end_year) & (full_source_df["Month"] == 12)))

    if trend_mode == "detrended":
        f_df, slopes = detrend_temperature_and_build_features(full_source_df, train_mask)
        eval_t_col, eval_next_t_col = "r_t", "r_next"
    else:
        f_df = full_source_df.copy()
        eval_t_col, eval_next_t_col = "Temperature_Anomaly", "next_temp"
        slopes = {r: 0.0 for r in f_df["Region"].unique()}

    f_df = f_df[f_df["Year"] >= 2005].copy().reset_index(drop=True)
    f_df = pd.merge(f_df, region_meta, on="Region", how="left")

    df_tr = f_df[(f_df["Year"] <= train_end_year)
                 & ~((f_df["Year"] == train_end_year) & (f_df["Month"] == 12))].copy()

    # Temperature thresholds in z-space
    t_stats = df_tr.groupby(["Region", "Month"])[eval_t_col].agg(["mean", "std"]).reset_index()
    t_stats.rename(columns={"Month": "target_month", "mean": "t_mu", "std": "t_sig"}, inplace=True)
    t_stats["t_sig"] = t_stats["t_sig"].replace(0, 1e-6).fillna(1.0)

    t_p90_recs = []
    for r in f_df["Region"].unique():
        sub_r = df_tr[df_tr["Region"] == r]
        for m in range(1, 13):
            prev_m = 12 if m == 1 else m - 1
            next_m = 1 if m == 12 else m + 1
            pooled = sub_r[sub_r["Month"].isin([prev_m, m, next_m])][eval_t_col].dropna().values
            p90 = float(np.percentile(pooled, 90)) if len(pooled) > 0 else 0.0
            t_p90_recs.append({"Region": r, "target_month": m, "t_p90_raw": p90})
    t_p90_df = pd.DataFrame(t_p90_recs)

    f_df = pd.merge(f_df, t_stats, on=["Region", "target_month"], how="left")
    f_df = pd.merge(f_df, t_p90_df, on=["Region", "target_month"], how="left")
    f_df["temp_z_next"] = (f_df[eval_next_t_col] - f_df["t_mu"]) / f_df["t_sig"]
    f_df["temp_z_hi"] = (f_df["t_p90_raw"] - f_df["t_mu"]) / f_df["t_sig"]
    f_df["target_temp_high"] = (f_df["temp_z_next"] > f_df["temp_z_hi"]).astype(int)

    t_curr_stats = t_stats.rename(columns={"target_month": "Month", "t_mu": "t_mu_curr", "t_sig": "t_sig_curr"})
    t_curr_p90 = t_p90_df.rename(columns={"target_month": "Month", "t_p90_raw": "t_p90_curr"})
    f_df = pd.merge(f_df, t_curr_stats, on=["Region", "Month"], how="left")
    f_df = pd.merge(f_df, t_curr_p90, on=["Region", "Month"], how="left")
    f_df["persist_temp_signal"] = (
        ((f_df[eval_t_col] - f_df["t_mu_curr"]) / f_df["t_sig_curr"])
        > ((f_df["t_p90_curr"] - f_df["t_mu_curr"]) / f_df["t_sig_curr"])
    ).astype(int)

    # Precipitation thresholds in z-space
    if USE_LOG_PRECIP:
        f_df["p_val"] = np.log1p(f_df["Precipitation_mm"])
        f_df["p_next"] = np.log1p(f_df["next_precip"])
    else:
        f_df["p_val"] = f_df["Precipitation_mm"]
        f_df["p_next"] = f_df["next_precip"]

    df_tr_p = f_df[(f_df["Year"] <= train_end_year)
                   & ~((f_df["Year"] == train_end_year) & (f_df["Month"] == 12))].copy()
    p_stats = df_tr_p.groupby(["Region", "Month"])["p_val"].agg(["mean", "std"]).reset_index()
    p_stats.rename(columns={"Month": "target_month", "mean": "p_mu", "std": "p_sig"}, inplace=True)
    p_stats["p_sig"] = p_stats["p_sig"].replace(0, 1e-6).fillna(1.0)

    p_recs = []
    for r in f_df["Region"].unique():
        sub_r = df_tr_p[df_tr_p["Region"] == r].copy()
        sub_r = pd.merge(sub_r, p_stats[p_stats["Region"] == r], left_on="Month",
                         right_on="target_month", how="left")
        sub_r["z_tr_p"] = (sub_r["p_val"] - sub_r["p_mu"]) / sub_r["p_sig"]
        for m in range(1, 13):
            if precip_pool_mode == "anomaly":
                prev_m = 12 if m == 1 else m - 1
                next_m = 1 if m == 12 else m + 1
                sample_z = sub_r[sub_r["Month"].isin([prev_m, m, next_m])]["z_tr_p"].dropna().values
            else:
                sample_z = sub_r[sub_r["Month"] == m]["z_tr_p"].dropna().values
            z_lo = float(np.percentile(sample_z, 10)) if len(sample_z) > 0 else -1.28
            z_hi = float(np.percentile(sample_z, 90)) if len(sample_z) > 0 else +1.28
            p_recs.append({"Region": r, "target_month": m, "precip_z_lo": z_lo, "precip_z_hi": z_hi})
    p_thresh_df = pd.DataFrame(p_recs)

    f_df = pd.merge(f_df, p_stats, on=["Region", "target_month"], how="left")
    f_df = pd.merge(f_df, p_thresh_df, on=["Region", "target_month"], how="left")
    f_df["precip_z_next"] = (f_df["p_next"] - f_df["p_mu"]) / f_df["p_sig"]
    f_df["target_precip_unusual"] = ((f_df["precip_z_next"] > f_df["precip_z_hi"])
                                     | (f_df["precip_z_next"] < f_df["precip_z_lo"])).astype(int)

    p_curr_stats = p_stats.rename(columns={"target_month": "Month", "p_mu": "p_mu_c", "p_sig": "p_sig_c"})
    p_curr_thresh = p_thresh_df.rename(columns={"target_month": "Month",
                                                "precip_z_lo": "p_z_lo_c", "precip_z_hi": "p_z_hi_c"})
    f_df = pd.merge(f_df, p_curr_stats, on=["Region", "Month"], how="left")
    f_df = pd.merge(f_df, p_curr_thresh, on=["Region", "Month"], how="left")
    z_curr_p = (f_df["p_val"] - f_df["p_mu_c"]) / f_df["p_sig_c"]
    f_df["persist_precip_signal"] = ((z_curr_p > f_df["p_z_hi_c"])
                                     | (z_curr_p < f_df["p_z_lo_c"])).astype(int)

    f_df["temp_seasonal_zscore"] = ((f_df[eval_t_col] - f_df["t_mu_curr"]) / f_df["t_sig_curr"]).round(3)
    f_df["precip_seasonal_zscore"] = ((f_df["p_val"] - f_df["p_mu_c"]) / f_df["p_sig_c"]).round(3)

    # Label-equals-z-rule assertions on labeled rows
    labeled = ~f_df["next_temp"].isna()
    assert (f_df.loc[labeled, "target_temp_high"]
            == (f_df.loc[labeled, "temp_z_next"] > f_df.loc[labeled, "temp_z_hi"]).astype(int)).all(), \
        "Temperature label does not equal the z-rule"
    assert (f_df.loc[labeled, "target_precip_unusual"]
            == ((f_df.loc[labeled, "precip_z_next"] > f_df.loc[labeled, "precip_z_hi"])
                | (f_df.loc[labeled, "precip_z_next"] < f_df.loc[labeled, "precip_z_lo"])).astype(int)).all(), \
        "Precipitation label does not equal the z-rule"

    # p_mu and p_sig are KEPT: the live step needs them to convert log-space output back to mm.
    drop_helpers = ["t_mu", "t_sig", "t_p90_raw", "t_mu_curr", "t_sig_curr", "t_p90_curr",
                    "p_val", "p_next", "p_mu_c", "p_sig_c", "p_z_lo_c", "p_z_hi_c"]
    f_df.drop(columns=[c for c in drop_helpers if c in f_df.columns], inplace=True)
    return f_df, slopes

EXCLUDE_COLS = ["Date", "Region", "Year", "Month", "target_month", "time_idx",
                "next_temp", "next_precip", "r_next", "temp_trend", "next_temp_trend"]
TEMP_FEATURE_COLS = sorted(list(set(
    [c for c in df_raw.columns if c not in EXCLUDE_COLS and c != "Temperature_Anomaly"]
    + ["r_t", "temp_seasonal_zscore", "precip_seasonal_zscore"] + region_cols)))
PRECIP_FEATURE_COLS = sorted(list(set(
    [c for c in df_raw.columns if c not in EXCLUDE_COLS and c != "r_t"]
    + ["temp_seasonal_zscore", "precip_seasonal_zscore"] + region_cols)))

# ==============================================================================
# SECTION 3: DEGENERATE PRECIPITATION MONTHS
# ==============================================================================
print("\n" + "=" * 100)
print("SECTION 3: Degenerate Precipitation Months")
print("=" * 100)

for f in FOLDS:
    tr_sub = df[(df["Year"] >= f["train_years"][0]) & (df["Year"] <= f["train_years"][1])
                & ~((df["Year"] == f["train_years"][1]) & (df["Month"] == 12))]
    deg_pairs, _ = get_degenerate_precip_pairs(tr_sub)
    print(f" -> {f['name']} ({f['train_years'][0]}-{f['train_years'][1]}): {len(deg_pairs)} pairs: "
          f"[{', '.join(f'{r}-M{m}' for r, m in sorted(deg_pairs))}]")

tr_final_sub = df[(df["Year"] <= FINAL_TRAIN_END)
                  & ~((df["Year"] == FINAL_TRAIN_END) & (df["Month"] == 12))]
deg_pairs_final, _ = get_degenerate_precip_pairs(tr_final_sub)
print(f" -> Final train ({2005}-{FINAL_TRAIN_END}): {len(deg_pairs_final)} pairs")

test_base_rows = df[(df["Year"] >= TEST_YEARS[0]) & (df["Year"] <= TEST_YEARS[1]) & ~df["next_temp"].isna()]
test_deg_mask = test_base_rows.apply(lambda r: (r["Region"], r["target_month"]) in deg_pairs_final, axis=1)
raw_test_rows_total = int(len(test_base_rows))
excluded_test_rows_count = int(test_deg_mask.sum())
kept_test_rows_count = raw_test_rows_total - excluded_test_rows_count
print(f" -> Test rows: raw {raw_test_rows_total} | excluded {excluded_test_rows_count} | kept {kept_test_rows_count}")

# ==============================================================================
# SECTION 4: PRECIPITATION POOLING (decision rule fixed in advance)
# ==============================================================================
print("\n" + "=" * 100)
print("SECTION 4: Precipitation Pooling Mode ('none' vs 'anomaly')")
print("=" * 100)

f3_none, _ = construct_fold_dataset(df_full, train_end_year=2018, precip_pool_mode="none")
f3_anom, _ = construct_fold_dataset(df_full, train_end_year=2018, precip_pool_mode="anomaly")
tr_mask_f3 = (f3_none["Year"] <= 2018) & ~((f3_none["Year"] == 2018) & (f3_none["Month"] == 12))
std_none = float(f3_none[tr_mask_f3].groupby("target_month")["target_precip_unusual"].mean().std())
std_anom = float(f3_anom[tr_mask_f3].groupby("target_month")["target_precip_unusual"].mean().std())
print(f" -> Monthly positive-rate std (training): none = {std_none:.4f} | anomaly = {std_anom:.4f}")

def run_precip_pool_cv(mode):
    aucs_rf, aucs_clim = [], []
    for f in FOLDS:
        f_df, _ = construct_fold_dataset(df_full, train_end_year=f["train_years"][1], precip_pool_mode=mode)
        tr_m = ((f_df["Year"] >= f["train_years"][0]) & (f_df["Year"] <= f["train_years"][1])
                & ~((f_df["Year"] == f["train_years"][1]) & (f_df["Month"] == 12)))
        va_m = (f_df["Year"] >= f["val_years"][0]) & (f_df["Year"] <= f["val_years"][1]) & ~f_df["next_temp"].isna()
        if EXCLUDE_DEGENERATE_PRECIP:
            deg_p, _ = get_degenerate_precip_pairs(f_df[tr_m])
            tr_m = tr_m & ~f_df.apply(lambda r: (r["Region"], r["target_month"]) in deg_p, axis=1)
            va_m = va_m & ~f_df.apply(lambda r: (r["Region"], r["target_month"]) in deg_p, axis=1)
        X_tr = f_df.loc[tr_m, PRECIP_FEATURE_COLS]
        z_tr = f_df.loc[tr_m, "precip_z_next"].values
        X_va = f_df.loc[va_m, PRECIP_FEATURE_COLS]
        y_va = f_df.loc[va_m, "target_precip_unusual"].values
        reg = RandomForestRegressor(n_estimators=100, max_depth=5, min_samples_leaf=5, random_state=RANDOM_STATE)
        reg.fit(X_tr, z_tr)
        sig = max(SIGMA_FLOOR, float(np.std(z_tr - np.clip(reg.predict(X_tr), -CLIP_LIMIT, CLIP_LIMIT))))
        risk = risk_from_z(reg.predict(X_va), sig, f_df.loc[va_m, "precip_z_hi"].values,
                           f_df.loc[va_m, "precip_z_lo"].values)
        aucs_rf.append(roc_auc_score(y_va, risk))
        aucs_clim.append(roc_auc_score(y_va, smoothed_climatology(f_df[tr_m], f_df.loc[va_m], "target_precip_unusual")))
    return np.mean(aucs_rf), np.std(aucs_rf), np.mean(aucs_clim)

auc_rf_none, std_rf_none, clim_none = run_precip_pool_cv("none")
auc_rf_anom, std_rf_anom, clim_anom = run_precip_pool_cv("anomaly")
pooled_std = float(np.sqrt((std_rf_none ** 2 + std_rf_anom ** 2) / 2.0))
gap_none = float(auc_rf_none - clim_none)
gap_anom = float(auc_rf_anom - clim_anom)

print(f"{'Mode':<10} | {'RF risk AUC':<22} | {'Climatology AUC':<16} | {'Gap':<8}")
print(f"{'none':<10} | {auc_rf_none:.3f} +/- {std_rf_none:.3f}       | {clim_none:.3f}           | {gap_none:+.3f}")
print(f"{'anomaly':<10} | {auc_rf_anom:.3f} +/- {std_rf_anom:.3f}       | {clim_anom:.3f}           | {gap_anom:+.3f}")

if (auc_rf_anom > auc_rf_none + pooled_std) and (abs(gap_anom) < abs(gap_none)):
    SELECTED_PRECIP_POOL_MODE = "anomaly"
else:
    SELECTED_PRECIP_POOL_MODE = "none"
pool_reason = (f"anomaly AUC {auc_rf_anom:.3f} vs none {auc_rf_none:.3f} + pooled std {pooled_std:.3f}; "
               f"|gap| anomaly {abs(gap_anom):.3f} vs none {abs(gap_none):.3f}")
print(f" >>> PRECIP_POOL_MODE = '{SELECTED_PRECIP_POOL_MODE}' | {pool_reason}")

summary_json["precipitation_pooling"] = {
    "std_monthly_rate_none": std_none, "std_monthly_rate_anomaly": std_anom,
    "auc_none": auc_rf_none, "auc_anomaly": auc_rf_anom,
    "selected_mode": SELECTED_PRECIP_POOL_MODE, "decision_reason": pool_reason,
}

# ==============================================================================
# SECTION 5: TEMPERATURE TREND AND DRIFT (training window 2005-2018 / 2005-2021)
# ==============================================================================
print("\n" + "=" * 100)
print("SECTION 5: Temperature Trend Slopes & Base-Rate Drift")
print("=" * 100)

f_detrend_cv, _ = construct_fold_dataset(df_full, train_end_year=2018, trend_mode="detrended")
f_fixed_cv, _ = construct_fold_dataset(df_full, train_end_year=2018, trend_mode="fixed")
f_detrend_te, slopes_final = construct_fold_dataset(df_full, train_end_year=2021, trend_mode="detrended")
f_fixed_te, _ = construct_fold_dataset(df_full, train_end_year=2021, trend_mode="fixed")

print(" -> Trend slopes on 2005-2021 (degrees C per decade):")
for r, sl in sorted(slopes_final.items()):
    print(f"    * {r:<16}: {sl:+.3f}")

tr_m18 = (f_fixed_cv["Year"] <= 2018) & ~((f_fixed_cv["Year"] == 2018) & (f_fixed_cv["Month"] == 12))
va_m18 = (f_fixed_cv["Year"] >= 2019) & (f_fixed_cv["Year"] <= 2021)
te_m21 = (f_fixed_te["Year"] >= 2022) & ~f_fixed_te["next_temp"].isna()

rates = {
    "fixed": {"train": float(f_fixed_cv.loc[tr_m18, "target_temp_high"].mean()),
              "val": float(f_fixed_cv.loc[va_m18, "target_temp_high"].mean()),
              "test": float(f_fixed_te.loc[te_m21, "target_temp_high"].mean())},
    "detrended": {"train": float(f_detrend_cv.loc[tr_m18, "target_temp_high"].mean()),
                  "val": float(f_detrend_cv.loc[va_m18, "target_temp_high"].mean()),
                  "test": float(f_detrend_te.loc[te_m21, "target_temp_high"].mean())},
}
for mode in ["fixed", "detrended"]:
    rates[mode]["drift"] = rates[mode]["test"] - rates[mode]["train"]
print(f" -> Drift (test - train): fixed {rates['fixed']['drift']*100:+.1f} pts | "
      f"detrended {rates['detrended']['drift']*100:+.1f} pts")

summary_json["temperature_drift"] = {"slopes_per_decade": slopes_final, **rates}

# ==============================================================================
# SECTION 6: RIDGE ALPHA TUNING (validation folds only)
# ==============================================================================
print("\n" + "=" * 100)
print(f"SECTION 6: Ridge Alpha Tuning on Validation Folds {RIDGE_ALPHA_GRID}")
print("=" * 100)

def tune_ridge_alpha(target_type):
    feat_cols = TEMP_FEATURE_COLS if target_type == "temperature" else PRECIP_FEATURE_COLS
    alpha_scores = {a: [] for a in RIDGE_ALPHA_GRID}
    for fold in FOLDS:
        f_df, _ = construct_fold_dataset(df_full, train_end_year=fold["train_years"][1],
                                         trend_mode="detrended" if target_type == "temperature" else "fixed",
                                         precip_pool_mode=SELECTED_PRECIP_POOL_MODE)
        tr_m = ((f_df["Year"] >= fold["train_years"][0]) & (f_df["Year"] <= fold["train_years"][1])
                & ~((f_df["Year"] == fold["train_years"][1]) & (f_df["Month"] == 12)))
        va_m = ((f_df["Year"] >= fold["val_years"][0]) & (f_df["Year"] <= fold["val_years"][1])
                & ~f_df["next_temp"].isna())
        if target_type == "precipitation" and EXCLUDE_DEGENERATE_PRECIP:
            deg_p, _ = get_degenerate_precip_pairs(f_df[tr_m])
            tr_m = tr_m & ~f_df.apply(lambda r: (r["Region"], r["target_month"]) in deg_p, axis=1)
            va_m = va_m & ~f_df.apply(lambda r: (r["Region"], r["target_month"]) in deg_p, axis=1)
        z_col = "temp_z_next" if target_type == "temperature" else "precip_z_next"
        y_col = "target_temp_high" if target_type == "temperature" else "target_precip_unusual"
        X_tr = f_df.loc[tr_m, feat_cols]
        z_tr = f_df.loc[tr_m, z_col].values
        X_va = f_df.loc[va_m, feat_cols]
        y_va = f_df.loc[va_m, y_col].values
        z_hi_va = f_df.loc[va_m, "temp_z_hi" if target_type == "temperature" else "precip_z_hi"].values
        z_lo_va = None if target_type == "temperature" else f_df.loc[va_m, "precip_z_lo"].values
        sc = StandardScaler()
        X_tr_s = sc.fit_transform(X_tr)
        X_va_s = sc.transform(X_va)
        for a in RIDGE_ALPHA_GRID:
            r_mod = Ridge(alpha=a, random_state=RANDOM_STATE)
            r_mod.fit(X_tr_s, z_tr)
            sig = max(SIGMA_FLOOR, float(np.std(z_tr - np.clip(r_mod.predict(X_tr_s), -CLIP_LIMIT, CLIP_LIMIT))))
            risk = risk_from_z(r_mod.predict(X_va_s), sig, z_hi_va, z_lo_va)
            alpha_scores[a].append(roc_auc_score(y_va, risk))
    means = {a: float(np.mean(alpha_scores[a])) for a in RIDGE_ALPHA_GRID}
    best_a = max(means, key=means.get)
    return best_a, means

best_alpha_t, alpha_means_t = tune_ridge_alpha("temperature")
best_alpha_p, alpha_means_p = tune_ridge_alpha("precipitation")
for label, best, means in [("Temperature", best_alpha_t, alpha_means_t),
                           ("Precipitation", best_alpha_p, alpha_means_p)]:
    print(f" -> {label}: " + " | ".join(f"a={a}: {means[a]:.3f}" for a in RIDGE_ALPHA_GRID) + f" -> best {best}")
    if best in (min(RIDGE_ALPHA_GRID), max(RIDGE_ALPHA_GRID)):
        print(f"    [WARNING] best alpha is at the grid edge.")

# ==============================================================================
# SECTION 7: APPROACH FIT / PREDICT (single code path for CV, live)
# ==============================================================================
def fit_selected_approach(name, X_tr, y_tr, z_tr, alpha_chosen=1.0):
    dropped_cols = [c for c in X_tr.columns if X_tr[c].std() < 1e-8]
    if dropped_cols:
        X_tr = X_tr.drop(columns=dropped_cols)
    scaler = None
    if "LogReg" in name or "Ridge" in name:
        scaler = StandardScaler()
        X_tr_proc = scaler.fit_transform(X_tr)
    else:
        X_tr_proc = X_tr

    sigma_resid = None
    if "Ridge" in name:
        model = Ridge(alpha=alpha_chosen, random_state=RANDOM_STATE)
    elif "RF (Regress Risk)" in name:
        model = RandomForestRegressor(n_estimators=100, max_depth=5, min_samples_leaf=5, random_state=RANDOM_STATE)
    elif "XGB (Regress Risk)" in name:
        model = XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.8,
                             reg_lambda=5.0, random_state=RANDOM_STATE)
    elif "LogReg (Classif)" in name:
        model = LogisticRegression(class_weight="balanced", C=0.5, max_iter=1000, random_state=RANDOM_STATE)
    elif "Random Forest (Classif)" in name:
        model = RandomForestClassifier(n_estimators=100, max_depth=5, min_samples_leaf=5,
                                       class_weight="balanced", random_state=RANDOM_STATE)
    elif "XGBoost (Classif)" in name:
        pos_w = max(1, (len(y_tr) - sum(y_tr)) / max(1, sum(y_tr)))
        model = XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.8,
                              reg_lambda=5.0, scale_pos_weight=pos_w, eval_metric="logloss",
                              random_state=RANDOM_STATE)
    else:
        raise ValueError(f"Unknown approach: {name}")

    if "Classif" in name:
        model.fit(X_tr_proc, y_tr)
    else:
        model.fit(X_tr_proc, z_tr)
        z_fit = np.clip(model.predict(X_tr_proc), -CLIP_LIMIT, CLIP_LIMIT)
        sigma_resid = max(SIGMA_FLOOR, float(np.std(z_tr - z_fit)))
    return model, sigma_resid, scaler, dropped_cols

def predict_approach_risk(name, model, sigma_resid, scaler, dropped_cols, X_val, z_hi_val, z_lo_val=None):
    """Returns (risk, z_pred or None, clipped_count, clipped_fraction, max_abs_z)."""
    if dropped_cols:
        X_val = X_val.drop(columns=[c for c in dropped_cols if c in X_val.columns])
    X_val_proc = scaler.transform(X_val) if scaler is not None else X_val
    if "Regress" in name:
        raw_z = model.predict(X_val_proc)
        clipped_count = int(np.sum(np.abs(raw_z) > CLIP_LIMIT))
        clipped_fraction = float(clipped_count / len(raw_z)) if len(raw_z) else 0.0
        max_abs_z = float(np.max(np.abs(raw_z))) if len(raw_z) else 0.0
        z_pred = np.clip(raw_z, -CLIP_LIMIT, CLIP_LIMIT)
        risk = risk_from_z(z_pred, sigma_resid, z_hi_val, z_lo_val)
        return risk, z_pred, clipped_count, clipped_fraction, max_abs_z
    risk = model.predict_proba(X_val_proc)[:, 1]
    return risk, None, 0, 0.0, 0.0

# ==============================================================================
# SECTION 8: WALK-FORWARD CV AND MODEL SELECTION
# ==============================================================================
print("\n" + "=" * 100)
print("SECTION 8: Walk-Forward CV & Model Selection")
print("=" * 100)

CANDIDATES = ["Ridge (Regress Risk)", "RF (Regress Risk)", "XGB (Regress Risk)",
              "LogReg (Classif)", "Random Forest (Classif)", "XGBoost (Classif)"]
BASELINES = ["Persistence", "Seasonal Climatology", "Always-Unusual"]

def run_target_cv(target_type, best_alpha):
    is_temp = target_type == "temperature"
    feat_cols = TEMP_FEATURE_COLS if is_temp else PRECIP_FEATURE_COLS
    metrics = {m: [] for m in CANDIDATES + BASELINES}
    msess_log = {"Ridge": [], "RF": [], "XGB": []}
    clip_log = {"Ridge": [], "RF": [], "XGB": []}
    maxz_log = {"Ridge": [], "RF": [], "XGB": []}
    oof_val_risk = {m: [] for m in CANDIDATES}
    oof_y, fold_indices = [], []

    for f_idx, fold in enumerate(FOLDS):
        f_df, _ = construct_fold_dataset(df_full, train_end_year=fold["train_years"][1],
                                         trend_mode="detrended" if is_temp else "fixed",
                                         precip_pool_mode=SELECTED_PRECIP_POOL_MODE)
        tr_m = ((f_df["Year"] >= fold["train_years"][0]) & (f_df["Year"] <= fold["train_years"][1])
                & ~((f_df["Year"] == fold["train_years"][1]) & (f_df["Month"] == 12)))
        va_m = ((f_df["Year"] >= fold["val_years"][0]) & (f_df["Year"] <= fold["val_years"][1])
                & ~f_df["next_temp"].isna())
        if not is_temp and EXCLUDE_DEGENERATE_PRECIP:
            deg_p, _ = get_degenerate_precip_pairs(f_df[tr_m])
            tr_m = tr_m & ~f_df.apply(lambda r: (r["Region"], r["target_month"]) in deg_p, axis=1)
            va_m = va_m & ~f_df.apply(lambda r: (r["Region"], r["target_month"]) in deg_p, axis=1)

        y_col = "target_temp_high" if is_temp else "target_precip_unusual"
        z_col = "temp_z_next" if is_temp else "precip_z_next"
        z_hi_col = "temp_z_hi" if is_temp else "precip_z_hi"
        z_lo_col = None if is_temp else "precip_z_lo"
        persist_col = "persist_temp_signal" if is_temp else "persist_precip_signal"

        X_tr, y_tr, z_tr = f_df.loc[tr_m, feat_cols], f_df.loc[tr_m, y_col].values, f_df.loc[tr_m, z_col].values
        X_va, y_va, z_va = f_df.loc[va_m, feat_cols], f_df.loc[va_m, y_col].values, f_df.loc[va_m, z_col].values
        z_hi_va = f_df.loc[va_m, z_hi_col].values
        z_lo_va = f_df.loc[va_m, z_lo_col].values if z_lo_col else None
        oof_y.extend(y_va)
        fold_indices.extend([f_idx] * len(y_va))

        print(f" -> [{target_type.upper()}] {fold['name']}: train N={len(X_tr)} | validation N={len(X_va)}")

        for cand in CANDIDATES:
            model, sig_res, sc, dc = fit_selected_approach(cand, X_tr, y_tr, z_tr, alpha_chosen=best_alpha)
            risk, z_pred, clip_cnt, clip_frac, max_z = predict_approach_risk(
                cand, model, sig_res, sc, dc, X_va, z_hi_va, z_lo_va)
            oof_val_risk[cand].extend(risk)
            auc_v = roc_auc_score(y_va, risk)
            pr_v = average_precision_score(y_va, risk)
            msess_val = None
            if "Regress" in cand:
                sk = "Ridge" if "Ridge" in cand else ("RF" if "RF" in cand else "XGB")
                mse_c = mean_squared_error(z_va, np.zeros_like(z_va))
                msess_val = 1.0 - (mean_squared_error(z_va, z_pred) / (mse_c + 1e-9))
                msess_log[sk].append(msess_val)
                clip_log[sk].append(clip_frac)
                maxz_log[sk].append(max_z)
            metrics[cand].append({"ROC-AUC": auc_v, "PR-AUC": pr_v})
            results_records.append({
                "Target": target_type, "Split": fold["name"], "Model": cand,
                "ROC_AUC": round(auc_v, 4), "PR_AUC": round(pr_v, 4),
                "MSESS": round(msess_val, 4) if msess_val is not None else "",
                "Clipped_Fraction": round(clip_frac, 4) if "Regress" in cand else 0.0,
                "Max_Abs_Z": round(max_z, 3) if "Regress" in cand else "",
            })

        auc_per = roc_auc_score(y_va, f_df.loc[va_m, persist_col].values)
        pr_per = average_precision_score(y_va, f_df.loc[va_m, persist_col].values)
        metrics["Persistence"].append({"ROC-AUC": auc_per, "PR-AUC": pr_per})
        results_records.append({"Target": target_type, "Split": fold["name"], "Model": "Persistence",
                                "ROC_AUC": round(auc_per, 4), "PR_AUC": round(pr_per, 4)})

        p_clim = smoothed_climatology(f_df[tr_m], f_df.loc[va_m], y_col)
        auc_cl = roc_auc_score(y_va, p_clim)
        pr_cl = average_precision_score(y_va, p_clim)
        metrics["Seasonal Climatology"].append({"ROC-AUC": auc_cl, "PR-AUC": pr_cl})
        results_records.append({"Target": target_type, "Split": fold["name"], "Model": "Seasonal Climatology",
                                "ROC_AUC": round(auc_cl, 4), "PR_AUC": round(pr_cl, 4)})

        auc_alw = roc_auc_score(y_va, np.ones(len(y_va)))
        metrics["Always-Unusual"].append({"ROC-AUC": auc_alw, "PR-AUC": float(np.mean(y_va))})
        results_records.append({"Target": target_type, "Split": fold["name"], "Model": "Always-Unusual",
                                "ROC_AUC": round(auc_alw, 4), "PR_AUC": round(float(np.mean(y_va)), 4)})

    return metrics, msess_log, clip_log, maxz_log, oof_val_risk, np.array(oof_y), np.array(fold_indices)

cv_res_t, msess_t, clip_t, maxz_t, oof_r_t, oof_y_t, f_idx_t = run_target_cv("temperature", best_alpha_t)
cv_res_p, msess_p, clip_p, maxz_p, oof_r_p, oof_y_p, f_idx_p = run_target_cv("precipitation", best_alpha_p)

def print_cv_and_select(cv_metrics, msess_log, clip_log, maxz_log, target_name):
    print(f"\n--- CV TABLE: {target_name.upper()} ---")
    print(f"{'Approach / Baseline':<25} | {'ROC-AUC':<18} | {'PR-AUC':<18} | {'MSESS (F1,F2,F3)':<26} | {'Max|z| per fold':<18} | {'Eligible':<14}")
    print("-" * 130)
    eligibility, stats = {}, {}
    for m in CANDIDATES + BASELINES:
        aucs = [x["ROC-AUC"] for x in cv_metrics[m]]
        prs = [x["PR-AUC"] for x in cv_metrics[m]]
        stats[m] = {"m_auc": float(np.mean(aucs)), "s_auc": float(np.std(aucs)),
                    "m_pr": float(np.mean(prs)), "s_pr": float(np.std(prs))}
        ms_str, mz_str, elig = "-", "-", "Baseline"
        if "Regress" in m:
            sk = "Ridge" if "Ridge" in m else ("RF" if "RF" in m else "XGB")
            vals = msess_log[sk]
            ms_str = f"{np.mean(vals):+.2f} ({vals[0]:.2f},{vals[1]:.2f},{vals[2]:.2f})"
            mz_str = ",".join(f"{z:.2f}" for z in maxz_log[sk])
            if any(v < MSESS_FLOOR for v in vals):
                elig = f"No (MSESS<{MSESS_FLOOR})"
            elif any(cf > MAX_CLIP_FRACTION for cf in clip_log[sk]):
                elig = f"No (clip>{MAX_CLIP_FRACTION*100:.0f}%)"
            else:
                elig = "Yes"
            eligibility[m] = elig == "Yes"
        elif m in CANDIDATES:
            elig = "Yes"
            eligibility[m] = True
        print(f"{m:<25} | {stats[m]['m_auc']:.3f} +/- {stats[m]['s_auc']:.3f}  | "
              f"{stats[m]['m_pr']:.3f} +/- {stats[m]['s_pr']:.3f}  | {ms_str:<26} | {mz_str:<18} | {elig:<14}")

    eligible = [c for c in CANDIDATES if eligibility.get(c, False)]
    best_cand = max(eligible, key=lambda k: stats[k]["m_auc"])
    selected = best_cand
    for simpler in ["Ridge (Regress Risk)", "LogReg (Classif)"]:
        if simpler in eligible and stats[simpler]["m_auc"] >= stats[best_cand]["m_auc"] - stats[best_cand]["s_auc"]:
            selected = simpler
            break
    best_baseline = max(BASELINES, key=lambda b: stats[b]["m_auc"])
    print(f" >>> SELECTED APPROACH: '{selected}' (CV ROC-AUC {stats[selected]['m_auc']:.3f})")
    if selected != best_cand:
        print(f"     [Parsimony] over '{best_cand}' ({stats[best_cand]['m_auc']:.3f}) within 1 std")
    print(f" >>> BEST CV BASELINE: '{best_baseline}' (CV ROC-AUC {stats[best_baseline]['m_auc']:.3f})")
    return selected, best_baseline, stats

sel_temp_approach, best_base_cv_t, stats_temp_cv = print_cv_and_select(cv_res_t, msess_t, clip_t, maxz_t, "Temperature")
sel_precip_approach, best_base_cv_p, stats_precip_cv = print_cv_and_select(cv_res_p, msess_p, clip_p, maxz_p, "Precipitation")

summary_json["cv_results"] = {
    "temperature": {"selected": sel_temp_approach, "best_cv_baseline": best_base_cv_t, "stats": stats_temp_cv},
    "precipitation": {"selected": sel_precip_approach, "best_cv_baseline": best_base_cv_p, "stats": stats_precip_cv},
}

# ==============================================================================
# SECTION 9: CALIBRATION AND TIER VALIDATION (Fold 3 used for one decision only)
# ==============================================================================
print("\n" + "=" * 100)
print("SECTION 9: Calibration & Tier Validation")
print("=" * 100)

def evaluate_calibration_and_tiers(target_type, selected_name, oof_risk_dict, oof_y, fold_indices):
    is_temp = target_type == "temperature"
    oof_risk = np.array(oof_risk_dict[selected_name])
    mask_12 = (fold_indices == 0) | (fold_indices == 1)
    mask_3 = (fold_indices == 2)

    calibrator = LogisticRegression(C=1.0, solver="lbfgs", random_state=RANDOM_STATE)
    calibrator.fit(oof_risk[mask_12].reshape(-1, 1), oof_y[mask_12])

    raw_brier = float(brier_score_loss(oof_y[mask_3], oof_risk[mask_3]))
    cal_pred_f3 = calibrator.predict_proba(oof_risk[mask_3].reshape(-1, 1))[:, 1]
    cal_brier = float(brier_score_loss(oof_y[mask_3], cal_pred_f3))
    keep_cal = bool(cal_brier < raw_brier)
    print(f"[{target_type.upper()}] Fold 3 Brier: raw {raw_brier:.4f} | calibrated {cal_brier:.4f} -> "
          f"{'KEEP calibrator' if keep_cal else 'KEEP raw risk'}")

    f_final_tr, _ = construct_fold_dataset(df_full, train_end_year=FINAL_TRAIN_END,
                                           trend_mode="detrended" if is_temp else "fixed",
                                           precip_pool_mode=SELECTED_PRECIP_POOL_MODE)
    tr_final = ((f_final_tr["Year"] <= FINAL_TRAIN_END)
                & ~((f_final_tr["Year"] == FINAL_TRAIN_END) & (f_final_tr["Month"] == 12)))
    if not is_temp and EXCLUDE_DEGENERATE_PRECIP:
        deg_fin, _ = get_degenerate_precip_pairs(f_final_tr[tr_final])
        tr_final = tr_final & ~f_final_tr.apply(lambda r: (r["Region"], r["target_month"]) in deg_fin, axis=1)
    y_name = "target_temp_high" if is_temp else "target_precip_unusual"
    tier_base_rate = float(f_final_tr.loc[tr_final, y_name].mean())

    f3_risk = cal_pred_f3 if keep_cal else oof_risk[mask_3]
    f3_lifts = f3_risk / (tier_base_rate + 1e-9)
    tier_df = pd.DataFrame({"y": oof_y[mask_3], "tier": [raw_tier(l) for l in f3_lifts]})

    print(f"[Fold 3 tiers: {target_type.upper()}] training base rate {tier_base_rate*100:.1f}%")
    obs, counts = {}, {}
    for t in ["Low", "Elevated", "High"]:
        sub = tier_df[tier_df["tier"] == t]
        counts[t] = len(sub)
        if len(sub) > 0:
            obs[t] = float(sub["y"].mean())
            print(f"    {t:<9}: rows {len(sub):<4} observed rate {obs[t]*100:5.1f}% lift {obs[t]/(tier_base_rate+1e-9):.2f}x")
        else:
            obs[t] = -1.0
            print(f"    {t:<9}: 0 rows")

    increasing = obs["Low"] < obs["Elevated"] < obs["High"] if min(counts.values()) > 0 else False
    enough_high = counts["High"] >= 10
    tier_validated = bool(increasing and enough_high)
    print(f" -> Tier scheme: {'VALIDATED' if tier_validated else 'NOT VALIDATED'} "
          f"(strictly increasing: {increasing}, High rows >= 10: {enough_high} [N={counts['High']}])")
    return calibrator, keep_cal, tier_base_rate, tier_validated

cal_t, keep_cal_t, base_rate_t, tier_val_t = evaluate_calibration_and_tiers(
    "temperature", sel_temp_approach, oof_r_t, oof_y_t, f_idx_t)
cal_p, keep_cal_p, base_rate_p, tier_val_p = evaluate_calibration_and_tiers(
    "precipitation", sel_precip_approach, oof_r_p, oof_y_p, f_idx_p)

# ==============================================================================
# SECTION 10: PERMUTATION IMPORTANCE (Fold 3 validation only)
# ==============================================================================
print("\n" + "=" * 100)
print("SECTION 10: Permutation Importance (Fold 3 validation split)")
print("=" * 100)

def compute_fold3_permutation_importance(target_type, selected_name, alpha):
    is_temp = target_type == "temperature"
    feat_cols = TEMP_FEATURE_COLS if is_temp else PRECIP_FEATURE_COLS
    f_df, _ = construct_fold_dataset(df_full, train_end_year=2018,
                                     trend_mode="detrended" if is_temp else "fixed",
                                     precip_pool_mode=SELECTED_PRECIP_POOL_MODE)
    tr_m = (f_df["Year"] <= 2018) & ~((f_df["Year"] == 2018) & (f_df["Month"] == 12))
    va_m = (f_df["Year"] >= 2019) & (f_df["Year"] <= 2021) & ~f_df["next_temp"].isna()
    if not is_temp and EXCLUDE_DEGENERATE_PRECIP:
        deg_p, _ = get_degenerate_precip_pairs(f_df[tr_m])
        tr_m = tr_m & ~f_df.apply(lambda r: (r["Region"], r["target_month"]) in deg_p, axis=1)
        va_m = va_m & ~f_df.apply(lambda r: (r["Region"], r["target_month"]) in deg_p, axis=1)
    y_col = "target_temp_high" if is_temp else "target_precip_unusual"
    z_col = "temp_z_next" if is_temp else "precip_z_next"

    X_tr = f_df.loc[tr_m, feat_cols]
    y_tr, z_tr = f_df.loc[tr_m, y_col].values, f_df.loc[tr_m, z_col].values
    X_va = f_df.loc[va_m, feat_cols]
    y_va, z_va = f_df.loc[va_m, y_col].values, f_df.loc[va_m, z_col].values

    model, _, sc, dc = fit_selected_approach(selected_name, X_tr, y_tr, z_tr, alpha_chosen=alpha)
    if dc:
        X_va = X_va.drop(columns=dc)
    X_va_proc = sc.transform(X_va) if sc is not None else X_va
    is_reg = "Regress" in selected_name
    scoring = "neg_mean_squared_error" if is_reg else "roc_auc"
    target_eval = z_va if is_reg else y_va
    perm = permutation_importance(model, X_va_proc, target_eval, scoring=scoring,
                                  n_repeats=5, random_state=RANDOM_STATE)
    actual = [c for c in feat_cols if c not in dc]
    print(f"\n[{target_type.upper()} | {selected_name} | scoring: {scoring}]")
    for rank, idx in enumerate(perm.importances_mean.argsort()[::-1][:10], 1):
        print(f"   {rank:2d}. {actual[idx]:<26}: {perm.importances_mean[idx]:+.4f}")
    neg = [actual[i] for i in range(len(actual)) if perm.importances_mean[i] < 0]
    print(f" -> Negative mean importance ({len(neg)}): {neg}")

compute_fold3_permutation_importance("temperature", sel_temp_approach, best_alpha_t)
compute_fold3_permutation_importance("precipitation", sel_precip_approach, best_alpha_p)

# ==============================================================================
# SECTION 11: FREEZE DECISIONS (write once, compare on every later run)
# ==============================================================================
print("\n" + "=" * 100)
print("SECTION 11: Freeze Decisions")
print("=" * 100)

frozen_decisions = {
    "selected_models": {
        "temperature": {"approach": sel_temp_approach, "alpha": best_alpha_t, "cv_baseline": best_base_cv_t},
        "precipitation": {"approach": sel_precip_approach, "alpha": best_alpha_p,
                          "cv_baseline": best_base_cv_p, "pooling_mode": SELECTED_PRECIP_POOL_MODE},
    },
    "calibration_decisions": {"temperature_calibrator_kept": keep_cal_t,
                              "precipitation_calibrator_kept": keep_cal_p},
    "tier_validation_status": {"temperature": tier_val_t, "precipitation": tier_val_p},
}

if os.path.exists(FROZEN_CONFIG_FILE):
    with open(FROZEN_CONFIG_FILE) as ff:
        old_frozen = json.load(ff)
    old_decisions = {k: old_frozen[k] for k in frozen_decisions}
    if old_decisions != frozen_decisions:
        raise RuntimeError("Decisions in this run differ from frozen_config_v6.json. "
                           "Refusing to continue: the frozen decisions must not change.")
    print(f" -> Decisions match the existing {FROZEN_CONFIG_FILE}. File left unchanged.")
else:
    frozen_out = {
        "config": summary_json["config"],
        "script_sha256": script_sha256,
        "frozen_timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        **frozen_decisions,
    }
    with open(FROZEN_CONFIG_FILE, "w") as ff:
        json.dump(frozen_out, ff, indent=2)
    print(f" -> Frozen config written: {os.path.abspath(FROZEN_CONFIG_FILE)}")

# ==============================================================================
# SECTION 12: LIVE FORECAST AND MODEL BUNDLE (uses labeled data only, no test)
# ==============================================================================
print("\n" + "=" * 100)
print("SECTION 12: Live Forecast & Model Bundle")
print("=" * 100)

latest_y = int(df["Year"].max())
latest_m = int(df.loc[df["Year"] == latest_y, "Month"].max())
pred_m = (latest_m % 12) + 1
pred_y = latest_y if latest_m < 12 else latest_y + 1

f_live_t, _ = construct_fold_dataset(df_full, train_end_year=latest_y, trend_mode="detrended")
f_live_p, _ = construct_fold_dataset(df_full, train_end_year=latest_y, trend_mode="fixed",
                                     precip_pool_mode=SELECTED_PRECIP_POOL_MODE)
tr_live_t = ~f_live_t["next_temp"].isna()
tr_live_p = ~f_live_p["next_precip"].isna()
live_row_mask_t = (f_live_t["Year"] == latest_y) & (f_live_t["Month"] == latest_m)
live_row_mask_p = (f_live_p["Year"] == latest_y) & (f_live_p["Month"] == latest_m)
live_regions = f_live_t.loc[live_row_mask_t, "Region"].values
assert np.array_equal(live_regions, f_live_p.loc[live_row_mask_p, "Region"].values), "Region order mismatch"

degen_pairs_live, _ = get_degenerate_precip_pairs(f_live_p[tr_live_p])

# Temperature refit on all labeled rows
m_liv_t, s_liv_t, sc_liv_t, dc_liv_t = fit_selected_approach(
    sel_temp_approach, f_live_t.loc[tr_live_t, TEMP_FEATURE_COLS],
    f_live_t.loc[tr_live_t, "target_temp_high"].values,
    f_live_t.loc[tr_live_t, "temp_z_next"].values, alpha_chosen=best_alpha_t)
risk_liv_t, z_liv_t, _, _, _ = predict_approach_risk(
    sel_temp_approach, m_liv_t, s_liv_t, sc_liv_t, dc_liv_t,
    f_live_t.loc[live_row_mask_t, TEMP_FEATURE_COLS],
    f_live_t.loc[live_row_mask_t, "temp_z_hi"].values, None)
if keep_cal_t:
    risk_liv_t = cal_t.predict_proba(risk_liv_t.reshape(-1, 1))[:, 1]

# Precipitation refit on all labeled rows
m_liv_p, s_liv_p, sc_liv_p, dc_liv_p = fit_selected_approach(
    sel_precip_approach, f_live_p.loc[tr_live_p, PRECIP_FEATURE_COLS],
    f_live_p.loc[tr_live_p, "target_precip_unusual"].values,
    f_live_p.loc[tr_live_p, "precip_z_next"].values, alpha_chosen=best_alpha_p)
risk_liv_p, z_liv_p, _, _, _ = predict_approach_risk(
    sel_precip_approach, m_liv_p, s_liv_p, sc_liv_p, dc_liv_p,
    f_live_p.loc[live_row_mask_p, PRECIP_FEATURE_COLS],
    f_live_p.loc[live_row_mask_p, "precip_z_hi"].values,
    f_live_p.loc[live_row_mask_p, "precip_z_lo"].values)
if keep_cal_p:
    risk_liv_p = cal_p.predict_proba(risk_liv_p.reshape(-1, 1))[:, 1]

p_mu_live = f_live_p.loc[live_row_mask_p, "p_mu"].values
p_sig_live = f_live_p.loc[live_row_mask_p, "p_sig"].values
precip_degen_live = np.array([(r, pred_m) in degen_pairs_live for r in live_regions])

print(f"Latest observation: {latest_y}-{latest_m:02d} | Forecast month: {pred_y}-{pred_m:02d}")
print("-" * 100)
print(f"{'Region':<16} | {'Target':<22} | {'Pred z':<8} | {'Risk':<8} | {'Lift':<7} | {'Tier':<16}")
print("-" * 100)

live_records = []
for i, reg in enumerate(live_regions):
    t_risk = float(risk_liv_t[i])
    t_lift = t_risk / (base_rate_t + 1e-9)
    t_tier = tier_label(t_lift, tier_val_t)
    # LogReg produces no z-score: report NaN, never a fake zero.
    t_z = float(z_liv_t[i]) if z_liv_t is not None else np.nan
    print(f"{reg:<16} | {'Temperature (High)':<22} | "
          f"{('N/A' if np.isnan(t_z) else f'{t_z:+.2f}'):<8} | {t_risk*100:5.1f}%  | {t_lift:5.2f}x | {t_tier:<16}")
    live_records.append({"region": reg, "target": "Temperature (High)",
                         "pred_z": None if np.isnan(t_z) else round(t_z, 2),
                         "risk_pct": round(t_risk * 100, 1), "lift": round(t_lift, 2), "tier": t_tier})

    if precip_degen_live[i]:
        print(f"{reg:<16} | {'Precipitation':<22} | {'N/A':<8} | {'N/A':<8} | {'N/A':<7} | N/A - dry season (degenerate)")
        live_records.append({"region": reg, "target": "Precipitation", "pred_z": None, "risk_pct": None,
                             "lift": None, "tier": "N/A - dry season (degenerate)"})
    else:
        p_risk = float(risk_liv_p[i])
        p_lift = p_risk / (base_rate_p + 1e-9)
        p_tier = tier_label(p_lift, tier_val_p)
        p_z = float(z_liv_p[i])
        print(f"{reg:<16} | {'Precipitation':<22} | {p_z:+.2f}    | {p_risk*100:5.1f}%  | {p_lift:5.2f}x | {p_tier:<16}")
        live_records.append({"region": reg, "target": "Precipitation", "pred_z": round(p_z, 2),
                             "risk_pct": round(p_risk * 100, 1), "lift": round(p_lift, 2), "tier": p_tier})

summary_json["live_forecast"] = {
    "latest_obs": f"{latest_y}-{latest_m:02d}",
    "target_horizon": f"{pred_y}-{pred_m:02d}",
    "records": live_records,
    "calibration": {"temperature": keep_cal_t, "precipitation": keep_cal_p},
}

bundle = {
    "latest_obs": f"{latest_y}-{latest_m:02d}",
    "forecast_year": int(pred_y),
    "forecast_month": int(pred_m),
    "regions": [str(r) for r in live_regions],
    "script_sha256": script_sha256,
    "trained_on": f"2005-{latest_y} (deployment model; includes test years)",
    "temp": {
        "approach": sel_temp_approach, "alpha": best_alpha_t,
        "model": m_liv_t, "scaler": sc_liv_t, "dropped_cols": dc_liv_t,
        "feature_cols": TEMP_FEATURE_COLS, "calibrator": cal_t if keep_cal_t else None,
        "base_rate": float(base_rate_t), "tier_validated": bool(tier_val_t),
        "risk": [float(x) for x in risk_liv_t],
    },
    "precip": {
        "approach": sel_precip_approach, "alpha": best_alpha_p, "pooling_mode": SELECTED_PRECIP_POOL_MODE,
        "model": m_liv_p, "scaler": sc_liv_p, "dropped_cols": dc_liv_p,
        "feature_cols": PRECIP_FEATURE_COLS, "calibrator": cal_p if keep_cal_p else None,
        "base_rate": float(base_rate_p), "tier_validated": bool(tier_val_p),
        "risk": [float(x) for x in risk_liv_p], "z": [float(x) for x in z_liv_p],
        "mu_log": [float(x) for x in p_mu_live], "sig_log": [float(x) for x in p_sig_live],
        "degenerate": [bool(x) for x in precip_degen_live], "unit_status": "UNCONFIRMED",
    },
}
joblib.dump(bundle, BUNDLE_FILE)
print(f"\n -> Model bundle saved: {os.path.abspath(BUNDLE_FILE)}")

# ==============================================================================
# SECTION 13: TEST LOCK (checked AFTER the live step)
# ==============================================================================
print("\n" + "=" * 100)
print("SECTION 13: Test Lock")
print("=" * 100)

lock_exists = os.path.exists(LOCK_FILE)
TEST_ALLOWED = (not lock_exists) or RESET_TEST_LOCK
if lock_exists and not RESET_TEST_LOCK:
    with open(LOCK_FILE) as lf:
        existing_lock = json.load(lf)
    print(f" -> Lock found (timestamp {existing_lock.get('lock_timestamp_utc')}).")
    print(" -> TEST ALREADY EVALUATED. The test section is skipped; the original test results stand.")
elif lock_exists and RESET_TEST_LOCK:
    print(" [WARNING] RESET_TEST_LOCK is True. The test set is being re-used and is NO LONGER untouched.")
else:
    print(" -> No lock found. Test will be evaluated once.")

# ==============================================================================
# SECTION 14: FINAL TEST (runs only if TEST_ALLOWED)
# ==============================================================================
def run_final_test_evaluation(target_type, selected_name, best_baseline_name, calibrator, keep_cal,
                              tier_base_rate, tier_validated, best_alpha, stats_cv):
    is_temp = target_type == "temperature"
    feat_cols = TEMP_FEATURE_COLS if is_temp else PRECIP_FEATURE_COLS
    f_df, _ = construct_fold_dataset(df_full, train_end_year=FINAL_TRAIN_END,
                                     trend_mode="detrended" if is_temp else "fixed",
                                     precip_pool_mode=SELECTED_PRECIP_POOL_MODE)
    tr_m = ((f_df["Year"] <= FINAL_TRAIN_END)
            & ~((f_df["Year"] == FINAL_TRAIN_END) & (f_df["Month"] == 12)))
    te_m = ((f_df["Year"] >= TEST_YEARS[0]) & (f_df["Year"] <= TEST_YEARS[1]) & ~f_df["next_temp"].isna())
    if not is_temp and EXCLUDE_DEGENERATE_PRECIP:
        deg_p, _ = get_degenerate_precip_pairs(f_df[tr_m])
        tr_m = tr_m & ~f_df.apply(lambda r: (r["Region"], r["target_month"]) in deg_p, axis=1)
        te_m = te_m & ~f_df.apply(lambda r: (r["Region"], r["target_month"]) in deg_p, axis=1)

    y_col = "target_temp_high" if is_temp else "target_precip_unusual"
    z_col = "temp_z_next" if is_temp else "precip_z_next"
    z_hi_col = "temp_z_hi" if is_temp else "precip_z_hi"
    z_lo_col = None if is_temp else "precip_z_lo"
    persist_col = "persist_temp_signal" if is_temp else "persist_precip_signal"

    X_tr, y_tr, z_tr = f_df.loc[tr_m, feat_cols], f_df.loc[tr_m, y_col].values, f_df.loc[tr_m, z_col].values
    X_te, y_te = f_df.loc[te_m, feat_cols], f_df.loc[te_m, y_col].values
    z_hi_te = f_df.loc[te_m, z_hi_col].values
    z_lo_te = f_df.loc[te_m, z_lo_col].values if z_lo_col else None

    model, s_res, sc, dc = fit_selected_approach(selected_name, X_tr, y_tr, z_tr, alpha_chosen=best_alpha)
    raw_risk, z_pred_te, clip_cnt, clip_frac, max_z = predict_approach_risk(
        selected_name, model, s_res, sc, dc, X_te, z_hi_te, z_lo_te)
    final_risk = calibrator.predict_proba(raw_risk.reshape(-1, 1))[:, 1] if keep_cal else raw_risk

    p_persist = f_df.loc[te_m, persist_col].values
    p_clim = smoothed_climatology(f_df[tr_m], f_df.loc[te_m], y_col)
    baseline_map = {"Persistence": p_persist, "Seasonal Climatology": p_clim,
                    "Always-Unusual": np.ones(len(y_te))}
    b_probs = baseline_map[best_baseline_name]

    auc_m = float(roc_auc_score(y_te, final_risk))
    auc_b = float(roc_auc_score(y_te, b_probs))
    pr_m = float(average_precision_score(y_te, final_risk))
    pr_b = float(average_precision_score(y_te, b_probs))
    brier_m = float(brier_score_loss(y_te, final_risk))
    brier_b = float(brier_score_loss(y_te, b_probs))
    test_base_rate = float(np.mean(y_te))

    print("\n" + "-" * 95)
    print(f"TEST RESULTS: {target_type.upper()} ({len(y_te)} rows)")
    print("-" * 95)
    print(f"Approach / frozen baseline : {selected_name} vs {best_baseline_name}")
    print(f"ROC-AUC                    : model {auc_m:.3f} | baseline {auc_b:.3f} | diff {auc_m-auc_b:+.3f}")
    print(f"PR-AUC                     : model {pr_m:.3f} | baseline {pr_b:.3f}")
    print(f"Brier                      : model {brier_m:.4f} | baseline {brier_b:.4f}")
    print(f"Base rates                 : training {tier_base_rate*100:.1f}% | test {test_base_rate*100:.1f}%")

    # Tier table: lift against training base rate (the frozen reference) and against test base rate
    lifts_tr = final_risk / (tier_base_rate + 1e-9)
    tier_df = pd.DataFrame({"y": y_te, "tier": [raw_tier(l) for l in lifts_tr]})
    print(f"\n[Test tiers | scheme {'VALIDATED' if tier_validated else 'NOT VALIDATED'}]")
    print(f"{'Tier':<10} | {'Rows':<5} | {'Observed rate':<14} | {'Lift vs train':<14} | {'Lift vs test':<12}")
    for t in ["Low", "Elevated", "High"]:
        sub = tier_df[tier_df["tier"] == t]
        if len(sub) > 0:
            o = float(sub["y"].mean())
            print(f"{t:<10} | {len(sub):<5} | {o*100:9.1f}%     | {o/(tier_base_rate+1e-9):8.2f}x     | {o/(test_base_rate+1e-9):6.2f}x")
        else:
            print(f"{t:<10} | 0     | N/A")

    years = f_df.loc[te_m, "Year"].values
    regions = f_df.loc[te_m, "Region"].values
    year_perf, years_beaten = {}, 0
    print("\n[By year]")
    for yr in [2022, 2023, 2024]:
        mk = years == yr
        n_yr = int(mk.sum())
        if len(np.unique(y_te[mk])) > 1:
            a_m = float(roc_auc_score(y_te[mk], final_risk[mk]))
            a_b = float(roc_auc_score(y_te[mk], b_probs[mk]))
            beat = bool(a_m > a_b)
            years_beaten += int(beat)
            year_perf[str(yr)] = {"N": n_yr, "model_auc": a_m, "baseline_auc": a_b, "model_beat_baseline": beat}
            print(f"  {yr} (N={n_yr}): model {a_m:.3f} | baseline {a_b:.3f} | model better: {beat}")
        else:
            year_perf[str(yr)] = {"N": n_yr, "model_auc": None, "baseline_auc": None, "model_beat_baseline": False}
            print(f"  {yr} (N={n_yr}): single class")

    print("\n[By region]")
    reg_perf = {}
    for r in sorted(np.unique(regions)):
        mk = regions == r
        n_reg, n_pos = int(mk.sum()), int(y_te[mk].sum())
        auc_r = float(roc_auc_score(y_te[mk], final_risk[mk])) if len(np.unique(y_te[mk])) > 1 else None
        reg_perf[r] = {"N": n_reg, "positives": n_pos, "auc": auc_r}
        warn = "  [WARNING: small N or few events]" if (n_reg < 30 or n_pos < 5) else ""
        print(f"  {r:<16}: AUC {('%.3f' % auc_r) if auc_r is not None else 'single class'} (N={n_reg}, positives={n_pos}){warn}")

    # Cluster bootstrap over Region x Year (15 clusters)
    tdf = pd.DataFrame({"Region": regions, "Year": years, "y": y_te, "m": final_risk, "b": b_probs})
    clusters = sorted(set(zip(tdf["Region"], tdf["Year"])))
    cl_idx = {c: tdf.index[(tdf["Region"] == c[0]) & (tdf["Year"] == c[1])].values for c in clusters}
    rng = np.random.RandomState(RANDOM_STATE)
    diffs, distinct = [], set()
    for _ in range(BOOTSTRAP_REPS):
        draw = rng.choice(len(clusters), size=len(clusters), replace=True)
        distinct.add(tuple(sorted(draw)))
        idx = np.concatenate([cl_idx[clusters[i]] for i in draw])
        by = tdf.loc[idx, "y"].values
        if len(np.unique(by)) > 1:
            diffs.append(roc_auc_score(by, tdf.loc[idx, "m"].values) - roc_auc_score(by, tdf.loc[idx, "b"].values))
    ci_lo = float(np.percentile(diffs, 2.5))
    ci_hi = float(np.percentile(diffs, 97.5))
    print(f"\n[Cluster bootstrap] distinct draws {len(distinct)}/{BOOTSTRAP_REPS} | "
          f"95% CI of AUC(model) - AUC(baseline): [{ci_lo:+.3f}, {ci_hi:+.3f}]")
    print(" -> Caveat: clusters in the same year are correlated; this interval is optimistic.")

    cv_stats = stats_cv
    cv_beat = cv_stats[selected_name]["m_auc"] > cv_stats[best_baseline_name]["m_auc"]
    verdict = compute_verdict(auc_m - auc_b, ci_lo, cv_beat, years_beaten, best_baseline_name, auc_b)
    print(f"\n >>> {target_type.upper()} VERDICT: {verdict['verdict']} <<<")

    return {
        "target": target_type, "selected_name": selected_name, "best_baseline_name": best_baseline_name,
        "test_auc": auc_m, "baseline_test_auc": auc_b, "diff_auc": auc_m - auc_b,
        "pr_auc": pr_m, "baseline_pr_auc": pr_b,
        "brier_model": brier_m, "brier_baseline": brier_b,
        "test_base_rate": test_base_rate, "training_base_rate": float(tier_base_rate),
        "ci_lower": ci_lo, "ci_upper": ci_hi, "distinct_bootstrap_draws": len(distinct),
        "years_beaten_count": years_beaten, "year_performance": year_perf,
        "region_performance": reg_perf, "verdict": verdict, "rows_evaluated": int(len(y_te)),
        "alpha": best_alpha,
    }

final_t, final_p = None, None
if TEST_ALLOWED:
    # Write the lock BEFORE evaluating so a crash mid-run cannot be followed by a silent re-run.
    with open(LOCK_FILE, "w") as lf:
        json.dump({"locked": True, "status": "started",
                   "lock_timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   "script_sha256": script_sha256, "reset_test_lock": RESET_TEST_LOCK,
                   "test_years": list(TEST_YEARS)}, lf, indent=2)

    final_t = run_final_test_evaluation("temperature", sel_temp_approach, best_base_cv_t, cal_t,
                                        keep_cal_t, base_rate_t, tier_val_t, best_alpha_t, stats_temp_cv)
    final_p = run_final_test_evaluation("precipitation", sel_precip_approach, best_base_cv_p, cal_p,
                                        keep_cal_p, base_rate_p, tier_val_p, best_alpha_p, stats_precip_cv)

    with open(LOCK_FILE, "w") as lf:
        json.dump({"locked": True, "status": "completed",
                   "lock_timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   "script_sha256": script_sha256, "reset_test_lock": RESET_TEST_LOCK,
                   "test_years": list(TEST_YEARS),
                   "temperature": {"approach": sel_temp_approach, "baseline": best_base_cv_t,
                                   "test_auc": final_t["test_auc"], "verdict": final_t["verdict"]["verdict"]},
                   "precipitation": {"approach": sel_precip_approach, "baseline": best_base_cv_p,
                                     "test_auc": final_p["test_auc"], "verdict": final_p["verdict"]["verdict"]}},
                  lf, indent=2)
    summary_json["final_test"] = {"temperature": final_t, "precipitation": final_p}
    summary_json["final_verdict"] = {"temperature": final_t["verdict"], "precipitation": final_p["verdict"]}

# ==============================================================================
# SECTION 15: LIMITATIONS (values computed in this run)
# ==============================================================================
n_years = len(df_raw["Year"].unique())
lim = [
    f"1. Record length: {n_years} years ({int(df_raw['Year'].min())}-{int(df_raw['Year'].max())}) for "
    f"{len(sorted_regions)} regions. WMO climatological normals use 30 years. Each region-month has about "
    f"{n_years - 1} to {n_years} values before pooling.",
    "2. Regional aggregation: values are averages over large macro-regions and smooth out local extremes.",
    f"3. Precipitation unit: UNCONFIRMED. Regional values run from {float(df_raw['Precipitation_mm'].min()):.2f} "
    f"to {float(df_raw['Precipitation_mm'].max()):.2f}. Results are reported in relative (log-scale) terms.",
    f"4. Warming drift: training base rate for temperature is {base_rate_t*100:.1f}%. "
    f"Detrended base rate drift (test minus train) is {rates['detrended']['drift']*100:+.1f} points; "
    f"fixed-mode drift is {rates['fixed']['drift']*100:+.1f} points.",
    f"5. Degenerate dry-season months: {len(deg_pairs_final)} region-month pairs excluded in the final window. "
    f"Excluded test rows: {excluded_test_rows_count} of {raw_test_rows_total}.",
]
if final_t is not None:
    lim += [
        f"6. Test window: {TEST_YEARS[0]}-{TEST_YEARS[1]}, {final_t['rows_evaluated']} temperature rows and "
        f"{final_p['rows_evaluated']} precipitation rows. Only 3 years, so year-level results vary a lot.",
        "7. Bootstrap: 15 region-year clusters, correlated within a year, so intervals are optimistic.",
        f"8. Development: {DEV_ITERATIONS} iterations. The test years were viewed during development, "
        f"so the test result is not a fully blind holdout.",
    ]
else:
    lim += [
        "6. Test section not executed in this run (lock present). Test figures come from the original sealed run.",
    ]
lim += [
    "9. Outputs are relative risk tiers, not disaster or weather forecasts. External drivers (ENSO/IOD) "
    "were not used because the files were not provided.",
]
limitations_text = "\n".join(lim)
print("\n" + "=" * 100)
print("SECTION 15: LIMITATIONS")
print("=" * 100)
print(limitations_text)
summary_json["limitations"] = limitations_text

# ==============================================================================
# SECTION 16: EXPORT (never overwrites the original sealed outputs during a locked run)
# ==============================================================================
if TEST_ALLOWED:
    out_json, out_csv = SUMMARY_JSON_FILE, RESULTS_CSV_FILE
else:
    out_json, out_csv = "summary_v6_locked_run.json", "results_v6_cv_only.csv"
    print(f"\n [INFO] Locked run: writing to {out_json} and {out_csv}. "
          f"The original {SUMMARY_JSON_FILE} and {RESULTS_CSV_FILE} are untouched.")

pd.DataFrame(results_records).to_csv(out_csv, index=False)
with open(out_json, "w") as jf:
    json.dump(summary_json, jf, indent=2, default=str)

print("\n[Outputs]")
print(f" -> Summary : {os.path.abspath(out_json)}")
print(f" -> Metrics : {os.path.abspath(out_csv)}")
print(f" -> Freeze  : {os.path.abspath(FROZEN_CONFIG_FILE)}")
print(f" -> Lock    : {os.path.abspath(LOCK_FILE)}")
print(f" -> Bundle  : {os.path.abspath(BUNDLE_FILE)}")
print(f"Script SHA-256: {script_sha256}")
print("\nRun complete.")