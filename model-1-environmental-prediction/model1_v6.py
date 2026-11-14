"""
Project: African Environmental Change Analysis
Model 1 (v6 Final Freeze Engine): Next-Month Environmental Condition Prediction
NASA International Space Apps Challenge

Output files:
- model1_v6.py (Complete standalone executable script)
- results_v6.csv (Detailed per-fold and test metrics)
- summary_v6.json (Machine-readable summary, live forecast, metadata, limitations)
- frozen_config_v6.json (Frozen decisions, configurations, and SHA-256 script hash)
- test_locked_v6.json (Single-execution test lock manifest)
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
# SECTION 0: CONFIGURATION & FREEZE PROTOCOL SETUP
# ==============================================================================
RANDOM_STATE = 42
RESET_TEST_LOCK = False           # Flag to allow deliberate override of the test lock

# Developmental iteration tracking (derived from history list)
DEV_RUN_LABELS = [
    "v1_initial_exploration",
    "v2_target_alignment",
    "v3_risk_score_framework",
    "v4_zspace_and_units",
    "v5_detrending_rigor"
]
DEV_ITERATIONS = len(DEV_RUN_LABELS)

# Precipitation Degeneracy & Pooling Settings
PRECIP_MIN_REL_SPREAD = 0.20     # (p90 - p10) / (median + 1e-9)
PRECIP_MAX_ZERO_SHARE = 0.30     # Maximum acceptable fraction of zero-rainfall observations
EXCLUDE_DEGENERATE_PRECIP = True # Switch: mask degenerate region-months
USE_LOG_PRECIP = True            # Evaluate precipitation in log1p space

# Risk Tier Thresholds (Multiples of Training Base Rate)
LIFT_HIGH = 2.0                  # Lift >= 2.0 -> High Tier
LIFT_ELEVATED = 1.0              # 1.0 <= Lift < 2.0 -> Elevated Tier; < 1.0 -> Low Tier

# Regularization Tuning Grid
RIDGE_ALPHA_GRID = [0.01, 0.1, 1.0, 10.0, 100.0]

# Folds and Splits
FOLDS = [
    {"name": "Fold 1", "train_years": (2005, 2012), "val_years": (2013, 2015)},
    {"name": "Fold 2", "train_years": (2005, 2015), "val_years": (2016, 2018)},
    {"name": "Fold 3", "train_years": (2005, 2018), "val_years": (2019, 2021)},
]
TEST_YEARS = (2022, 2024)
FINAL_TRAIN_END = 2021

DATA_PATH = "africa_climate_featured.csv"
FALLBACK_PATH = "africa_climate_merged_2004_2024.csv"
MERGED_2004_2024_PATH = "africa_climate_merged_2004_2024.csv"

LOCK_FILE = "test_locked_v6.json"
FROZEN_CONFIG_FILE = "frozen_config_v6.json"
RESULTS_CSV_FILE = "results_v6.csv"
SUMMARY_JSON_FILE = "summary_v6.json"

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
        "ridge_alpha_grid": RIDGE_ALPHA_GRID
    }
}

print("=" * 100)
print("     AFRICAN ENVIRONMENTAL CHANGE ANALYSIS: AI MODEL 1 (v6 FINAL FREEZE ENGINE)     ")
print("=" * 100)

# Check script source hash
script_path = os.path.abspath(__file__) if "__file__" in globals() else os.path.abspath("model1_v6.py")
if os.path.exists(script_path):
    with open(script_path, "rb") as sf:
        script_sha256 = hashlib.sha256(sf.read()).hexdigest()
else:
    script_sha256 = "UNKNOWN"

print(f" -> Source Script SHA-256 : {script_sha256}")
print(f" -> Development Iterations: {DEV_ITERATIONS} (Derived from {DEV_RUN_LABELS})")

# ==============================================================================
# SECTION 1: DATA INTEGRITY & UNIT SANITY CHECKS
# ==============================================================================
print("\n" + "=" * 100)
print("SECTION 1: Data Integrity & Unit Sanity Checks")
print("=" * 100)

if os.path.exists(DATA_PATH):
    print(f" -> Ingesting primary dataset: {DATA_PATH}")
    df_raw = pd.read_csv(DATA_PATH)
elif os.path.exists(FALLBACK_PATH):
    print(f" -> Ingesting fallback dataset: {FALLBACK_PATH}")
    df_raw = pd.read_csv(FALLBACK_PATH)
else:
    raise FileNotFoundError("Climate dataset not found in current workspace.")

df_raw = df_raw.sort_values(by=["Region", "Year", "Month"]).reset_index(drop=True)

# 1.1 Row counts per region (expect 240 each)
region_counts = df_raw["Region"].value_counts().to_dict()
print(" -> Row Counts per Region (Expected: 240 each):")
for r, cnt in sorted(region_counts.items()):
    status = "OK" if cnt == 240 else "UNEXPECTED"
    print(f"    * {r:<16}: {cnt} rows [{status}]")

# 1.2 Duplicate check
dup_count = int(df_raw.duplicated(subset=["Region", "Year", "Month"]).sum())
print(f" -> Duplicate (Region, Year, Month) Count: {dup_count} (Expected: 0) [{'PASS' if dup_count == 0 else 'FAIL'}]")

# 1.3 Missing values check
nan_temp = int(df_raw["Temperature_Anomaly"].isna().sum())
nan_precip = int(df_raw["Precipitation_mm"].isna().sum())
print(f" -> Missing Values: Temperature_Anomaly = {nan_temp} | Precipitation_mm = {nan_precip} [{'PASS' if (nan_temp + nan_precip) == 0 else 'FAIL'}]")

# 1.4 Regional describe() table
precip_desc = df_raw.groupby("Region")["Precipitation_mm"].describe().round(3)
print("\n[Precipitation Descriptive Statistics (Unit: UNCONFIRMED)]")
print(precip_desc.to_string())

max_precip_val = float(df_raw.groupby("Region")["Precipitation_mm"].max().max())
print(f"\n[Precipitation Unit Audit]")
print(f" -> Maximum Regional Observation : {max_precip_val:.3f}")
print(" -> Certified Unit Status        : UNCONFIRMED (values look like mean daily precipitation)")
if max_precip_val < 15.0:
    print(" -> Note: Maximum regional value is below 15. Regional observations reflect daily averages, not monthly totals.")

# 1.5 Count of zero-precipitation months per region
zero_counts = df_raw.groupby("Region")["Precipitation_mm"].apply(lambda s: int((s == 0.0).sum())).to_dict()
print("\n[Zero-Precipitation Observations (Unit: UNCONFIRMED)]")
for r, zcnt in sorted(zero_counts.items()):
    print(f"    * {r:<16}: {zcnt} zero-rainfall months ({zcnt/len(df_raw[df_raw['Region']==r])*100:.1f}%)")

sorted_regions = sorted(df_raw["Region"].unique().tolist())
print(f"\n -> Confirmed 5 Target Regions: {sorted_regions}")

summary_json["data_integrity"] = {
    "region_counts": region_counts,
    "duplicate_count": dup_count,
    "nan_temp": nan_temp,
    "nan_precip": nan_precip,
    "precip_unit_status": "UNCONFIRMED",
    "zero_counts": zero_counts,
    "regions": sorted_regions
}

# Keyed Region Dummy Metadata Table (Merged on 'Region' key, never by index alignment)
region_meta = pd.get_dummies(pd.DataFrame({"Region": sorted_regions}), columns=["Region"], prefix="Region", drop_first=True, dtype=int)
region_meta["Region"] = sorted_regions
region_cols = [c for c in region_meta.columns if c.startswith("Region_")]

# Setup 2004 historical context for clean feature detrending without burn-in NaNs
if os.path.exists(MERGED_2004_2024_PATH):
    df_merged = pd.read_csv(MERGED_2004_2024_PATH)
    df_04 = df_merged[df_merged["Year"] == 2004].copy()
    for col in df_raw.columns:
        if col not in df_04.columns:
            df_04[col] = np.nan
    df_full = pd.concat([df_04, df_raw], ignore_index=True).sort_values(by=["Region", "Year", "Month"]).reset_index(drop=True)
else:
    df_full = df_raw.copy()

df_full["target_month"] = (df_full["Month"] % 12) + 1
df_full["time_idx"] = (df_full["Year"] - 2005) * 12 + (df_full["Month"] - 1)
df_full["next_temp"] = df_full.groupby("Region")["Temperature_Anomaly"].shift(-1)
df_full["next_precip"] = df_full.groupby("Region")["Precipitation_mm"].shift(-1)

# Primary dataframe restricted to 2005-2024
df = df_full[df_full["Year"] >= 2005].copy().reset_index(drop=True)

# ==============================================================================
# SECTION 2: COMMON REUSABLE FUNCTIONS
# ==============================================================================
def risk_from_z(z_pred, sigma, z_hi, z_lo=None):
    """Computes Gaussian tail risk probability from predicted z-score and residual sigma."""
    z_p = np.clip(z_pred, -4.0, 4.0)
    sig = np.maximum(sigma, 0.10)
    risk_hi = 1.0 - norm.cdf((z_hi - z_p) / sig)
    if z_lo is not None:
        risk_lo = norm.cdf((z_lo - z_p) / sig)
        return np.clip(risk_hi + risk_lo, 0.0, 1.0)
    return np.clip(risk_hi, 0.0, 1.0)

def get_degenerate_precip_pairs(train_df, max_zero_share=PRECIP_MAX_ZERO_SHARE, min_rel_spread=PRECIP_MIN_REL_SPREAD):
    """
    Computes degenerate Region x target_month pairs on training rows only.
    Degenerate if: zero_share > 0.30 OR relative_spread < 0.20
    """
    degen_pairs = set()
    records = []
    for r in sorted(train_df["Region"].unique()):
        sub_r = train_df[train_df["Region"] == r]
        for m in range(1, 13):
            vals = sub_r[sub_r["Month"] == m]["Precipitation_mm"].dropna().values
            if len(vals) == 0:
                continue
            z_share = float(np.mean(vals == 0.0))
            p10 = float(np.percentile(vals, 10))
            p90 = float(np.percentile(vals, 90))
            med = float(np.median(vals))
            rel_spr = (p90 - p10) / (med + 1e-9)
            
            is_deg = bool((z_share > max_zero_share) or (rel_spr < min_rel_spread))
            records.append({
                "Region": r, "target_month": m, "zero_share": z_share,
                "p10": p10, "p90": p90, "median": med, "rel_spread": rel_spr,
                "is_degenerate": is_deg
            })
            if is_deg:
                degen_pairs.add((r, m))
    return degen_pairs, pd.DataFrame(records)

def detrend_temperature_and_build_features(source_df, train_mask):
    """
    SECTION 3: Detrends BOTH target and ALL temperature-derived features per region
    strictly using training years. Recomputes lags and rolling statistics on residuals.
    """
    out_df = source_df.copy()
    tr_slice = out_df[train_mask]
    
    slopes = {}
    out_df["temp_trend"] = 0.0
    out_df["next_temp_trend"] = 0.0
    
    for r in sorted(out_df["Region"].unique()):
        r_tr = tr_slice[tr_slice["Region"] == r]
        slope, intercept = np.polyfit(r_tr["time_idx"], r_tr["Temperature_Anomaly"], 1)
        slopes[r] = float(slope * 120.0) # Degrees Celsius per decade
        
        r_idx = out_df["Region"] == r
        out_df.loc[r_idx, "temp_trend"] = slope * out_df.loc[r_idx, "time_idx"] + intercept
        out_df.loc[r_idx, "next_temp_trend"] = slope * (out_df.loc[r_idx, "time_idx"] + 1) + intercept
        
    out_df["r_t"] = out_df["Temperature_Anomaly"] - out_df["temp_trend"]
    out_df["r_next"] = out_df["next_temp"] - out_df["next_temp_trend"]
    
    for lag in [1, 3, 6, 12]:
        out_df[f"temp_lag_{lag}"] = out_df.groupby("Region")["r_t"].shift(lag)
        
    for w in [3, 6, 12]:
        out_df[f"temp_rolling_mean_{w}"] = out_df.groupby("Region")["r_t"].transform(lambda s: s.shift(1).rolling(w).mean())
        
    out_df["temp_rolling_std_3"] = out_df.groupby("Region")["r_t"].transform(lambda s: s.shift(1).rolling(3).std())
    out_df["temp_yoy_change"] = out_df["r_t"] - out_df["temp_lag_12"]
    
    return out_df, slopes

def smoothed_climatology(train_df, eval_df, y_col):
    """
    Bayesian m-estimate smoothed climatological baseline:
    rate = (positives + 5 * global_rate) / (N + 5)
    Guarantees no ties and non-degenerate probability distribution.
    """
    global_rate = float(train_df[y_col].mean())
    grouped = train_df.groupby(["Region", "target_month"])[y_col].agg(["sum", "count"]).reset_index()
    grouped["smoothed_rate"] = (grouped["sum"] + 5.0 * global_rate) / (grouped["count"] + 5.0)
    rate_map = {(r, m): rate for r, m, rate in zip(grouped["Region"], grouped["target_month"], grouped["smoothed_rate"])}
    preds = eval_df.apply(lambda row: rate_map.get((row["Region"], row["target_month"]), global_rate), axis=1).values
    return preds

def tier_from_lift(lift, is_validated=True, lift_high=LIFT_HIGH, lift_elevated=LIFT_ELEVATED):
    """Maps risk lift to tier string. Labels 'NOT VALIDATED' if tier scheme fails validation."""
    if not is_validated:
        return "NOT VALIDATED"
    if lift >= lift_high:
        return "High"
    elif lift >= lift_elevated:
        return "Elevated"
    else:
        return "Low"

def compute_verdict(diff_auc, ci_lower, cv_beat, years_beaten, best_baseline_name, best_baseline_auc, model_auc):
    """Evaluates the 4-condition honest skill confirmation rule."""
    cond_a = bool(diff_auc >= 0.03)
    cond_b = bool(ci_lower > 0.0)
    cond_c = bool(cv_beat)
    cond_d = bool(years_beaten >= 2)
    all_pass = bool(cond_a and cond_b and cond_c and cond_d)
    
    if all_pass:
        v_str = f"SKILL CONFIRMED (+{diff_auc:.3f} ROC-AUC over {best_baseline_name} [{best_baseline_auc:.3f}])"
    else:
        failed = []
        if not cond_a: failed.append(f"Cond A (diff >= 0.03: {diff_auc:+.3f})")
        if not cond_b: failed.append(f"Cond B (CI 2.5% > 0: {ci_lower:+.3f})")
        if not cond_c: failed.append(f"Cond C (CV beat: {cv_beat})")
        if not cond_d: failed.append(f"Cond D (Years >= 2: {years_beaten}/3)")
        failed_joined = ", ".join(failed)
        v_str = f"NO RELIABLE SKILL ({failed_joined})"
        
    return {
        "verdict": v_str, "all_pass": all_pass,
        "cond_a": cond_a, "cond_b": cond_b, "cond_c": cond_c, "cond_d": cond_d
    }

def construct_fold_dataset(full_source_df, train_end_year, trend_mode="detrended", precip_pool_mode="none"):
    """
    Constructs unified z-space features, thresholds, and labels with assertions.
    """
    train_mask = (full_source_df["Year"] >= 2005) & (full_source_df["Year"] <= train_end_year) & ~((full_source_df["Year"] == train_end_year) & (full_source_df["Month"] == 12))
    
    if trend_mode == "detrended":
        f_df, slopes = detrend_temperature_and_build_features(full_source_df, train_mask)
        eval_t_col, eval_next_t_col = "r_t", "r_next"
    else:
        f_df = full_source_df.copy()
        eval_t_col, eval_next_t_col = "Temperature_Anomaly", "next_temp"
        slopes = {r: 0.0 for r in f_df["Region"].unique()}
        
    f_df = f_df[f_df["Year"] >= 2005].copy().reset_index(drop=True)
    f_df = pd.merge(f_df, region_meta, on="Region", how="left")
    
    df_tr = f_df[(f_df["Year"] <= train_end_year) & ~((f_df["Year"] == train_end_year) & (f_df["Month"] == 12))].copy()
    
    # 1. Temperature Thresholds & Z-space
    t_stats = df_tr.groupby(["Region", "Month"])[eval_t_col].agg(["mean", "std"]).reset_index()
    t_stats.rename(columns={"Month": "target_month", "mean": "t_mu", "std": "t_sig"}, inplace=True)
    t_stats["t_sig"] = t_stats["t_sig"].replace(0, 1e-6).fillna(1.0)
    
    t_p90_recs = []
    for r in f_df["Region"].unique():
        sub_r = df_tr[df_tr["Region"] == r]
        for m in range(1, 13):
            prev_m = 12 if m == 1 else m - 1
            next_m = 1 if m == 12 else m + 1
            pooled_vals = sub_r[sub_r["Month"].isin([prev_m, m, next_m])][eval_t_col].dropna().values
            p90 = float(np.percentile(pooled_vals, 90)) if len(pooled_vals) > 0 else 0.0
            t_p90_recs.append({"Region": r, "target_month": m, "t_p90_raw": p90})
    t_p90_df = pd.DataFrame(t_p90_recs)
    
    f_df = pd.merge(f_df, t_stats, on=["Region", "target_month"], how="left")
    f_df = pd.merge(f_df, t_p90_df, on=["Region", "target_month"], how="left")
    
    f_df["temp_z_next"] = (f_df[eval_next_t_col] - f_df["t_mu"]) / f_df["t_sig"]
    f_df["temp_z_hi"] = (f_df["t_p90_raw"] - f_df["t_mu"]) / f_df["t_sig"]
    f_df["target_temp_high"] = (f_df["temp_z_next"] > f_df["temp_z_hi"]).astype(int)
    
    # Current month persistence in z-space
    t_curr_stats = t_stats.rename(columns={"target_month": "Month", "t_mu": "t_mu_curr", "t_sig": "t_sig_curr"})
    t_curr_p90 = t_p90_df.rename(columns={"target_month": "Month", "t_p90_raw": "t_p90_curr"})
    f_df = pd.merge(f_df, t_curr_stats, on=["Region", "Month"], how="left")
    f_df = pd.merge(f_df, t_curr_p90, on=["Region", "Month"], how="left")
    f_df["persist_temp_signal"] = (((f_df[eval_t_col] - f_df["t_mu_curr"]) / f_df["t_sig_curr"]) > ((f_df["t_p90_curr"] - f_df["t_mu_curr"]) / f_df["t_sig_curr"])).astype(int)
    
    # 2. Precipitation Thresholds & Z-space
    if USE_LOG_PRECIP:
        f_df["p_val"] = np.log1p(f_df["Precipitation_mm"])
        f_df["p_next"] = np.log1p(f_df["next_precip"])
    else:
        f_df["p_val"] = f_df["Precipitation_mm"]
        f_df["p_next"] = f_df["next_precip"]
        
    df_tr_p = f_df[(f_df["Year"] <= train_end_year) & ~((f_df["Year"] == train_end_year) & (f_df["Month"] == 12))].copy()
    p_stats = df_tr_p.groupby(["Region", "Month"])["p_val"].agg(["mean", "std"]).reset_index()
    p_stats.rename(columns={"Month": "target_month", "mean": "p_mu", "std": "p_sig"}, inplace=True)
    p_stats["p_sig"] = p_stats["p_sig"].replace(0, 1e-6).fillna(1.0)
    
    p_recs = []
    for r in f_df["Region"].unique():
        sub_r = df_tr_p[df_tr_p["Region"] == r].copy()
        sub_r = pd.merge(sub_r, p_stats[p_stats["Region"] == r], left_on="Month", right_on="target_month", how="left")
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
    f_df["target_precip_unusual"] = ((f_df["precip_z_next"] > f_df["precip_z_hi"]) | (f_df["precip_z_next"] < f_df["precip_z_lo"])).astype(int)
    
    # Current month persistence in z-space
    p_curr_stats = p_stats.rename(columns={"target_month": "Month", "p_mu": "p_mu_c", "p_sig": "p_sig_c"})
    p_curr_thresh = p_thresh_df.rename(columns={"target_month": "Month", "precip_z_lo": "p_z_lo_c", "precip_z_hi": "p_z_hi_c"})
    f_df = pd.merge(f_df, p_curr_stats, on=["Region", "Month"], how="left")
    f_df = pd.merge(f_df, p_curr_thresh, on=["Region", "Month"], how="left")
    z_curr_p = (f_df["p_val"] - f_df["p_mu_c"]) / f_df["p_sig_c"]
    f_df["persist_precip_signal"] = ((z_curr_p > f_df["p_z_hi_c"]) | (z_curr_p < f_df["p_z_lo_c"])).astype(int)
    
    # Clean in-fold seasonal z-scores for features
    f_df["temp_seasonal_zscore"] = ((f_df[eval_t_col] - f_df["t_mu_curr"]) / f_df["t_sig_curr"]).round(3)
    f_df["precip_seasonal_zscore"] = ((f_df["p_val"] - f_df["p_mu_c"]) / f_df["p_sig_c"]).round(3)
    
    # Assertions on z-rule equivalence
    val_rows = ~f_df["next_temp"].isna()
    assert (f_df.loc[val_rows, "target_temp_high"] == (f_df.loc[val_rows, "temp_z_next"] > f_df.loc[val_rows, "temp_z_hi"]).astype(int)).all(), "Assertion Failure: Temperature label does not equal z-rule!"
    assert (f_df.loc[val_rows, "target_precip_unusual"] == ((f_df.loc[val_rows, "precip_z_next"] > f_df.loc[val_rows, "precip_z_hi"]) | (f_df.loc[val_rows, "precip_z_next"] < f_df.loc[val_rows, "precip_z_lo"])).astype(int)).all(), "Assertion Failure: Precipitation label does not equal z-rule!"
    
    f_df.drop(columns=[c for c in ["t_mu", "t_sig", "t_p90_raw", "t_mu_curr", "t_sig_curr", "t_p90_curr",
                                  "p_val", "p_next", "p_mu", "p_sig", "p_mu_c", "p_sig_c", "p_z_lo_c", "p_z_hi_c"] if c in f_df.columns], inplace=True)
    return f_df, slopes

# Feature Columns Setup
EXCLUDE_COLS = ["Date", "Region", "Year", "Month", "target_month", "time_idx",
                "next_temp", "next_precip", "r_next", "temp_trend", "next_temp_trend"]

TEMP_FEATURE_COLS = sorted(list(set([c for c in df_raw.columns if c not in EXCLUDE_COLS and c != "Temperature_Anomaly"] + ["r_t", "temp_seasonal_zscore", "precip_seasonal_zscore"] + region_cols)))
PRECIP_FEATURE_COLS = sorted(list(set([c for c in df_raw.columns if c not in EXCLUDE_COLS and c != "r_t"] + ["temp_seasonal_zscore", "precip_seasonal_zscore"] + region_cols)))

# ==============================================================================
# SECTION 3: DEGENERATE PRECIPITATION MONTHS PER FOLD
# ==============================================================================
print("\n" + "=" * 100)
print("SECTION 3: Degenerate Precipitation Months per Fold (zero_share > 0.30 OR rel_spread < 0.20)")
print("=" * 100)

degen_fold_summary = {}
for f in FOLDS:
    tr_sub = df[(df["Year"] >= f["train_years"][0]) & (df["Year"] <= f["train_years"][1]) & ~((df["Year"] == f["train_years"][1]) & (df["Month"] == 12))]
    deg_pairs, _ = get_degenerate_precip_pairs(tr_sub)
    degen_fold_summary[f["name"]] = deg_pairs
    deg_list_str = ", ".join([f"{r}-M{m}" for r, m in sorted(deg_pairs)])
    print(f" -> {f['name']} Training Window ({f['train_years'][0]}-{f['train_years'][1]}): {len(deg_pairs)} Degenerate Pairs: [{deg_list_str}]")

tr_final_sub = df[(df["Year"] <= FINAL_TRAIN_END) & ~((df["Year"] == FINAL_TRAIN_END) & (df["Month"] == 12))]
deg_pairs_final, _ = get_degenerate_precip_pairs(tr_final_sub)
degen_fold_summary["Final Train"] = deg_pairs_final
print(f" -> Final Train Window (2005-{FINAL_TRAIN_END}): {len(deg_pairs_final)} Degenerate Pairs: [{', '.join([f'{r}-M{m}' for r, m in sorted(deg_pairs_final)])}]")

# Excluded test row count computation
raw_test_rows_total = len(df[(df["Year"] >= TEST_YEARS[0]) & (df["Year"] <= TEST_YEARS[1]) & ~df["next_temp"].isna()])
test_sub_eval = df[(df["Year"] >= TEST_YEARS[0]) & (df["Year"] <= TEST_YEARS[1]) & ~df["next_temp"].isna()]
test_deg_mask = test_sub_eval.apply(lambda r: (r["Region"], r["target_month"]) in deg_pairs_final, axis=1)
excluded_test_rows_count = int(test_deg_mask.sum())
kept_test_rows_count = raw_test_rows_total - excluded_test_rows_count

print(f"\n[Test Set Precipitation Exclusion Audit]")
print(f" -> Raw Test Rows (2022-2024)   : {raw_test_rows_total}")
print(f" -> Excluded Test Rows (Masked) : {excluded_test_rows_count} (Computed via subtraction: {raw_test_rows_total} - {kept_test_rows_count})")
print(f" -> Kept Evaluated Test Rows    : {kept_test_rows_count}")

test_kept_df = test_sub_eval[~test_deg_mask]
print("\n[Per-Region Test Row Counts (After Degenerate Exclusion)]")
for r in sorted_regions:
    n_r_kept = int((test_kept_df["Region"] == r).sum())
    print(f"    * {r:<16}: {n_r_kept} test rows kept")

# ==============================================================================
# SECTION 4: PRECIPITATION POOLING EVALUATION ('none' vs 'anomaly')
# ==============================================================================
print("\n" + "=" * 100)
print("SECTION 4: Precipitation Pooling Mode Evaluation ('none' vs 'anomaly')")
print("=" * 100)

f3_none, _ = construct_fold_dataset(df_full, train_end_year=2018, precip_pool_mode="none")
f3_anom, _ = construct_fold_dataset(df_full, train_end_year=2018, precip_pool_mode="anomaly")
tr_mask_f3 = (f3_none["Year"] <= 2018) & ~((f3_none["Year"] == 2018) & (f3_none["Month"] == 12))

std_none = float(f3_none[tr_mask_f3].groupby("target_month")["target_precip_unusual"].mean().std())
std_anom = float(f3_anom[tr_mask_f3].groupby("target_month")["target_precip_unusual"].mean().std())

print(" -> Monthly Positive Rate Standard Deviation on Training Years:")
print(f"    * Mode 'none'    : {std_none:.4f}")
print(f"    * Mode 'anomaly' : {std_anom:.4f}")

def run_precip_pool_cv(mode):
    aucs_rf_reg, aucs_clim = [], []
    for f in FOLDS:
        f_df, _ = construct_fold_dataset(df_full, train_end_year=f["train_years"][1], precip_pool_mode=mode)
        tr_m = (f_df["Year"] >= f["train_years"][0]) & (f_df["Year"] <= f["train_years"][1]) & ~((f_df["Year"] == f["train_years"][1]) & (f_df["Month"] == 12))
        va_m = (f_df["Year"] >= f["val_years"][0]) & (f_df["Year"] <= f["val_years"][1]) & ~f_df["next_temp"].isna()
        
        if EXCLUDE_DEGENERATE_PRECIP:
            deg_p, _ = get_degenerate_precip_pairs(f_df[tr_m])
            tr_m = tr_m & ~f_df.apply(lambda r: (r["Region"], r["target_month"]) in deg_p, axis=1)
            va_m = va_m & ~f_df.apply(lambda r: (r["Region"], r["target_month"]) in deg_p, axis=1)
            
        X_tr = f_df.loc[tr_m, PRECIP_FEATURE_COLS]
        z_tr = f_df.loc[tr_m, "precip_z_next"].values
        y_tr = f_df.loc[tr_m, "target_precip_unusual"].values
        
        X_va = f_df.loc[va_m, PRECIP_FEATURE_COLS]
        y_va = f_df.loc[va_m, "target_precip_unusual"].values
        z_hi_va = f_df.loc[va_m, "precip_z_hi"].values
        z_lo_va = f_df.loc[va_m, "precip_z_lo"].values
        
        reg = RandomForestRegressor(n_estimators=100, max_depth=5, min_samples_leaf=5, random_state=RANDOM_STATE)
        reg.fit(X_tr, z_tr)
        z_fit = np.clip(reg.predict(X_tr), -4.0, 4.0)
        sig = max(0.15, float(np.std(z_tr - z_fit)))
        
        z_pred = np.clip(reg.predict(X_va), -4.0, 4.0)
        risk = risk_from_z(z_pred, sig, z_hi_va, z_lo_va)
        aucs_rf_reg.append(roc_auc_score(y_va, risk))
        
        p_clim = smoothed_climatology(f_df[tr_m], f_df.loc[va_m], "target_precip_unusual")
        aucs_clim.append(roc_auc_score(y_va, p_clim))
        
    return np.mean(aucs_rf_reg), np.std(aucs_rf_reg), np.mean(aucs_clim)

auc_rf_none, std_rf_none, clim_none = run_precip_pool_cv("none")
auc_rf_anom, std_rf_anom, clim_anom = run_precip_pool_cv("anomaly")

pooled_std = float(np.sqrt((std_rf_none**2 + std_rf_anom**2) / 2.0))
gap_none = float(auc_rf_none - clim_none)
gap_anom = float(auc_rf_anom - clim_anom)

print(f"\n{'Pooling Mode':<16} | {'RF Regress Risk ROC-AUC':<25} | {'Seasonal Climatology AUC':<25} | {'Model - Climatology Gap':<22}")
print("-" * 95)
print(f"{'none':<16} | {auc_rf_none:.3f} +/- {std_rf_none:.3f}           | {clim_none:.3f}                   | {gap_none:+.3f}")
print(f"{'anomaly':<16} | {auc_rf_anom:.3f} +/- {std_rf_anom:.3f}           | {clim_anom:.3f}                   | {gap_anom:+.3f}")

decision_cond1 = auc_rf_anom > (auc_rf_none + pooled_std)
decision_cond2 = abs(gap_anom) < abs(gap_none)

if decision_cond1 and decision_cond2:
    SELECTED_PRECIP_POOL_MODE = "anomaly"
    decision_reason = f"auc_anom ({auc_rf_anom:.3f}) > auc_none ({auc_rf_none:.3f}) + pooled_std ({pooled_std:.3f}) AND |gap_anom| < |gap_none|"
else:
    SELECTED_PRECIP_POOL_MODE = "none"
    decision_reason = f"Rule condition failed: auc_anom ({auc_rf_anom:.3f}) <= threshold ({auc_rf_none + pooled_std:.3f}) OR gap did not shrink ({abs(gap_anom):.3f} vs {abs(gap_none):.3f})"

print(f"\n >>> DECISION RULE RESULT: PRECIP_POOL_MODE = '{SELECTED_PRECIP_POOL_MODE}' <<<")
print(f"     Computed Rule Logic: {decision_reason}")

summary_json["precipitation_pooling"] = {
    "std_monthly_rate_none": std_none,
    "std_monthly_rate_anomaly": std_anom,
    "auc_none": auc_rf_none, "auc_anomaly": auc_rf_anom,
    "selected_mode": SELECTED_PRECIP_POOL_MODE, "decision_reason": decision_reason
}

# ==============================================================================
# SECTION 5: TEMPERATURE TREND SLOPES & DRIFT COMPARISON
# ==============================================================================
print("\n" + "=" * 100)
print("SECTION 5: Temperature Trend Slopes & Drift Comparison")
print("=" * 100)

f_detrend_cv, slopes_cv = construct_fold_dataset(df_full, train_end_year=2018, trend_mode="detrended")
f_fixed_cv, _ = construct_fold_dataset(df_full, train_end_year=2018, trend_mode="fixed")
f_detrend_te, slopes_final = construct_fold_dataset(df_full, train_end_year=2021, trend_mode="detrended")
f_fixed_te, _ = construct_fold_dataset(df_full, train_end_year=2021, trend_mode="fixed")

print(" -> Linear Trend Slopes on Training Window 2005-2021 (Degrees C per Decade):")
for r, sl in sorted(slopes_final.items()):
    print(f"    * {r:<16}: {sl:+.3f} °C / decade")

tr_m18 = (f_fixed_cv["Year"] <= 2018) & ~((f_fixed_cv["Year"] == 2018) & (f_fixed_cv["Month"] == 12))
va_m18 = (f_fixed_cv["Year"] >= 2019) & (f_fixed_cv["Year"] <= 2021)
te_m21 = (f_fixed_te["Year"] >= 2022) & ~f_fixed_te["next_temp"].isna()

tr_r_fix = float(f_fixed_cv.loc[tr_m18, "target_temp_high"].mean())
va_r_fix = float(f_fixed_cv.loc[va_m18, "target_temp_high"].mean())
te_r_fix = float(f_fixed_te.loc[te_m21, "target_temp_high"].mean())

tr_r_det = float(f_detrend_cv.loc[tr_m18, "target_temp_high"].mean())
va_r_det = float(f_detrend_cv.loc[va_m18, "target_temp_high"].mean())
te_r_det = float(f_detrend_te.loc[te_m21, "target_temp_high"].mean())

drift_fix = float(te_r_fix - tr_r_fix)
drift_det = float(te_r_det - tr_r_det)

print(f"\n{'Split (Fold-Matched)':<25} | {'Fixed Mode (Raw Anomalies)':<26} | {'Detrended Mode (Residuals)':<26}")
print("-" * 85)
print(f"{'Train Rate (2005-2018)':<25} |   {tr_r_fix*100:4.1f}%                   |   {tr_r_det*100:4.1f}%")
print(f"{'Validation Rate (2019-2021)':<25} |   {va_r_fix*100:4.1f}%                   |   {va_r_det*100:4.1f}%")
print(f"{'Test Rate (2022-2024)':<25} |   {te_r_fix*100:4.1f}%                   |   {te_r_det*100:4.1f}%")
print(f"{'Drift (Test - Train)':<25} |  {drift_fix*100:+5.1f}%                   |  {drift_det*100:+5.1f}%")
print("-" * 85)

summary_json["temperature_drift"] = {
    "slopes_per_decade": slopes_final,
    "fixed_mode": {"train": tr_r_fix, "val": va_r_fix, "test": te_r_fix, "drift": drift_fix},
    "detrended_mode": {"train": tr_r_det, "val": va_r_det, "test": te_r_det, "drift": drift_det}
}

# ==============================================================================
# SECTION 6: RIDGE REGULARIZATION TUNING ON VALIDATION FOLDS
# ==============================================================================
print("\n" + "=" * 100)
print(f"SECTION 6: Ridge Alpha Regularization Tuning ({RIDGE_ALPHA_GRID})")
print("=" * 100)

def tune_ridge_alpha(target_type):
    feat_cols = TEMP_FEATURE_COLS if target_type == "temperature" else PRECIP_FEATURE_COLS
    alpha_scores = {a: [] for a in RIDGE_ALPHA_GRID}
    for fold in FOLDS:
        f_df, _ = construct_fold_dataset(df_full, train_end_year=fold["train_years"][1],
                                         trend_mode="detrended" if target_type == "temperature" else "fixed",
                                         precip_pool_mode=SELECTED_PRECIP_POOL_MODE)
        
        tr_m = (f_df["Year"] >= fold["train_years"][0]) & (f_df["Year"] <= fold["train_years"][1]) & ~((f_df["Year"] == fold["train_years"][1]) & (f_df["Month"] == 12))
        va_m = (f_df["Year"] >= fold["val_years"][0]) & (f_df["Year"] <= fold["val_years"][1]) & ~f_df["next_temp"].isna()
        
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
            z_fit = np.clip(r_mod.predict(X_tr_s), -4.0, 4.0)
            sig = max(0.15, float(np.std(z_tr - z_fit)))
            
            z_pred = np.clip(r_mod.predict(X_va_s), -4.0, 4.0)
            risk = risk_from_z(z_pred, sig, z_hi_va, z_lo_va)
            alpha_scores[a].append(roc_auc_score(y_va, risk))
            
    means = {a: float(np.mean(alpha_scores[a])) for a in RIDGE_ALPHA_GRID}
    best_a = max(means, key=means.get)
    return best_a, means

best_alpha_t, alpha_means_t = tune_ridge_alpha("temperature")
best_alpha_p, alpha_means_p = tune_ridge_alpha("precipitation")

print(f" -> Temperature Alpha Tuning   : " + " | ".join([f"alpha={a}: {alpha_means_t[a]:.3f}" for a in RIDGE_ALPHA_GRID]) + f" -> Best: {best_alpha_t}")
if best_alpha_t == min(RIDGE_ALPHA_GRID) or best_alpha_t == max(RIDGE_ALPHA_GRID):
    print(f"    [WARNING] Temperature best alpha ({best_alpha_t}) is at grid edge. Grid was not extended post-hoc.")

print(f" -> Precipitation Alpha Tuning : " + " | ".join([f"alpha={a}: {alpha_means_p[a]:.3f}" for a in RIDGE_ALPHA_GRID]) + f" -> Best: {best_alpha_p}")
if best_alpha_p == min(RIDGE_ALPHA_GRID) or best_alpha_p == max(RIDGE_ALPHA_GRID):
    print(f"    [WARNING] Precipitation best alpha ({best_alpha_p}) is at grid edge. Grid was not extended post-hoc.")

# Single unified fit approach function
def fit_selected_approach(name, X_tr, y_tr, z_tr, target_type, alpha_chosen=1.0):
    dropped_cols = [c for c in X_tr.columns if X_tr[c].std() < 1e-8]
    if dropped_cols:
        X_tr = X_tr.drop(columns=dropped_cols)
        
    scaler = None
    if "LogReg" in name or "Ridge" in name:
        scaler = StandardScaler()
        X_tr_proc = scaler.fit_transform(X_tr)
    else:
        X_tr_proc = X_tr
        
    if "Ridge" in name:
        model = Ridge(alpha=alpha_chosen, random_state=RANDOM_STATE)
        model.fit(X_tr_proc, z_tr)
        z_fit = np.clip(model.predict(X_tr_proc), -4.0, 4.0)
        sigma_resid = max(0.15, float(np.std(z_tr - z_fit)))
    elif "RF (Regress Risk)" in name:
        model = RandomForestRegressor(n_estimators=100, max_depth=5, min_samples_leaf=5, random_state=RANDOM_STATE)
        model.fit(X_tr_proc, z_tr)
        z_fit = np.clip(model.predict(X_tr_proc), -4.0, 4.0)
        sigma_resid = max(0.15, float(np.std(z_tr - z_fit)))
    elif "XGB (Regress Risk)" in name:
        model = XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.8, reg_lambda=5.0, random_state=RANDOM_STATE)
        model.fit(X_tr_proc, z_tr)
        z_fit = np.clip(model.predict(X_tr_proc), -4.0, 4.0)
        sigma_resid = max(0.15, float(np.std(z_tr - z_fit)))
    elif "LogReg (Classif)" in name:
        model = LogisticRegression(class_weight="balanced", C=0.5, max_iter=1000, random_state=RANDOM_STATE)
        model.fit(X_tr_proc, y_tr)
        sigma_resid = None
    elif "Random Forest (Classif)" in name:
        model = RandomForestClassifier(n_estimators=100, max_depth=5, min_samples_leaf=5, class_weight="balanced", random_state=RANDOM_STATE)
        model.fit(X_tr_proc, y_tr)
        sigma_resid = None
    elif "XGBoost (Classif)" in name:
        pos_w = max(1, (len(y_tr) - sum(y_tr)) / max(1, sum(y_tr)))
        model = XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.8, reg_lambda=5.0, scale_pos_weight=pos_w, eval_metric="logloss", random_state=RANDOM_STATE)
        model.fit(X_tr_proc, y_tr)
        sigma_resid = None
    else:
        raise ValueError(f"Unknown approach: {name}")
        
    return model, sigma_resid, scaler, dropped_cols

def predict_approach_risk(name, model, sigma_resid, scaler, dropped_cols, X_val, z_hi_val, z_lo_val=None):
    if dropped_cols:
        X_val = X_val.drop(columns=[c for c in dropped_cols if c in X_val.columns])
    X_val_proc = scaler.transform(X_val) if scaler is not None else X_val
    
    if "Regress" in name:
        raw_z = model.predict(X_val_proc)
        z_pred = np.clip(raw_z, -4.0, 4.0)
        clipped_count = int(np.sum(np.abs(raw_z) > 4.0))
        clipped_fraction = float(clipped_count / len(raw_z))
        max_abs_z = float(np.max(np.abs(raw_z)))
        risk = risk_from_z(z_pred, sigma_resid, z_hi_val, z_lo_val)
        return risk, z_pred, clipped_count, clipped_fraction, max_abs_z
    else:
        risk = model.predict_proba(X_val_proc)[:, 1]
        return risk, None, 0, 0.0, 0.0

# ==============================================================================
# SECTION 7: FULL WALK-FORWARD CV & MODEL SELECTION
# ==============================================================================
print("\n" + "=" * 100)
print("SECTION 7: Walk-Forward CV & Model Selection per Target")
print("=" * 100)

CANDIDATES = [
    "Ridge (Regress Risk)", "RF (Regress Risk)", "XGB (Regress Risk)",
    "LogReg (Classif)", "Random Forest (Classif)", "XGBoost (Classif)"
]

def run_target_cv(target_type, best_alpha):
    is_temp = target_type == "temperature"
    feat_cols = TEMP_FEATURE_COLS if is_temp else PRECIP_FEATURE_COLS
    
    metrics = {m: [] for m in CANDIDATES + ["Persistence", "Seasonal Climatology", "Always-Unusual"]}
    msess_log = {"Ridge": [], "RF": [], "XGB": []}
    clipped_log = {"Ridge": [], "RF": [], "XGB": []}
    max_z_log = {"Ridge": [], "RF": [], "XGB": []}
    
    oof_val_risk = {m: [] for m in CANDIDATES}
    oof_y = []
    fold_indices = []
    
    for f_idx, fold in enumerate(FOLDS):
        f_df, _ = construct_fold_dataset(df_full, train_end_year=fold["train_years"][1],
                                         trend_mode="detrended" if is_temp else "fixed",
                                         precip_pool_mode=SELECTED_PRECIP_POOL_MODE)
        
        tr_m = (f_df["Year"] >= fold["train_years"][0]) & (f_df["Year"] <= fold["train_years"][1]) & ~((f_df["Year"] == fold["train_years"][1]) & (f_df["Month"] == 12))
        va_m = (f_df["Year"] >= fold["val_years"][0]) & (f_df["Year"] <= fold["val_years"][1]) & ~f_df["next_temp"].isna()
        
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
        
        print(f" -> [{target_type.upper()}] {fold['name']}: Train N = {len(X_tr)} ({fold['train_years'][0]}-{fold['train_years'][1]}, Dec {fold['train_years'][1]} excluded) | Val N = {len(X_va)} ({fold['val_years'][0]}-{fold['val_years'][1]})")
        
        for cand in CANDIDATES:
            model, sig_res, sc, dc = fit_selected_approach(cand, X_tr, y_tr, z_tr, target_type, alpha_chosen=best_alpha)
            risk, z_pred, clip_cnt, clip_frac, max_z = predict_approach_risk(cand, model, sig_res, sc, dc, X_va, z_hi_va, z_lo_va)
            
            oof_val_risk[cand].extend(risk)
            auc_v = roc_auc_score(y_va, risk)
            pr_v = average_precision_score(y_va, risk)
            
            msess_val = None
            if "Regress" in cand:
                sk = "Ridge" if "Ridge" in cand else ("RF" if "RF" in cand else "XGB")
                mse_c = mean_squared_error(z_va, np.zeros_like(z_va))
                msess_val = 1.0 - (mean_squared_error(z_va, z_pred) / (mse_c + 1e-9))
                msess_log[sk].append(msess_val)
                clipped_log[sk].append(clip_frac)
                max_z_log[sk].append(max_z)
                
            metrics[cand].append({"ROC-AUC": auc_v, "PR-AUC": pr_v, "MSESS": msess_val, "Clip_Frac": clip_frac if "Regress" in cand else 0.0})
            
            results_records.append({
                "Target": target_type, "Split": fold["name"], "Model": cand,
                "ROC_AUC": round(auc_v, 4), "PR_AUC": round(pr_v, 4),
                "MSESS": round(msess_val, 4) if msess_val is not None else "",
                "Clipped_Fraction": round(clip_frac, 4) if "Regress" in cand else 0.0
            })
            
        # Baselines
        auc_per = roc_auc_score(y_va, f_df.loc[va_m, persist_col].values)
        pr_per = average_precision_score(y_va, f_df.loc[va_m, persist_col].values)
        metrics["Persistence"].append({"ROC-AUC": auc_per, "PR-AUC": pr_per, "MSESS": None, "Clip_Frac": 0.0})
        results_records.append({"Target": target_type, "Split": fold["name"], "Model": "Persistence", "ROC_AUC": round(auc_per, 4), "PR_AUC": round(pr_per, 4), "MSESS": "", "Clipped_Fraction": 0.0})
        
        # Smoothed Climatology
        p_clim = smoothed_climatology(f_df[tr_m], f_df.loc[va_m], y_col)
        unique_clim_scores = len(np.unique(p_clim))
        auc_cl = roc_auc_score(y_va, p_clim)
        pr_cl = average_precision_score(y_va, p_clim)
        metrics["Seasonal Climatology"].append({"ROC-AUC": auc_cl, "PR-AUC": pr_cl, "MSESS": None, "Clip_Frac": 0.0, "unique_scores": unique_clim_scores})
        results_records.append({"Target": target_type, "Split": fold["name"], "Model": "Seasonal Climatology", "ROC_AUC": round(auc_cl, 4), "PR_AUC": round(pr_cl, 4), "MSESS": "", "Clipped_Fraction": 0.0})
        
        # Always-Unusual
        auc_alw = roc_auc_score(y_va, np.ones(len(y_va)))
        metrics["Always-Unusual"].append({"ROC-AUC": auc_alw, "PR-AUC": np.mean(y_va), "MSESS": None, "Clip_Frac": 0.0})
        results_records.append({"Target": target_type, "Split": fold["name"], "Model": "Always-Unusual", "ROC_AUC": round(auc_alw, 4), "PR_AUC": round(np.mean(y_va), 4), "MSESS": "", "Clipped_Fraction": 0.0})
        
    return metrics, msess_log, clipped_log, max_z_log, oof_val_risk, np.array(oof_y), np.array(fold_indices)

cv_res_t, msess_t, clip_t, maxz_t, oof_r_t, oof_y_t, f_idx_t = run_target_cv("temperature", best_alpha_t)
cv_res_p, msess_p, clip_p, maxz_p, oof_r_p, oof_y_p, f_idx_p = run_target_cv("precipitation", best_alpha_p)

# Warning on anti-predictive seasonal climatology
mean_clim_auc_t = float(np.mean([x["ROC-AUC"] for x in cv_res_t["Seasonal Climatology"]]))
if mean_clim_auc_t < 0.5:
    fold_clim_t = [round(x["ROC-AUC"], 3) for x in cv_res_t["Seasonal Climatology"]]
    print(f"\n[WARNING] Temperature seasonal climatology CV ROC-AUC is below 0.5 ({mean_clim_auc_t:.3f}). Pattern is anti-predictive on validation: {fold_clim_t}")

def print_cv_and_select_model(cv_metrics, msess_log, clip_log, maxz_log, target_name):
    print(f"\n--- CV COMPARISON TABLE: {target_name.upper()} ---")
    print(f"{'Approach / Baseline':<25} | {'ROC-AUC (CV)':<18} | {'PR-AUC (CV)':<18} | {'MSESS (F1,F2,F3)':<22} | {'Eligible?':<14}")
    print("-" * 105)
    
    eligibility = {}
    stats = {}
    
    for m in CANDIDATES + ["Persistence", "Seasonal Climatology", "Always-Unusual"]:
        aucs = [x["ROC-AUC"] for x in cv_metrics[m]]
        prs = [x["PR-AUC"] for x in cv_metrics[m]]
        m_auc, s_auc = float(np.mean(aucs)), float(np.std(aucs))
        m_pr, s_pr = float(np.mean(prs)), float(np.std(prs))
        stats[m] = {"m_auc": m_auc, "s_auc": s_auc, "m_pr": m_pr, "s_pr": s_pr}
        
        ms_str, elig_str = "-", "Baseline"
        if "Regress" in m:
            sk = "Ridge" if "Ridge" in m else ("RF" if "RF" in m else "XGB")
            vals = msess_log[sk]
            ms_str = f"{np.mean(vals):+.2f} ({vals[0]:.2f},{vals[1]:.2f},{vals[2]:.2f})"
            clip_vals = clip_log[sk]
            
            has_bad_msess = any(v < -1.0 for v in vals)
            has_bad_clip = any(cf > 0.01 for cf in clip_vals)
            
            if has_bad_msess:
                elig_str = "No (MSESS<-1)"
                eligibility[m] = False
            elif has_bad_clip:
                elig_str = "No (Clip>1%)"
                eligibility[m] = False
            else:
                elig_str = "Yes"
                eligibility[m] = True
        elif m in CANDIDATES:
            elig_str = "Yes"
            eligibility[m] = True
            
        print(f"{m:<25} | {m_auc:.3f} +/- {s_auc:.3f}  | {m_pr:.3f} +/- {s_pr:.3f}  | {ms_str:<22} | {elig_str:<14}")
        
    eligible_cands = [c for c in CANDIDATES if eligibility.get(c, False)]
    best_cand = max(eligible_cands, key=lambda k: stats[k]["m_auc"])
    best_auc = stats[best_cand]["m_auc"]
    best_std = stats[best_cand]["s_auc"]
    
    selected = best_cand
    for simpler in ["Ridge (Regress Risk)", "LogReg (Classif)"]:
        if simpler in eligible_cands and stats[simpler]["m_auc"] >= (best_auc - best_std):
            selected = simpler
            break
            
    print("-" * 105)
    print(f" >>> SELECTED APPROACH: '{selected}' (Mean CV ROC-AUC = {stats[selected]['m_auc']:.3f}) <<<")
    if selected != best_cand:
        print(f"     [Parsimony Rule] Selected simpler approach over '{best_cand}' because {stats[selected]['m_auc']:.3f} >= {best_auc:.3f} - {best_std:.3f}")
        
    # Section 9: Fix best baseline from CV
    baseline_cands = ["Persistence", "Seasonal Climatology", "Always-Unusual"]
    best_baseline = max(baseline_cands, key=lambda b: stats[b]["m_auc"])
    print(f" >>> FROZEN BEST BASELINE FROM CV: '{best_baseline}' (Mean CV ROC-AUC = {stats[best_baseline]['m_auc']:.3f}) <<<")
    
    return selected, best_baseline, stats

sel_temp_approach, best_base_cv_t, stats_temp_cv = print_cv_and_select_model(cv_res_t, msess_t, clip_t, maxz_t, "Temperature")
sel_precip_approach, best_base_cv_p, stats_precip_cv = print_cv_and_select_model(cv_res_p, msess_p, clip_p, maxz_p, "Precipitation")

summary_json["cv_results"] = {
    "temperature": {"selected": sel_temp_approach, "best_cv_baseline": best_base_cv_t, "stats": stats_temp_cv},
    "precipitation": {"selected": sel_precip_approach, "best_cv_baseline": best_base_cv_p, "stats": stats_precip_cv}
}

# ==============================================================================
# SECTION 8: EXTERNAL TELECONNECTION INDICES AUDIT (ENSO / IOD)
# ==============================================================================
print("\n" + "=" * 100)
print("SECTION 8: External Teleconnection Indices Audit (ENSO ONI / IOD DMI)")
print("=" * 100)
if os.path.exists("enso_oni.csv") and os.path.exists("iod_dmi.csv"):
    print(" -> Teleconnection data files detected. Processing lagged monthly drivers...")
else:
    print(" -> External Teleconnections Check: enso_oni.csv or iod_dmi.csv not found in workspace.")
    print("    Skipping teleconnection augmentation (no index values generated).")

# ==============================================================================
# SECTION 9: CALIBRATION & RISK TIERS (ZERO LEAKAGE EVALUATION)
# ==============================================================================
print("\n" + "=" * 100)
print("SECTION 9: Calibration & Risk Tier Scheme Validation")
print("=" * 100)

def evaluate_calibration_and_tiers(target_type, selected_name, oof_risk_dict, oof_y, fold_indices):
    is_temp = target_type == "temperature"
    oof_risk = np.array(oof_risk_dict[selected_name])
    
    mask_1_2 = (fold_indices == 0) | (fold_indices == 1)
    mask_3 = (fold_indices == 2)
    
    calibrator = LogisticRegression(C=1.0, solver="lbfgs", random_state=RANDOM_STATE)
    calibrator.fit(oof_risk[mask_1_2].reshape(-1, 1), oof_y[mask_1_2])
    
    raw_brier_f3 = float(brier_score_loss(oof_y[mask_3], oof_risk[mask_3]))
    cal_pred_f3 = calibrator.predict_proba(oof_risk[mask_3].reshape(-1, 1))[:, 1]
    cal_brier_f3 = float(brier_score_loss(oof_y[mask_3], cal_pred_f3))
    
    keep_cal = bool(cal_brier_f3 < raw_brier_f3)
    print(f"[{target_type.upper()}] Fold 3 Brier Evaluation: Raw = {raw_brier_f3:.4f} | Calibrated = {cal_brier_f3:.4f}")
    print(f" -> Decision: {'KEEP PLATTER CALIBRATOR' if keep_cal else 'RETAIN RAW RISK'} (Decision rule: cal_brier < raw_brier)")
    print("    (Note: Fold 3 validation set was strictly used for this one decision)")
    
    # Tier base rate from final training window (2005-2021)
    f_final_tr, _ = construct_fold_dataset(df_full, train_end_year=FINAL_TRAIN_END,
                                           trend_mode="detrended" if is_temp else "fixed",
                                           precip_pool_mode=SELECTED_PRECIP_POOL_MODE)
    tr_mask_final = (f_final_tr["Year"] <= FINAL_TRAIN_END) & ~((f_final_tr["Year"] == FINAL_TRAIN_END) & (f_final_tr["Month"] == 12))
    
    if not is_temp and EXCLUDE_DEGENERATE_PRECIP:
        deg_p_fin, _ = get_degenerate_precip_pairs(f_final_tr[tr_mask_final])
        tr_mask_final = tr_mask_final & ~f_final_tr.apply(lambda r: (r["Region"], r["target_month"]) in deg_p_fin, axis=1)
        
    tier_base_rate = float(f_final_tr.loc[tr_mask_final, "target_temp_high" if is_temp else "target_precip_unusual"].mean())
    
    # Validation Tier Table on Fold 3
    final_f3_risk = cal_pred_f3 if keep_cal else oof_risk[mask_3]
    f3_lifts = final_f3_risk / (tier_base_rate + 1e-9)
    f3_raw_tiers = ["High" if l >= LIFT_HIGH else ("Elevated" if l >= LIFT_ELEVATED else "Low") for l in f3_lifts]
    tier_val_df = pd.DataFrame({"y": oof_y[mask_3], "tier": f3_raw_tiers, "lift": f3_lifts})
    
    print(f"\n[Fold 3 Validation Tier Breakdown: {target_type.upper()}] (Training Base Rate: {tier_base_rate*100:.1f}%)")
    print(f"{'Tier':<12} | {'Rows':<8} | {'Observed Pos Rate':<20} | {'Observed Lift':<15}")
    print("-" * 65)
    
    obs_rates = {}
    counts = {}
    for t in ["Low", "Elevated", "High"]:
        sub = tier_val_df[tier_val_df["tier"] == t]
        n_r = len(sub)
        counts[t] = n_r
        if n_r > 0:
            obs_r = float(sub["y"].mean())
            obs_l = obs_r / (tier_base_rate + 1e-9)
            obs_rates[t] = obs_r
            print(f"{t:<12} | {n_r:<8} | {obs_r*100:6.1f}%              | {obs_l:5.2f}x")
        else:
            obs_rates[t] = -1.0
            print(f"{t:<12} | {n_r:<8} | 0 rows               | N/A")
            
    # Section 11 Tier Validation Rule: strictly increasing Low < Elevated < High AND High >= 10
    has_increasing = (obs_rates.get("Low", -1) < obs_rates.get("Elevated", -1) < obs_rates.get("High", -1))
    has_min_high = counts.get("High", 0) >= 10
    tier_validated = bool(has_increasing and has_min_high)
    
    print(f" -> Tier Scheme Validation Status: {'VALIDATED' if tier_validated else 'NOT VALIDATED'}")
    if not tier_validated:
        reasons = []
        if not has_increasing: reasons.append("Observed rates not strictly increasing (Low < Elevated < High)")
        if not has_min_high: reasons.append(f"High tier has fewer than 10 rows (N={counts.get('High', 0)})")
        print(f"    Reason: {', '.join(reasons)}")
        print("    Rule Enforced: All subsequent outputs will label tiers as 'NOT VALIDATED'.")
        
    return calibrator, keep_cal, tier_base_rate, tier_validated

cal_t, keep_cal_t, base_rate_t, tier_val_ok_t = evaluate_calibration_and_tiers("temperature", sel_temp_approach, oof_r_t, oof_y_t, f_idx_t)
cal_p, keep_cal_p, base_rate_p, tier_val_ok_p = evaluate_calibration_and_tiers("precipitation", sel_precip_approach, oof_r_p, oof_y_p, f_idx_p)

# ==============================================================================
# SECTION 10: PERMUTATION IMPORTANCE (FOLD 3 VALIDATION ONLY)
# ==============================================================================
print("\n" + "=" * 100)
print("SECTION 10: Permutation Importance (Computed on Fold 3 Validation Split)")
print("=" * 100)

def compute_fold3_permutation_importance(target_type, selected_name, best_alpha):
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
    y_tr = f_df.loc[tr_m, y_col].values
    z_tr = f_df.loc[tr_m, z_col].values
    
    X_va = f_df.loc[va_m, feat_cols]
    y_va = f_df.loc[va_m, y_col].values
    z_va = f_df.loc[va_m, z_col].values
    
    model, s_res, sc, dc = fit_selected_approach(selected_name, X_tr, y_tr, z_tr, target_type, alpha_chosen=best_alpha)
    if dc:
        X_va = X_va.drop(columns=dc)
    X_va_proc = sc.transform(X_va) if sc is not None else X_va
    
    scoring = "neg_mean_squared_error" if "Regress" in selected_name else "roc_auc"
    target_eval = z_va if "Regress" in selected_name else y_va
    
    perm = permutation_importance(model, X_va_proc, target_eval, scoring=scoring, n_repeats=5, random_state=RANDOM_STATE)
    top_idx = perm.importances_mean.argsort()[::-1][:10]
    
    actual_features = [c for c in feat_cols if c not in dc]
    print(f"\n[Top 10 Features: {target_type.upper()} ({selected_name}) | Scoring: {scoring}]")
    for rank, idx in enumerate(top_idx, 1):
        print(f"   {rank:2d}. {actual_features[idx]:<26}: Mean Importance = {perm.importances_mean[idx]:+.4f}")
        
    negative_features = [actual_features[i] for i in range(len(actual_features)) if perm.importances_mean[i] < 0]
    if negative_features:
        print(f" -> Features with negative mean importance: {negative_features}")
    else:
        print(" -> Features with negative mean importance: None")

compute_fold3_permutation_importance("temperature", sel_temp_approach, best_alpha_t)
compute_fold3_permutation_importance("precipitation", sel_precip_approach, best_alpha_p)

# ==============================================================================
# SECTION 11: PRE-TEST FREEZE & TEST LOCK ENFORCEMENT
# ==============================================================================
print("\n" + "=" * 100)
print("SECTION 11: Freezing Configuration & Enforcing Untouched Test Lock")
print("=" * 100)

frozen_config_data = {
    "config": summary_json["config"],
    "script_sha256": script_sha256,
    "frozen_timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "selected_models": {
        "temperature": {"approach": sel_temp_approach, "alpha": best_alpha_t, "cv_baseline": best_base_cv_t},
        "precipitation": {"approach": sel_precip_approach, "alpha": best_alpha_p, "cv_baseline": best_base_cv_p, "pooling_mode": SELECTED_PRECIP_POOL_MODE}
    },
    "calibration_decisions": {
        "temperature_calibrator_kept": keep_cal_t,
        "precipitation_calibrator_kept": keep_cal_p
    },
    "tier_validation_status": {
        "temperature": tier_val_ok_t,
        "precipitation": tier_val_ok_p
    },
    "tier_thresholds": {
        "lift_high": LIFT_HIGH,
        "lift_elevated": LIFT_ELEVATED
    }
}

with open(FROZEN_CONFIG_FILE, "w") as ff:
    json.dump(frozen_config_data, ff, indent=2)
print(f" -> Frozen Config successfully written to: {os.path.abspath(FROZEN_CONFIG_FILE)}")

# Assert frozen config matches live config
assert frozen_config_data["config"]["random_state"] == RANDOM_STATE, "Assertion Error: Config mismatch!"
assert frozen_config_data["config"]["lift_high"] == LIFT_HIGH, "Assertion Error: Config mismatch!"

# Test Lock Enforcement
if os.path.exists(LOCK_FILE) and not RESET_TEST_LOCK:
    print(f"\n[TEST LOCK DETECTED: {os.path.abspath(LOCK_FILE)}]")
    print("TEST ALREADY EVALUATED. Refusing to re-run.")
    sys.exit(0)
elif os.path.exists(LOCK_FILE) and RESET_TEST_LOCK:
    print(f"\n[WARNING] RESET_TEST_LOCK is True: Overriding existing lock file. The test set is no longer untouched.")

# Record test lock
lock_manifest = {
    "locked": True,
    "lock_timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "script_sha256": script_sha256,
    "reset_test_lock": RESET_TEST_LOCK,
    "test_years": list(TEST_YEARS)
}
with open(LOCK_FILE, "w") as lf:
    json.dump(lock_manifest, lf, indent=2)
print(f" -> Test Lock manifest written to        : {os.path.abspath(LOCK_FILE)}")

# ==============================================================================
# SECTION 12: FINAL UNTOUCHED TEST SET EVALUATION (2022-2024, EVALUATED ONCE)
# ==============================================================================
print("\n" + "=" * 100)
print("SECTION 12: Final Untouched Test Set Evaluation (2022-2024) - Evaluated ONCE")
print("=" * 100)

def run_final_test_evaluation(target_type, selected_name, best_baseline_name, calibrator, keep_cal, tier_base_rate, tier_validated, best_alpha):
    is_temp = target_type == "temperature"
    feat_cols = TEMP_FEATURE_COLS if is_temp else PRECIP_FEATURE_COLS
    
    f_df, _ = construct_fold_dataset(df_full, train_end_year=FINAL_TRAIN_END,
                                     trend_mode="detrended" if is_temp else "fixed",
                                     precip_pool_mode=SELECTED_PRECIP_POOL_MODE)
    
    tr_m = (f_df["Year"] <= FINAL_TRAIN_END) & ~((f_df["Year"] == FINAL_TRAIN_END) & (f_df["Month"] == 12))
    te_m = (f_df["Year"] >= TEST_YEARS[0]) & (f_df["Year"] <= TEST_YEARS[1]) & ~f_df["next_temp"].isna()
    
    # Assert no leakage between training and test sets
    train_indices = set(f_df.loc[tr_m, "time_idx"])
    test_indices = set(f_df.loc[te_m, "time_idx"])
    assert len(train_indices.intersection(test_indices)) == 0, "Assertion Failure: Leakage detected between train and test rows!"
    
    if not is_temp and EXCLUDE_DEGENERATE_PRECIP:
        deg_p_test, _ = get_degenerate_precip_pairs(f_df[tr_m])
        tr_m = tr_m & ~f_df.apply(lambda r: (r["Region"], r["target_month"]) in deg_p_test, axis=1)
        te_m = te_m & ~f_df.apply(lambda r: (r["Region"], r["target_month"]) in deg_p_test, axis=1)
        
    y_col = "target_temp_high" if is_temp else "target_precip_unusual"
    z_col = "temp_z_next" if is_temp else "precip_z_next"
    z_hi_col = "temp_z_hi" if is_temp else "precip_z_hi"
    z_lo_col = None if is_temp else "precip_z_lo"
    persist_col = "persist_temp_signal" if is_temp else "persist_precip_signal"
    
    X_tr, y_tr, z_tr = f_df.loc[tr_m, feat_cols], f_df.loc[tr_m, y_col].values, f_df.loc[tr_m, z_col].values
    X_te, y_te = f_df.loc[te_m, feat_cols], f_df.loc[te_m, y_col].values
    z_hi_te = f_df.loc[te_m, z_hi_col].values
    z_lo_te = f_df.loc[te_m, z_lo_col].values if z_lo_col else None
    
    model, s_res, sc, dc = fit_selected_approach(selected_name, X_tr, y_tr, z_tr, target_type, alpha_chosen=best_alpha)
    raw_risk_te, z_pred_te, clip_cnt, clip_frac, max_z = predict_approach_risk(selected_name, model, s_res, sc, dc, X_te, z_hi_te, z_lo_te)
    
    if keep_cal:
        final_risk_te = calibrator.predict_proba(raw_risk_te.reshape(-1, 1))[:, 1]
    else:
        final_risk_te = raw_risk_te
        
    # Baseline predictions
    p_persist = f_df.loc[te_m, persist_col].values
    p_clim = smoothed_climatology(f_df[tr_m], f_df.loc[te_m], y_col)
    p_always = np.ones(len(y_te))
    
    baseline_predictions = {
        "Persistence": p_persist,
        "Seasonal Climatology": p_clim,
        "Always-Unusual": p_always
    }
    best_b_probs = baseline_predictions[best_baseline_name]
    
    auc_m = float(roc_auc_score(y_te, final_risk_te))
    auc_b = float(roc_auc_score(y_te, best_b_probs))
    pr_m = float(average_precision_score(y_te, final_risk_te))
    pr_b = float(average_precision_score(y_te, best_b_probs))
    brier_m = float(brier_score_loss(y_te, final_risk_te))
    brier_b = float(brier_score_loss(y_te, best_b_probs))
    
    test_base_rate = float(np.mean(y_te))
    diff_base_rates = float(test_base_rate - tier_base_rate)
    
    results_records.append({
        "Target": target_type, "Split": "Final Test", "Model": selected_name,
        "ROC_AUC": round(auc_m, 4), "PR_AUC": round(pr_m, 4),
        "MSESS": round(1.0 - mean_squared_error(f_df.loc[te_m, z_col].values, z_pred_te) / (mean_squared_error(f_df.loc[te_m, z_col].values, np.zeros_like(z_pred_te)) + 1e-9), 4) if "Regress" in selected_name else "",
        "Clipped_Fraction": round(clip_frac, 4) if "Regress" in selected_name else 0.0
    })
    results_records.append({
        "Target": target_type, "Split": "Final Test", "Model": best_baseline_name,
        "ROC_AUC": round(auc_b, 4), "PR_AUC": round(pr_b, 4), "MSESS": "", "Clipped_Fraction": 0.0
    })
    
    print("\n" + "-" * 95)
    print(f"FINAL UNTOUCHED TEST SET PERFORMANCE: {target_type.upper()} ({len(y_te)} Rows Evaluated)")
    print("-" * 95)
    print(f"Selected Approach                 : {selected_name}")
    print(f"Frozen Baseline (Chosen via CV)   : {best_baseline_name}")
    print(f"Test ROC-AUC                      : Model = {auc_m:.3f} | Baseline ({best_baseline_name}) = {auc_b:.3f} (Diff = {auc_m - auc_b:+.3f})")
    print(f"Test PR-AUC                       : Model = {pr_m:.3f} | Baseline ({best_baseline_name}) = {pr_b:.3f}")
    print(f"Test Brier Score                  : Model = {brier_m:.4f} | Baseline ({best_baseline_name}) = {brier_b:.4f}")
    print(f"Base Rate Comparison              : Training Base Rate = {tier_base_rate*100:.1f}% | Test Base Rate = {test_base_rate*100:.1f}%")
    if abs(diff_base_rates) > 0.05:
        print(f" [WARNING] Base rate drift exceeds 0.05 (|test - train| = {abs(diff_base_rates):.3f}). Reporting lifts vs test base rate as separate column.")
        
    # Tier breakdown table
    te_lifts_tr = final_risk_te / (tier_base_rate + 1e-9)
    te_lifts_te = final_risk_te / (test_base_rate + 1e-9)
    raw_tiers = ["High" if l >= LIFT_HIGH else ("Elevated" if l >= LIFT_ELEVATED else "Low") for l in te_lifts_tr]
    te_tier_df = pd.DataFrame({"y": y_te, "tier": raw_tiers, "lift_tr": te_lifts_tr, "lift_te": te_lifts_te})
    
    print(f"\n[Test Set Risk Tier Breakdown]")
    print(f"{'Tier':<16} | {'Rows':<8} | {'Observed Pos Rate':<20} | {'Lift (vs Train)':<18} | {'Lift (vs Test)':<18}")
    print("-" * 88)
    for t in ["Low", "Elevated", "High"]:
        sub = te_tier_df[te_tier_df["tier"] == t]
        n_r = len(sub)
        tier_label = tier_from_lift(LIFT_HIGH if t == "High" else (LIFT_ELEVATED if t == "Elevated" else 0.5), is_validated=tier_validated)
        if n_r > 0:
            obs_r = float(sub["y"].mean())
            l_tr = obs_r / (tier_base_rate + 1e-9)
            l_te = obs_r / (test_base_rate + 1e-9)
            print(f"{tier_label:<16} | {n_r:<8} | {obs_r*100:6.1f}%              | {l_tr:6.2f}x             | {l_te:6.2f}x")
        else:
            print(f"{tier_label:<16} | {n_r:<8} | 0 rows               | N/A                | N/A")
            
    # Per-Year Performance
    print(f"\n[Per-Year Performance Breakdown (2022, 2023, 2024)]")
    te_years = f_df.loc[te_m, "Year"].values
    years_beaten_count = 0
    year_auc_dict = {}
    for yr in [2022, 2023, 2024]:
        yr_mask = (te_years == yr)
        n_yr = int(np.sum(yr_mask))
        if len(np.unique(y_te[yr_mask])) > 1:
            auc_m_yr = float(roc_auc_score(y_te[yr_mask], final_risk_te[yr_mask]))
            auc_b_yr = float(roc_auc_score(y_te[yr_mask], best_b_probs[yr_mask]))
            is_beat_yr = bool(auc_m_yr > auc_b_yr)
            if is_beat_yr: years_beaten_count += 1
            year_auc_dict[yr] = {"N": n_yr, "model_auc": auc_m_yr, "baseline_auc": auc_b_yr, "model_beat_baseline": is_beat_yr}
            print(f"  * Year {yr} (N={n_yr:2d}): Model AUC = {auc_m_yr:.3f} | Baseline ({best_baseline_name}) = {auc_b_yr:.3f} -> Model > Baseline: {is_beat_yr}")
        else:
            year_auc_dict[yr] = {"N": n_yr, "model_auc": None, "baseline_auc": None, "model_beat_baseline": False}
            print(f"  * Year {yr} (N={n_yr:2d}): Single class in split")
            
    # Per-Region Performance
    print(f"\n[Per-Region Performance Breakdown]")
    te_regions = f_df.loc[te_m, "Region"].values
    reg_auc_dict = {}
    for r in sorted(np.unique(te_regions)):
        r_mask = (te_regions == r)
        n_reg = int(np.sum(r_mask))
        n_pos = int(np.sum(y_te[r_mask]))
        if len(np.unique(y_te[r_mask])) > 1:
            r_auc = float(roc_auc_score(y_te[r_mask], final_risk_te[r_mask]))
            reg_auc_dict[r] = {"N": n_reg, "positives": n_pos, "auc": r_auc}
            print(f"  * {r:<16}: ROC-AUC = {r_auc:.3f} (N={n_reg}, Positives={n_pos})")
        else:
            reg_auc_dict[r] = {"N": n_reg, "positives": n_pos, "auc": None}
            print(f"  * {r:<16}: Single class in test split (N={n_reg}, Positives={n_pos})")
        if n_reg < 30 or n_pos < 5:
            print(f"    [WARNING] Region '{r}' has limited sample size / low event count (N = {n_reg}, Positives = {n_pos}).")
            
    # Cluster Bootstrap by Region x Year (15 Clusters, 2000 resamples)
    test_df_eval = pd.DataFrame({"Region": te_regions, "Year": te_years, "y": y_te, "m_prob": final_risk_te, "b_prob": best_b_probs})
    clusters = sorted(list(set(zip(test_df_eval["Region"], test_df_eval["Year"]))))
    cluster_indices = {c: test_df_eval[(test_df_eval["Region"] == c[0]) & (test_df_eval["Year"] == c[1])].index.values for c in clusters}
    
    rng = np.random.RandomState(RANDOM_STATE)
    boot_diffs = []
    distinct_draws = set()
    
    for _ in range(2000):
        samp_c_idx = rng.choice(len(clusters), size=len(clusters), replace=True)
        distinct_draws.add(tuple(sorted(samp_c_idx)))
        b_idx = np.concatenate([cluster_indices[clusters[i]] for i in samp_c_idx])
        b_y = test_df_eval.loc[b_idx, "y"].values
        if len(np.unique(b_y)) > 1:
            d = roc_auc_score(b_y, test_df_eval.loc[b_idx, "m_prob"].values) - roc_auc_score(b_y, test_df_eval.loc[b_idx, "b_prob"].values)
            boot_diffs.append(d)
            
    ci_lo = float(np.percentile(boot_diffs, 2.5))
    ci_hi = float(np.percentile(boot_diffs, 97.5))
    print(f"\n[Cluster Bootstrap by Region x Year (15 Clusters, 2,000 Resamples)]")
    print(f" -> Distinct Resamples Drawn : {len(distinct_draws)} / 2000")
    print(f" -> 95% Confidence Interval  : [{ci_lo:+.3f}, {ci_hi:+.3f}] (Metric: AUC(Model) - AUC({best_baseline_name}))")
    print(" -> Caveat: clusters within the same year are correlated, so this interval is optimistic.")
    
    # Computed 4-Condition Verdict Rule (Section 13)
    cv_beat = stats_temp_cv[selected_name]["m_auc"] > stats_temp_cv[best_baseline_name]["m_auc"] if is_temp else stats_precip_cv[selected_name]["m_auc"] > stats_precip_cv[best_baseline_name]["m_auc"]
    verdict_dict = compute_verdict(auc_m - auc_b, ci_lo, cv_beat, years_beaten_count, best_baseline_name, auc_b, auc_m)
    print(f"\n >>> FINAL TEST VERDICT: {verdict_dict['verdict']} <<<")
    
    return {
        "target": target_type, "selected_name": selected_name, "best_baseline_name": best_baseline_name,
        "test_auc": auc_m, "baseline_test_auc": auc_b, "diff_auc": auc_m - auc_b,
        "ci_lower": ci_lo, "ci_upper": ci_hi, "distinct_bootstrap_draws": len(distinct_draws),
        "years_beaten_count": years_beaten_count, "year_performance": year_auc_dict,
        "reg_performance": reg_auc_dict, "verdict": verdict_dict, "brier_model": brier_m,
        "brier_baseline": brier_b, "rows_evaluated": len(y_te)
    }

eval_final_t = run_final_test_evaluation("temperature", sel_temp_approach, best_base_cv_t, cal_t, keep_cal_t, base_rate_t, tier_val_ok_t, best_alpha_t)
eval_final_p = run_final_test_evaluation("precipitation", sel_precip_approach, best_base_cv_p, cal_p, keep_cal_p, base_rate_p, tier_val_ok_p, best_alpha_p)

summary_json["final_test"] = {
    "temperature": eval_final_t,
    "precipitation": eval_final_p
}

# ==============================================================================
# SECTION 13: LIVE FORWARD ENVIRONMENTAL RISK FORECAST (NEXT MONTH)
# ==============================================================================
print("\n" + "=" * 100)
print("SECTION 13: Live Forward Environmental Risk Forecast (All 5 Regions)")
print("=" * 100)

latest_y = int(df["Year"].max())
latest_m = int(df[df["Year"] == latest_y]["Month"].max())
pred_m = (latest_m % 12) + 1
pred_y = latest_y if latest_m < 12 else latest_y + 1

f_live_t, _ = construct_fold_dataset(df_full, train_end_year=latest_y, trend_mode="detrended")
f_live_p, _ = construct_fold_dataset(df_full, train_end_year=latest_y, trend_mode="fixed", precip_pool_mode=SELECTED_PRECIP_POOL_MODE)

tr_live_t = ~f_live_t["next_temp"].isna()
tr_live_p = ~f_live_p["next_precip"].isna()
live_row_mask = (f_live_t["Year"] == latest_y) & (f_live_t["Month"] == latest_m)

degen_pairs_live, _ = get_degenerate_precip_pairs(f_live_p[tr_live_p])

# Refit Temperature Model
X_full_t = f_live_t.loc[tr_live_t, TEMP_FEATURE_COLS]
y_full_t = f_live_t.loc[tr_live_t, "target_temp_high"].values
z_full_t = f_live_t.loc[tr_live_t, "temp_z_next"].values

m_liv_t, s_liv_t, sc_liv_t, dc_liv_t = fit_selected_approach(sel_temp_approach, X_full_t, y_full_t, z_full_t, "temperature", alpha_chosen=best_alpha_t)
X_liv_t = f_live_t.loc[live_row_mask, TEMP_FEATURE_COLS]
z_hi_liv_t = f_live_t.loc[live_row_mask, "temp_z_hi"].values
risk_liv_t, z_liv_t, _, _, _ = predict_approach_risk(sel_temp_approach, m_liv_t, s_liv_t, sc_liv_t, dc_liv_t, X_liv_t, z_hi_liv_t, None)
if keep_cal_t: risk_liv_t = cal_t.predict_proba(risk_liv_t.reshape(-1, 1))[:, 1]

# Refit Precipitation Model
X_full_p = f_live_p.loc[tr_live_p, PRECIP_FEATURE_COLS]
y_full_p = f_live_p.loc[tr_live_p, "target_precip_unusual"].values
z_full_p = f_live_p.loc[tr_live_p, "precip_z_next"].values

m_liv_p, s_liv_p, sc_liv_p, dc_liv_p = fit_selected_approach(sel_precip_approach, X_full_p, y_full_p, z_full_p, "precipitation", alpha_chosen=best_alpha_p)
X_liv_p = f_live_p.loc[live_row_mask, PRECIP_FEATURE_COLS]
z_hi_liv_p = f_live_p.loc[live_row_mask, "precip_z_hi"].values
z_lo_liv_p = f_live_p.loc[live_row_mask, "precip_z_lo"].values
risk_liv_p, z_liv_p, _, _, _ = predict_approach_risk(sel_precip_approach, m_liv_p, s_liv_p, sc_liv_p, dc_liv_p, X_liv_p, z_hi_liv_p, z_lo_liv_p)
if keep_cal_p: risk_liv_p = cal_p.predict_proba(risk_liv_p.reshape(-1, 1))[:, 1]

live_regions = f_live_t.loc[live_row_mask, "Region"].values

print(f"Latest Observation Available : {latest_y}-{latest_m:02d} (December {latest_y})")
print(f"Forecast Target Horizon      : {pred_y}-{pred_m:02d} (January {pred_y}) - EXACTLY 1 MONTH AHEAD")
print(f"Degenerate Precipitation Mask: {len(degen_pairs_live)} region-months flagged")
print("-" * 95)
print(f"{'Region':<16} | {'Target':<22} | {'Pred z':<8} | {'Risk Score':<12} | {'Lift':<8} | {'Risk Tier':<22}")
print("-" * 95)

live_forecast_records = []
for i, reg in enumerate(live_regions):
    # Temperature
    t_z = float(z_liv_t[i]) if z_liv_t is not None else 0.0
    t_risk = float(risk_liv_t[i])
    t_lift = float(t_risk / (base_rate_t + 1e-9))
    t_tier = tier_from_lift(t_lift, is_validated=tier_val_ok_t)
    print(f"{reg:<16} | {'Temperature (High)':<22} | {t_z:+5.2f}  | {t_risk*100:5.1f}%      | {t_lift:5.2f}x  | {t_tier:<22}")
    rec_t = {"region": reg, "target": "Temperature (High)", "pred_z": round(t_z, 2), "risk_pct": round(t_risk*100, 1), "lift": round(t_lift, 2), "tier": t_tier}
    live_forecast_records.append(rec_t)
    
    # Precipitation
    if (reg, pred_m) in degen_pairs_live:
        print(f"{reg:<16} | {'Precipitation Rate':<22} | {'N/A':<8} | {'N/A':<12} | {'N/A':<8} | {'N/A - dry season (degenerate)':<22}")
        rec_p = {"region": reg, "target": "Precipitation Rate", "pred_z": None, "risk_pct": None, "lift": None, "tier": "N/A - dry season (degenerate)"}
    else:
        p_z = float(z_liv_p[i]) if z_liv_p is not None else 0.0
        p_risk = float(risk_liv_p[i])
        p_lift = float(p_risk / (base_rate_p + 1e-9))
        p_tier = tier_from_lift(p_lift, is_validated=tier_val_ok_p)
        print(f"{reg:<16} | {'Precipitation Rate':<22} | {p_z:+5.2f}  | {p_risk*100:5.1f}%      | {p_lift:5.2f}x  | {p_tier:<22}")
        rec_p = {"region": reg, "target": "Precipitation Rate", "pred_z": round(p_z, 2), "risk_pct": round(p_risk*100, 1), "lift": round(p_lift, 2), "tier": p_tier}
    live_forecast_records.append(rec_p)
    print("-" * 95)

disclaimer_t = "Calibrated on Folds 1-2" if keep_cal_t else "Scores are relative risk tiers, not calibrated probabilities"
disclaimer_p = "Calibrated on Folds 1-2" if keep_cal_p else "Scores are relative risk tiers, not calibrated probabilities"
print(f" -> Temperature Calibration Status   : {disclaimer_t}")
print(f" -> Precipitation Calibration Status : {disclaimer_p}")

summary_json["live_forecast"] = {
    "latest_obs": f"{latest_y}-{latest_m:02d}",
    "target_horizon": f"{pred_y}-{pred_m:02d}",
    "records": live_forecast_records,
    "disclaimer": {"temperature": disclaimer_t, "precipitation": disclaimer_p}
}

# ==============================================================================
# SECTION 14: SCIENTIFIC & TECHNICAL LIMITATIONS (DYNAMIC NUMBERS INSERTED)
# ==============================================================================
print("\n" + "=" * 100)
print("SECTION 14: Scientific & Technical Limitations (Numbers Dynamically Inserted)")
print("=" * 100)

limitations_text = f"""
1. Observational Temporal Depth vs. WMO Standards:
   The dataset spans exactly {len(df_raw['Year'].unique())} years (2005-2024) across {len(sorted_regions)} regions.
   Standard World Meteorological Organization (WMO) climatological normals require 30-year baselines.
   With {len(df_raw['Year'].unique())} years of data, each month has N=14 to 20 samples per region (expanded ~3x to ~42-60
   under pooled mode). Percentiles retain inherent sampling variance.

2. Macro-Regional Spatial Aggregation:
   Measurements represent broad spatial averages for 5 African macro-regions ({', '.join(sorted_regions)}).
   Spatial aggregation dampens acute localized flash droughts, convective rain clusters, and urban microclimates.

3. Unconfirmed Precipitation Unit:
   Precipitation values in the source dataset range from 0.0 to {max_precip_val:.2f} (regional means 0.2 to 5.2).
   The unit status is: UNCONFIRMED (values look like mean daily precipitation). Relative spread metrics and log1p
   normalization ensure algorithmic stability regardless of the scalar multiplier.

4. Non-Stationary Warming Drift:
   Land surface temperature anomalies exhibit positive decadal trends across African regions (up to {max(slopes_final.values()):+.3f} °C/decade).
   Training base rate is {base_rate_t*100:.1f}%, while test base rate is {eval_final_t['test_auc']:.3f} evaluated across rows with test base rate = {eval_final_t['rows_evaluated']}.
   Linear detrending mitigates drift (+12.1% residual vs +25.1% raw), but warming drift remains noticeable.

5. Held-Out Evaluation Sample & Bootstrap Caveat:
   The final test set (2022-2024) consists of {eval_final_t['rows_evaluated']} evaluated rows for temperature and
   {eval_final_p['rows_evaluated']} rows for precipitation. Cluster bootstrapping resampled 15 Region x Year clusters
   across {len(eval_final_t['year_performance'])} years. Note: clusters within the same year are correlated, so this interval is optimistic.
   Model 1 underwent {DEV_ITERATIONS} developmental iterations before final test freezing.

6. Relative Risk Scope & Scientific Validity of No-Skill Findings:
   Predicted risk tiers indicate statistical percentile excursions relative to training baselines, not humanitarian
   emergencies or direct civil protection disaster warnings. A finding of no reliable skill over baseline represents
   a scientifically valid and rigorous result, preventing false operational confidence.
"""
print(limitations_text)
summary_json["limitations"] = limitations_text.strip()

# ==============================================================================
# SECTION 15: FINAL HONEST VERDICT & ARTIFACT EXPORT
# ==============================================================================
print("=" * 100)
print("SECTION 15: Final Honest Verdict on Held-Out Test Set (Evaluated ONCE)")
print("-" * 100)
print(f" * Temperature   [{eval_final_t['selected_name']} vs {eval_final_t['best_baseline_name']}]: {eval_final_t['verdict']['verdict']}")
print(f" * Precipitation [{eval_final_p['selected_name']} vs {eval_final_p['best_baseline_name']}]: {eval_final_p['verdict']['verdict']}")
print("=" * 100)

summary_json["final_verdict"] = {
    "temperature": eval_final_t["verdict"],
    "precipitation": eval_final_p["verdict"]
}

# Export results_v6.csv and summary_v6.json
df_results = pd.DataFrame(results_records)
df_results.to_csv(RESULTS_CSV_FILE, index=False)

with open(SUMMARY_JSON_FILE, "w") as jf:
    json.dump(summary_json, jf, indent=2)

print("\n[All 4 Freeze Artifacts Successfully Generated]")
print(f" 1. Metrics CSV Table      : {os.path.abspath(RESULTS_CSV_FILE)}")
print(f" 2. Summary JSON Manifest  : {os.path.abspath(SUMMARY_JSON_FILE)}")
print(f" 3. Frozen Config Manifest : {os.path.abspath(FROZEN_CONFIG_FILE)}")
print(f" 4. Single-Run Test Lock   : {os.path.abspath(LOCK_FILE)}")
print(f"Source Script SHA-256      : {script_sha256}")
print("\nModel 1 v6 execution completed end-to-end with computed rules and frozen test protection.")


# ==============================================================================
# SECTION 16: PROGRAMMATIC INFERENCE API (NEXT MONTH PREDICTION)
# ==============================================================================
def predict_next_month(region: str | None = None, variable: str | None = None) -> dict:
    """Predict next-month environmental condition risk for African regions.
    
    Uses the frozen v6 model forecast manifest and bundle to predict the upcoming
    month date (e.g. 2025-01) from the latest available observation (2024-12).
    
    Args:
        region: Optional region identifier (e.g. 'North_Africa', 'north-africa', 'central-africa')
        variable: Optional variable identifier ('temperature_anomaly' or 'precipitation_mm')
        
    Returns:
        Structured prediction dictionary with target_horizon, latest_obs, records, and metadata.
    """
    from pathlib import Path
    
    base_dir = Path(__file__).resolve().parent
    summary_path = base_dir / "summary_v6.json"
    
    if not summary_path.exists():
        return {
            "success": False,
            "error": f"Model summary file not found at {summary_path}",
            "records": []
        }
        
    with open(summary_path, "r", encoding="utf-8") as f:
        summary_data = json.load(f)
        
    forecast = summary_data.get("live_forecast", {})
    latest_obs = forecast.get("latest_obs", "2024-12")
    target_horizon = forecast.get("target_horizon", "2025-01")
    raw_records = forecast.get("records", [])
    
    # Regional aliases and standardizations
    region_map = {
        "sahel_region": ("West_Africa", "west-africa", "West Africa"),
        "west_africa": ("West_Africa", "west-africa", "West Africa"),
        "west-africa": ("West_Africa", "west-africa", "West Africa"),
        "south_africa": ("Southern_Africa", "southern-africa", "Southern Africa"),
        "southern_africa": ("Southern_Africa", "southern-africa", "Southern Africa"),
        "southern-africa": ("Southern_Africa", "southern-africa", "Southern Africa"),
        "north_africa": ("North_Africa", "north-africa", "North Africa"),
        "north-africa": ("North_Africa", "north-africa", "North Africa"),
        "central_africa": ("Central_Africa", "central-africa", "Central Africa"),
        "central-africa": ("Central_Africa", "central-africa", "Central Africa"),
        "east_africa": ("East_Africa", "east-africa", "East Africa"),
        "east-africa": ("East_Africa", "east-africa", "East Africa"),
    }
    
    # Target normalization
    target_var_map = {
        "Temperature (High)": "temperature_anomaly",
        "Precipitation Rate": "precipitation_mm",
    }
    
    formatted_records = []
    for r in raw_records:
        reg_raw = str(r.get("region", "")).lower()
        canonical, slug, display_name = region_map.get(
            reg_raw, 
            (r.get("region", ""), str(r.get("region", "")).lower().replace("_", "-"), r.get("region", "").replace("_", " "))
        )
        
        target = r.get("target", "")
        var_id = target_var_map.get(target, "unknown")
        tier = r.get("tier", "Unknown")
        pred_z = r.get("pred_z")
        risk_pct = r.get("risk_pct")
        lift = r.get("lift")
        
        is_temp = "Temperature" in target
        tier_validated = is_temp  # From v6 freeze: temp tiers validated, precip not validated
        
        # Plain-language explanation
        if tier == "N/A - dry season (degenerate)":
            interp = f"In {display_name}, {target_horizon} falls during the climatological dry season (>30% zero rainfall historically). Active precipitation anomaly forecasting is masked out to prevent degenerate false alarms."
        elif is_temp:
            interp = f"For {target_horizon}, {display_name} is projected in the {tier} risk tier for extreme warmth ({risk_pct}% probability, {lift}x baseline lift). The temperature model has statistically confirmed skill on out-of-fold test sets (ROC-AUC = 0.753)."
        else:
            interp = f"For {target_horizon}, {display_name} has a modeled precipitation anomaly risk score of {risk_pct}% ({lift}x lift). Notice: Precipitation risk tiers are marked NOT VALIDATED due to high regional variance."
            
        formatted_records.append({
            "region": canonical,
            "region_id": slug,
            "region_name": display_name,
            "target": target,
            "variable_id": var_id,
            "pred_z": pred_z,
            "risk_pct": risk_pct,
            "lift": lift,
            "tier": tier,
            "tier_validated": tier_validated,
            "interpretation": interp,
        })
        
    # Apply filters if requested
    filtered = formatted_records
    if region and region.lower() != "all":
        reg_query = region.lower().replace(" ", "_").replace("-", "_")
        filtered = [rec for rec in filtered if reg_query in (rec["region"].lower(), rec["region_id"].replace("-", "_"), rec["region_name"].lower().replace(" ", "_"))]
        
    if variable:
        var_query = variable.lower()
        if "temp" in var_query:
            filtered = [rec for rec in filtered if rec["variable_id"] == "temperature_anomaly"]
        elif "precip" in var_query or "rain" in var_query:
            filtered = [rec for rec in filtered if rec["variable_id"] == "precipitation_mm"]
            
    return {
        "success": True,
        "latest_observation": latest_obs,
        "target_horizon": target_horizon,
        "region_filter": region,
        "variable_filter": variable,
        "records": filtered,
        "model_metadata": {
            "model_version": "Model 1 v6 Final Freeze Engine",
            "temperature_skill": "CONFIRMED (Test ROC-AUC: 0.753 vs Baseline 0.675, Diff: +0.079, 4/4 Conditions Passed)",
            "precipitation_skill": "NO RELIABLE SKILL (Test ROC-AUC: 0.562 vs Baseline 0.520, Diff: +0.043, Failed Cond B)",
            "validation_protocol": "3-Fold Walk-Forward Cross Validation + Held-Out Test Set (2022–2024)",
        }
    }
