import numpy as np
import pandas as pd

print(">>> [1/5] Loading Cleaned Climate Dataset...")
df = pd.read_csv("africa_climate_merged_2004_2024.csv")

# التأكد الصارم من الترتيب الزمني والإقليمي قبل أي عملية
df = df.sort_values(
    by=["Region", "Year", "Month"], ascending=[True, True, True]
).reset_index(drop=True)

# ==============================================================================
# 1. Cyclical Time Encoding (Sin / Cos)
# ==============================================================================
print(">>> [2/5] Creating Cyclical Time Features (Sin/Cos)...")
df["month_sin"] = np.sin(2 * np.pi * df["Month"] / 12.0).round(4)
df["month_cos"] = np.cos(2 * np.pi * df["Month"] / 12.0).round(4)

# ==============================================================================
# 2. Lag Features (معزولة بالكامل لكل إقليم - Grouped by Region)
# ==============================================================================
print(">>> [3/5] Engineering Lag Features per Region...")
lag_periods = [1, 3, 6, 12]

for lag in lag_periods:
    # Lags للحرارة
    df[f"temp_lag_{lag}"] = (
        df.groupby("Region")["Temperature_Anomaly"].shift(lag).round(3)
    )
    # Lags للأمطار
    df[f"precip_lag_{lag}"] = (
        df.groupby("Region")["Precipitation_mm"].shift(lag).round(3)
    )

# ==============================================================================
# 3. Rolling Statistics (المتوسطات والانحرافات المتحركة لكل إقليم)
# ==============================================================================
print(">>> [4/5] Computing Rolling Statistics per Region...")
rolling_windows = [3, 6, 12]

for w in rolling_windows:
    # المتوسطات المتحركة للحرارة
    df[f"temp_rolling_mean_{w}"] = (
        df.groupby("Region")["Temperature_Anomaly"]
        .transform(lambda x: x.rolling(window=w).mean())
        .round(3)
    )
    # المتوسطات المتحركة للأمطار
    df[f"precip_rolling_mean_{w}"] = (
        df.groupby("Region")["Precipitation_mm"]
        .transform(lambda x: x.rolling(window=w).mean())
        .round(3)
    )

# انحراف التذبذب قصير المدى (3-Month Variability / Volatility)
df["temp_rolling_std_3"] = (
    df.groupby("Region")["Temperature_Anomaly"]
    .transform(lambda x: x.rolling(window=3).std())
    .round(3)
)
df["precip_rolling_std_3"] = (
    df.groupby("Region")["Precipitation_mm"]
    .transform(lambda x: x.rolling(window=3).std())
    .round(3)
)

# ==============================================================================
# 4. Seasonal Anomalies, YoY Deltas & Z-Scores
# ==============================================================================
print(">>> [5/5] Calculating Seasonal Z-Scores and YoY Changes...")

# 4.1 التغير السنوي المباشر (Year-over-Year Delta: القيمة الحالية - نفس الشهر العام الماضي)
df["temp_yoy_change"] = (df["Temperature_Anomaly"] - df["temp_lag_12"]).round(3)
df["precip_yoy_change"] = (df["Precipitation_mm"] - df["precip_lag_12"]).round(
    3
)


# 4.2 الشذوذ الإحصائي الفصلي (Seasonal Z-Score) لكل شهر داخل كل إقليم
# لحساب درجة غرابة الشهر مقارنة بنفس الشهر تاريخياً
def calculate_seasonal_zscore(group_df, col_name):
    # حساب المتوسط والانحراف المعياري الخاص بهذا الإقليم وهذا الشهر تحديداً
    mean = group_df[col_name].transform("mean")
    std = group_df[col_name].transform("std")
    # لتجنب القسمة على صفر في المناطق الصحراوية عديمة المطر
    std = std.replace(0, 1e-6)
    return ((group_df[col_name] - mean) / std).round(3)


df["temp_seasonal_zscore"] = df.groupby(["Region", "Month"])[
    "Temperature_Anomaly"
].transform(lambda x: (x - x.mean()) / (x.std() if x.std() != 0 else 1e-6))
df["precip_seasonal_zscore"] = df.groupby(["Region", "Month"])[
    "Precipitation_mm"
].transform(lambda x: (x - x.mean()) / (x.std() if x.std() != 0 else 1e-6))

# تقريب النتائج
df["temp_seasonal_zscore"] = df["temp_seasonal_zscore"].round(3)
df["precip_seasonal_zscore"] = df["precip_seasonal_zscore"].round(3)

# ==============================================================================
# 5. تنظيف صفوف البداية (Handling Initial Lag Window)
# ==============================================================================
# نظراً لأن lag_12 يحتاج 12 شهراً تاريخياً، فإن أول سنة (2004) ستحتوي على NaNs طبيعية
# نقوم بحذف سنة 2004 لتصبح البيانات خالية 100% من أي قيمة فارغة من 2005 إلى 2024
df_featured = df.dropna().reset_index(drop=True)

# حفظ الملف النهائي لموديل الـ AI
output_file = "africa_climate_featured.csv"
df_featured.to_csv(output_file, index=False)

# ==============================================================================
# تقرير التحقق النهائي (Verification Summary)
# ==============================================================================
print("\n" + "=" * 65)
print("       FEATURE ENGINEERING COMPLETED SUCCESSFULLY!        ")
print("=" * 65)
print(f"Output File Saved     : {output_file}")
print(
    f"Total Final Rows      : {len(df_featured)} (5 regions x 20 years [2005-2024] x 12 months = 1200 rows)"
)
print(f"Total Columns/Features: {len(df_featured.columns)}")
print(f"Any Null Values?      : {df_featured.isnull().sum().sum()} (Must be 0)")
print("=" * 65)
print("\nList of All Generated Features:")
for i, col in enumerate(df_featured.columns, 1):
    print(f"  {i:2d}. {col}")
print("\nSample Preview (First 3 Rows):")
print(df_featured.head(3).T)