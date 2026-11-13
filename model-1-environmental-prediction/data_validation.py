import numpy as np
import pandas as pd

# 1. قراءة الملف الناتج
csv_file = "africa_climate_merged_2004_2024.csv"
df = pd.read_csv(csv_file)

print("=" * 60)
print("             AI DATA HEALTH CHECK REPORT             ")
print("=" * 60)

# فحص 1: هل توجد أي قيم مفقودة (Missing / Null Values)؟
missing_values = df.isnull().sum().sum()
print(f"1. Missing Values (NaNs): {missing_values}")
if missing_values == 0:
    print("   [PASSED] No missing data found! Clean dataset.")
else:
    print("   [WARNING] There are missing values to handle.")

# فحص 2: هل الشهور متصلة كاملة بدون انقطاع؟
expected_months_per_region = 21 * 12  # 252 شهر
counts_per_region = df["Region"].value_counts()
print(f"\n2. Time Continuity Check (Expected: {expected_months_per_region}):")
all_regions_complete = True
for region, count in counts_per_region.items():
    status = "OK" if count == expected_months_per_region else "INCOMPLETE"
    print(f"   - {region}: {count} months -> [{status}]")
    if count != expected_months_per_region:
        all_regions_complete = False

# فحص 3: فحص القيم الشاذة أو أخطاء ناسا (-999)
has_negative_rain = (df["Precipitation_mm"] < 0).any()
print(
    f"\n3. NASA Error Codes Check (-999): {'CLEAN' if not has_negative_rain else 'DETECTED'}"
)

# فحص 4: ملخص الإحصائيات والأرقام (Min, Max, Mean)
print("\n4. Feature Statistical Summary:")
print(
    df[["Temperature_Anomaly", "Precipitation_mm"]]
    .describe()
    .round(2)
    .to_string()
)

print("\n" + "=" * 60)
if missing_values == 0 and all_regions_complete and not has_negative_rain:
    print(" >>> VERDICT: DATA IS 100% CLEAN AND READY FOR AI MODELING! <<<")
print("=" * 60)