import os
import pandas as pd
import xarray as xr

# ==============================================================================
# 1. إعدادات الأقاليم والملفات (Strict Region-to-File Configuration)
# ==============================================================================
# ربطنا كل إقليم بحدوده الجغرافية وملف الأمطار المقابل له بدقة 100%
REGIONS_CONFIG = {
    "North_Africa": {
        "lat": slice(20.0, 37.0),
        "lon": slice(-15.0, 35.0),
        "rain_file": (
            "POWER_Point_Monthly_20040101_20241231_030d00N_031d20E_LST.csv"
        ),
    },
    "Sahel_Region": {
        "lat": slice(10.0, 18.0),
        "lon": slice(-15.0, 35.0),
        "rain_file": (
            "POWER_Point_Monthly_20040101_20241231_014d00N_014d00E_LST.csv"
        ),
    },
    "East_Africa": {
        "lat": slice(-5.0, 15.0),
        "lon": slice(28.0, 52.0),
        "rain_file": (
            "POWER_Point_Monthly_20040101_20241231_001d00N_038d00E_LST.csv"
        ),
    },
    "Central_Africa": {
        "lat": slice(-10.0, 10.0),
        "lon": slice(10.0, 30.0),
        "rain_file": (
            "POWER_Point_Monthly_20040101_20241231_000d00N_020d00E_LST.csv"
        ),
    },
    "South_Africa": {
        "lat": slice(-35.0, -10.0),
        "lon": slice(10.0, 40.0),
        "rain_file": (
            "POWER_Point_Monthly_20040101_20241231_029d00S_024d00E_LST.csv"
        ),
    },
}

START_YEAR = 2004
END_YEAR = 2024


# ==============================================================================
# 2. دالة قراءة وتنسيق ملفات أمطار ناسا (NASA POWER Parser)
# ==============================================================================
def parse_nasa_rainfall(file_path, region_name):
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Error: File '{file_path}' not found in directory!"
        )

    # تخطي السطور التمهيدية والوصول لسطر العناوين
    with open(file_path, "r") as f:
        lines = f.readlines()

    header_idx = None
    for idx, line in enumerate(lines):
        if "YEAR" in line and "JAN" in line:
            header_idx = idx
            break

    if header_idx is None:
        raise ValueError(
            f"Could not find valid data header in file: {file_path}"
        )

    # قراءة الداتا كـ DataFrame
    df_raw = pd.read_csv(file_path, skiprows=header_idx)

    # تنظيف وتفكيك الشهور من أفقي إلى رأسي
    months_abbr = [
        "JAN",
        "FEB",
        "MAR",
        "APR",
        "MAY",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "OCT",
        "NOV",
        "DEC",
    ]
    df_melted = df_raw.melt(
        id_vars=["YEAR"],
        value_vars=months_abbr,
        var_name="Month_Name",
        value_name="Precipitation_mm",
    )

    # تحويل الشهور لأرقام (1 إلى 12) والسنوات لأرقام صحيحة
    month_map = {m: i + 1 for i, m in enumerate(months_abbr)}
    df_melted["Month"] = df_melted["Month_Name"].map(month_map).astype(int)
    df_melted["Year"] = df_melted["YEAR"].astype(int)
    df_melted["Region"] = region_name

    # فلترة المدى الزمني والتأكد من إزالة أي قيم مفقودة (-999 من ناسا)
    df_filtered = df_melted[
        (df_melted["Year"] >= START_YEAR) & (df_melted["Year"] <= END_YEAR)
    ].copy()
    df_filtered.loc[df_filtered["Precipitation_mm"] < 0, "Precipitation_mm"] = (
        0.0
    )

    return df_filtered[["Region", "Year", "Month", "Precipitation_mm"]]


# ==============================================================================
# 3. معالجة درجات الحرارة وقص أقاليم إفريقيا (Temperature Extraction)
# ==============================================================================
print(">>> [1/3] Loading NASA GISTEMP Temperature Data...")
ds_temp = xr.open_dataset("gistemp.nc")

temp_records = []

for region_name, conf in REGIONS_CONFIG.items():
    print(f"    - Processing Temperature for: {region_name}...")

    # قص الإقليم وحساب المتوسط الجغرافي الشهري
    slice_temp = (
        ds_temp["tempanomaly"]
        .sel(lat=conf["lat"], lon=conf["lon"])
        .mean(dim=["lat", "lon"], skipna=True)
    )

    df_slice = slice_temp.to_dataframe().reset_index()
    df_slice["Region"] = region_name
    df_slice["Year"] = df_slice["time"].dt.year.astype(int)
    df_slice["Month"] = df_slice["time"].dt.month.astype(int)
    df_slice["Temperature_Anomaly"] = df_slice["tempanomaly"].round(3)

    # فلترة السنين
    df_slice = df_slice[
        (df_slice["Year"] >= START_YEAR) & (df_slice["Year"] <= END_YEAR)
    ]
    temp_records.append(
        df_slice[["Region", "Year", "Month", "Temperature_Anomaly"]]
    )

df_all_temp = pd.concat(temp_records, ignore_index=True)
print(f">>> Temperature extraction complete! Total records: {len(df_all_temp)}")


# ==============================================================================
# 4. معالجة ملفات الأمطار الخمسة (Rainfall Extraction)
# ==============================================================================
print("\n>>> [2/3] Loading and Parsing NASA POWER Rainfall Files...")
rain_records = []

for region_name, conf in REGIONS_CONFIG.items():
    print(f"    - Loading: {conf['rain_file']} for {region_name}...")
    df_single_rain = parse_nasa_rainfall(conf["rain_file"], region_name)
    rain_records.append(df_single_rain)

df_all_rain = pd.concat(rain_records, ignore_index=True)
print(f">>> Rainfall extraction complete! Total records: {len(df_all_rain)}")


# ==============================================================================
# 5. الدمج النهائي المنهجي والترتيب الصارم (Systematic Merge & Sort)
# ==============================================================================
print("\n>>> [3/3] Merging Temperature and Rainfall into Final Dataset...")

# الدمج الكامل بناءً على الثلاثية (Region, Year, Month)
df_final = pd.merge(
    df_all_temp, df_all_rain, on=["Region", "Year", "Month"], how="inner"
)

# ترتيب البيانات زمنياً وإقليمياً بشكل قطعي ومحدد
df_final = df_final.sort_values(
    by=["Region", "Year", "Month"], ascending=[True, True, True]
).reset_index(drop=True)

# إضافة عمود تاريخ منسق للـ Charts
df_final["Date"] = (
    df_final["Year"].astype(str)
    + "-"
    + df_final["Month"].astype(str).str.zfill(2)
)

# حفظ الملف النهائي
output_csv = "africa_climate_merged_2004_2024.csv"
df_final.to_csv(output_csv, index=False)

# ==============================================================================
# 6. التقرير النهائي للتحقق والتأكيد (Verification Summary)
# ==============================================================================
print("\n" + "=" * 60)
print("           DATASET BUILD SUCCESSFUL!            ")
print("=" * 60)
print(f"Output File Saved    : {output_csv}")
print(f"Total Rows Expected  : 1260 (5 regions x 21 years x 12 months)")
print(f"Actual Rows Generated: {len(df_final)}")
print(f"Null Values Present  : {df_final.isnull().sum().sum()} (Must be 0)")
print("=" * 60)
print("\nFirst 10 Rows Preview:")
print(df_final.head(10))
print("\nLast 5 Rows Preview:")
print(df_final.tail(5))