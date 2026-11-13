"""
Project: African Environmental Change Analysis
AI Model 1: Next-Month Environmental Condition Prediction
NASA International Space Apps Challenge
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, classification_report
)

# Optional XGBoost import with graceful fallback
try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    from sklearn.ensemble import GradientBoostingClassifier as XGBClassifier
    HAS_XGBOOST = False

# ==============================================================================
# SECTION 1: DATA LOADING & CHRONOLOGICAL INTEGRITY CHECK
# ==============================================================================
print("=" * 80)
print("   AFRICAN ENVIRONMENTAL CHANGE ANALYSIS: AI PREDICTIVE ENGINE (MODEL 1)   ")
print("=" * 80)
print("\n[Step 1/7] Loading and Verifying Feature-Engineered Dataset...")

DATA_PATH = "africa_climate_featured.csv"
df = pd.read_csv(DATA_PATH)

# Enforce strict chronological sort within each region
df = df.sort_values(by=["Region", "Year", "Month"]).reset_index(drop=True)

print(f" -> Loaded {len(df)} records across {df['Region'].nunique()} African regions.")
print(f" -> Time coverage: {df['Year'].min()} to {df['Year'].max()} (Monthly).")

# ==============================================================================
# SECTION 2: ANTI-LEAKAGE TARGET VARIABLE GENERATION
# ==============================================================================
print("\n[Step 2/7] Generating Future Target Variables (1 Month Ahead)...")

# 1-Month Ahead Future Observation (Shift -1 per region to avoid cross-region bleeding)
df["next_month_temp"] = df.groupby("Region")["Temperature_Anomaly"].shift(-1)
df["next_month_precip"] = df.groupby("Region")["Precipitation_mm"].shift(-1)

# Chronological split definitions
TRAIN_END_YEAR = 2018
VAL_START_YEAR, VAL_END_YEAR = 2019, 2021
TEST_START_YEAR, TEST_END_YEAR = 2022, 2024

train_mask = df["Year"] <= TRAIN_END_YEAR
df_train_only = df[train_mask]

# Calculate 10th and 90th percentiles STRICTLY on training split (by Region & Month)
# This prevents Data Leakage from future validation/test distributions
print(" -> Computing region- and month-specific climatological thresholds on Training Data (2005-2018)...")
thresholds = df_train_only.groupby(["Region", "Month"]).agg(
    temp_p10=("Temperature_Anomaly", lambda x: np.percentile(x, 10)),
    temp_p90=("Temperature_Anomaly", lambda x: np.percentile(x, 90)),
    precip_p10=("Precipitation_mm", lambda x: np.percentile(x, 10)),
    precip_p90=("Precipitation_mm", lambda x: np.percentile(x, 90))
).reset_index()

# Merge training thresholds back to the full dataset
df = pd.merge(df, thresholds, on=["Region", "Month"], how="left")

# Define Binary Targets: 1 if Next Month is Unusually High OR Unusually Low, else 0
# Retain detailed direction for later analysis
df["future_temp_unusual"] = np.where(
    (df["next_month_temp"] > df["temp_p90"]) | (df["next_month_temp"] < df["temp_p10"]), 1, 0
)
df["future_precip_unusual"] = np.where(
    (df["next_month_precip"] > df["precip_p90"]) | (df["next_month_precip"] < df["precip_p10"]), 1, 0
)

# Identify the very last observation for each region (e.g. Dec 2024)
# Since next month (Jan 2025) has no ground truth yet, these rows form our Live Forward Inference set!
latest_year = df["Year"].max()
latest_month = df[df["Year"] == latest_year]["Month"].max()
live_inference_mask = (df["Year"] == latest_year) & (df["Month"] == latest_month)
df_live_inference = df[live_inference_mask].copy()

# Filter out rows where next month is NaN (i.e. the live inference row) for model training/evaluation
df_modeling = df[~df["next_month_temp"].isna()].copy()
df_modeling["future_temp_unusual"] = df_modeling["future_temp_unusual"].astype(int)
df_modeling["future_precip_unusual"] = df_modeling["future_precip_unusual"].astype(int)

print(f" -> Labeled {len(df_modeling)} historical samples with ground truth.")
print(f" -> Reserved {len(df_live_inference)} samples for live forward-looking prediction ({latest_year}-{latest_month:02d}).")

# ==============================================================================
# SECTION 3: FEATURE MATRIX PREPARATION & CHRONOLOGICAL PARTITIONING
# ==============================================================================
print("\n[Step 3/7] Preparing Feature Space and Chronological Partitions...")

# Exclude metadata, ground truths, and lookahead targets
EXCLUDE_COLS = [
    "Date", "Region", "Year", "Month",
    "next_month_temp", "next_month_precip",
    "future_temp_unusual", "future_precip_unusual",
    "temp_p10", "temp_p90", "precip_p10", "precip_p90"
]
FEATURE_COLS = [c for c in df_modeling.columns if c not in EXCLUDE_COLS]

# One-hot encode Region (with drop_first to prevent collinearity)
region_dummies = pd.get_dummies(df_modeling["Region"], prefix="Region", drop_first=True, dtype=int)
X_all = pd.concat([df_modeling[FEATURE_COLS], region_dummies], axis=1)

# Encode live inference set identically
region_dummies_live = pd.get_dummies(df_live_inference["Region"], prefix="Region", drop_first=True, dtype=int)
# Ensure columns match exactly
X_live = pd.concat([df_live_inference[FEATURE_COLS], region_dummies_live], axis=1).reindex(columns=X_all.columns, fill_value=0)

# Chronological partition masks
train_idx = df_modeling["Year"] <= TRAIN_END_YEAR
val_idx = (df_modeling["Year"] >= VAL_START_YEAR) & (df_modeling["Year"] <= VAL_END_YEAR)
test_idx = (df_modeling["Year"] >= TEST_START_YEAR) & (df_modeling["Year"] <= TEST_END_YEAR)

X_train, X_val, X_test = X_all[train_idx], X_all[val_idx], X_all[test_idx]

# Targets
y_train_temp, y_val_temp, y_test_temp = (
    df_modeling.loc[train_idx, "future_temp_unusual"],
    df_modeling.loc[val_idx, "future_temp_unusual"],
    df_modeling.loc[test_idx, "future_temp_unusual"],
)

y_train_precip, y_val_precip, y_test_precip = (
    df_modeling.loc[train_idx, "future_precip_unusual"],
    df_modeling.loc[val_idx, "future_precip_unusual"],
    df_modeling.loc[test_idx, "future_precip_unusual"],
)

print(f" -> Feature dimensions : {X_train.shape[1]} features.")
print(f" -> Training set       : {X_train.shape[0]} samples ({df_modeling.loc[train_idx, 'Year'].min()}-{TRAIN_END_YEAR})")
print(f" -> Validation set     : {X_val.shape[0]} samples ({VAL_START_YEAR}-{VAL_END_YEAR})")
print(f" -> Testing set        : {X_test.shape[0]} samples ({TEST_START_YEAR}-{TEST_END_YEAR})")

# Feature Scaling strictly for Logistic Regression (fit on Train only)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)
X_test_scaled = scaler.transform(X_test)
X_live_scaled = scaler.transform(X_live)

# ==============================================================================
# SECTION 4: MODEL TRAINING & VALIDATION COMPARISON
# ==============================================================================
def train_and_evaluate_models(target_name, y_train, y_val, y_test):
    print("\n" + "=" * 70)
    print(f"   EVALUATING MODELS FOR TARGET: {target_name.upper()}   ")
    print("=" * 70)
    
    # Baseline: Majority Class Persistence
    majority_class = y_train.mode()[0]
    base_preds_val = np.full_like(y_val, majority_class)
    base_f1 = f1_score(y_val, base_preds_val, zero_division=0)
    base_rec = recall_score(y_val, base_preds_val, zero_division=0)
    
    print(f"[Baseline - Climatology] Val F1: {base_f1:.3f} | Recall: {base_rec:.3f}")
    
    # Model Definitions
    models = {
        "Logistic Regression": {
            "model": LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42),
            "X_tr": X_train_scaled, "X_v": X_val_scaled, "X_te": X_test_scaled, "X_liv": X_live_scaled
        },
        "Random Forest": {
            "model": RandomForestClassifier(n_estimators=100, max_depth=6, class_weight="balanced", random_state=42),
            "X_tr": X_train, "X_v": X_val, "X_te": X_test, "X_liv": X_live
        },
        "XGBoost": {
            "model": XGBClassifier(
                n_estimators=100, max_depth=4, learning_rate=0.05,
                scale_pos_weight=max(1, (len(y_train) - sum(y_train)) / max(1, sum(y_train))),
                random_state=42
            ),
            "X_tr": X_train, "X_v": X_val, "X_te": X_test, "X_liv": X_live
        }
    }
    
    val_results = {}
    
    for name, m_info in models.items():
        clf = m_info["model"]
        clf.fit(m_info["X_tr"], y_train)
        
        preds_val = clf.predict(m_info["X_v"])
        probs_val = clf.predict_proba(m_info["X_v"])[:, 1] if hasattr(clf, "predict_proba") else preds_val
        
        acc = accuracy_score(y_val, preds_val)
        prec = precision_score(y_val, preds_val, zero_division=0)
        rec = recall_score(y_val, preds_val, zero_division=0)
        f1 = f1_score(y_val, preds_val, zero_division=0)
        try:
            auc = roc_auc_score(y_val, probs_val)
        except:
            auc = 0.5
            
        val_results[name] = {
            "Accuracy": acc, "Precision": prec, "Recall": rec, "F1": f1, "AUC": auc,
            "fitted_model": clf, "X_test": m_info["X_te"], "X_live": m_info["X_liv"]
        }
        print(f" -> {name:20s} | Val Acc: {acc:.3f} | Prec: {prec:.3f} | Recall: {rec:.3f} | F1: {f1:.3f} | AUC: {auc:.3f}")
    
    # Model Selection: Pick best model based on F1-Score (balances precision and recall for rare unusual events)
    best_model_name = max(val_results, key=lambda k: val_results[k]["F1"])
    best_info = val_results[best_model_name]
    print(f"\n >>> Selected Best Model for {target_name}: '{best_model_name}' (Val F1: {best_info['F1']:.3f}) <<<")
    
    # Final Evaluation on the Untouched Test Set (2022-2024)
    best_clf = best_info["fitted_model"]
    test_preds = best_clf.predict(best_info["X_test"])
    test_probs = best_clf.predict_proba(best_info["X_test"])[:, 1]
    
    print("\n" + "-" * 55)
    print(f"   FINAL UNTOUCHED TEST SET PERFORMANCE (2022-2024)   ")
    print("-" * 55)
    print(f"Test Accuracy : {accuracy_score(y_test, test_preds):.3f}")
    print(f"Test Precision: {precision_score(y_test, test_preds, zero_division=0):.3f}")
    print(f"Test Recall   : {recall_score(y_test, test_preds, zero_division=0):.3f}")
    print(f"Test F1-Score : {f1_score(y_test, test_preds, zero_division=0):.3f}")
    print(f"Test ROC-AUC  : {roc_auc_score(y_test, test_probs):.3f}")
    print("\nConfusion Matrix [Normal (0), Unusual (1)]:")
    print(confusion_matrix(y_test, test_preds))
    
    # Generate live forward prediction
    live_preds = best_clf.predict(best_info["X_live"])
    live_probs = best_clf.predict_proba(best_info["X_live"])[:, 1]
    
    return best_model_name, live_probs, live_preds

# Run Model Comparison for Both Targets
best_temp_name, live_temp_probs, live_temp_preds = train_and_evaluate_models(
    "Temperature Unusual Condition", y_train_temp, y_val_temp, y_test_temp
)

best_precip_name, live_precip_probs, live_precip_preds = train_and_evaluate_models(
    "Precipitation Unusual Condition", y_train_precip, y_val_precip, y_test_precip
)

# ==============================================================================
# SECTION 5: STRUCTURED LIVE INFERENCE OUTPUT FOR ALL 5 AFRICAN REGIONS
# ==============================================================================
print("\n" + "=" * 80)
print(f"   LIVE FORWARD-LOOKING ENVIRONMENTAL PREDICTION REPORT   ")
print(f"   Latest Observation: {latest_year}-{latest_month:02d} | Target Horizon: Next Month (1 Month Ahead)")
print("=" * 80)

regions_live = df_live_inference["Region"].values

for i, region in enumerate(regions_live):
    t_prob = live_temp_probs[i] * 100
    t_class = "UNUSUAL CONDITION" if live_temp_preds[i] == 1 else "Normal Condition"
    
    p_prob = live_precip_probs[i] * 100
    p_class = "UNUSUAL CONDITION" if live_precip_preds[i] == 1 else "Normal Condition"
    
    print(f"\nRegion: {region}")
    print(f"  * Temperature Anomaly : {t_prob:5.1f}% Probability -> [{t_class}] (Model: {best_temp_name})")
    print(f"  * Precipitation       : {p_prob:5.1f}% Probability -> [{p_class}] (Model: {best_precip_name})")

# ==============================================================================
# SECTION 6: SCIENTIFIC & TECHNICAL LIMITATIONS (FOR JUDGES & DOCUMENTATION)
# ==============================================================================
print("\n" + "=" * 80)
print("                SCIENTIFIC & TECHNICAL LIMITATIONS                ")
print("=" * 80)
print("""
1. Regional Aggregation: 
   Measurements represent large regional spatial averages (~5 macro-regions across Africa).
   Regional averages can smooth out localized flash droughts, micro-climates, or extreme weather events.

2. Climatological Sample Size:
   Thresholds are established on a 14-year training baseline (2005-2018, N=14 per month per region).
   While sufficient for capturing broad decadal anomalies, standard WMO climatology prefers 30-year baselines.

3. Prediction Objective:
   The model is strictly calibrated to detect statistically unusual environmental anomalies (p10 / p90),
   not direct civil defense disasters or immediate weather forecasts.
""")
print("=" * 80)
print("All tasks executed cleanly. Results ready for submission and UI integration!")
