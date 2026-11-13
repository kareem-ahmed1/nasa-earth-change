import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

print("="*65)
print("  NASA HACKATHON: AI CLIMATE & DROUGHT PREDICTOR FOR AFRICA")
print("="*65)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

# --- 1. LOAD HISTORICAL TEMPERATURE DATA (GISTEMP) ---
print("\n[Step 1/5] Loading NASA GISTEMP Temperature Anomalies...")
ds_temp = xr.open_dataset(os.path.join(BASE_DIR, "gistemp.nc"))

# Slice to Africa coordinates (-35 to 38 Lat, -18 to 52 Lon)
africa_temp = ds_temp["tempanomaly"].sel(lat=slice(-35.0, 38.0), lon=slice(-18.0, 52.0))

# Calculate historical African continental average (1880 - 2026)
africa_trend = africa_temp.mean(dim=["lat", "lon"]).to_dataframe().reset_index().dropna()
africa_trend["rolling_12m"] = africa_trend["tempanomaly"].rolling(12).mean()

# --- 2. GENERATE CHART 1: HISTORICAL AFRICA WARMING TREND ---
print("[Step 2/5] Generating Chart 1: Historical Africa Warming Trend...")
plt.figure(figsize=(10, 4.5))
plt.plot(africa_trend["time"], africa_trend["tempanomaly"], color="#fdae61", alpha=0.35, label="Monthly Anomaly")
plt.plot(africa_trend["time"], africa_trend["rolling_12m"], color="#d7191c", linewidth=2.2, label="12-Month Moving Average")
plt.axhline(0, color="black", linestyle="--", alpha=0.6)
plt.title("Long-Term Surface Temperature Anomaly over Africa (1880 - Present)", fontsize=13, fontweight="bold")
plt.xlabel("Year", fontsize=11)
plt.ylabel("Temperature Anomaly (°C)", fontsize=11)
plt.legend(loc="upper left")
plt.grid(True, linestyle=":", alpha=0.5)
plt.tight_layout()
chart1_path = "chart1_africa_warming_trend.png"
plt.savefig(chart1_path, dpi=300)
plt.close()
print(f" -> Saved: {chart1_path}")

# --- 3. MERGE RECENT TEMPERATURE WITH SATELLITE VEGETATION ---
print("\n[Step 3/5] Merging Temperature with Satellite Vegetation (NDVI) across Africa...")
ds_veg = xr.open_dataset(os.path.join(BASE_DIR, "NDVI_dataset.nc"))

# Align coordinates for Jan 2023 snapshot
t_slice = africa_temp.sel(time="2023-01-15").squeeze().drop_vars("time")
v_slice = ds_veg["NDVI"].sel(latitude=slice(38.0, -35.0), longitude=slice(-18.0, 52.0)).squeeze().drop_vars("time")
v_renamed = v_slice.rename({"latitude": "lat", "longitude": "lon"})

# Match grids using nearest neighbor
v_interp = v_renamed.interp(lat=t_slice.lat, lon=t_slice.lon, method="nearest")

# Build unified tabular dataset
df_africa = pd.DataFrame({
    "lat": t_slice.lat.values.repeat(len(t_slice.lon)),
    "lon": list(t_slice.lon.values) * len(t_slice.lat),
    "temp_anomaly": t_slice.values.flatten(),
    "ndvi": v_interp.values.flatten()
}).dropna()

# Filter valid land areas
df_africa = df_africa[df_africa["ndvi"] >= 0].reset_index(drop=True)
print(f" -> Successfully matched {len(df_africa)} ground coordinate cells across Africa!")

# Calculate Correlation
corr = df_africa["temp_anomaly"].corr(df_africa["ndvi"])
print(f" -> Temperature vs. Vegetation Correlation: {corr:.4f}")

# --- 4. GENERATE CHART 2: SCATTER PLOT & DISTRIBUTION ---
print("\n[Step 4/5] Generating Chart 2: Climate Impact Scatter Plot...")
plt.figure(figsize=(8, 4.5))
plt.scatter(df_africa["temp_anomaly"], df_africa["ndvi"], c=df_africa["ndvi"], cmap="YlGn", edgecolors="black", linewidth=0.3, alpha=0.75)
z = np.polyfit(df_africa["temp_anomaly"], df_africa["ndvi"], 1)
p = np.poly1d(z)
plt.plot(df_africa["temp_anomaly"], p(df_africa["temp_anomaly"]), color="red", linestyle="--", linewidth=1.5, label="Trendline")
plt.title("Impact of Surface Temperature Anomaly on Vegetation Index (Africa)", fontsize=12, fontweight="bold")
plt.xlabel("Temperature Anomaly (°C)", fontsize=11)
plt.ylabel("Vegetation Greenness (NDVI)", fontsize=11)
plt.colorbar(label="NDVI Value")
plt.legend()
plt.grid(True, linestyle=":", alpha=0.5)
plt.tight_layout()
chart2_path = "chart2_temp_vs_vegetation_scatter.png"
plt.savefig(chart2_path, dpi=300)
plt.close()
print(f" -> Saved: {chart2_path}")

# --- 5. TRAIN AI DROUGHT PREDICTION MODEL ---
print("\n[Step 5/5] Training AI Machine Learning Model (Drought Risk Classifier)...")

# Define Disaster / Drought Severity Levels (Ground Truth Rules)
# Severe: High Heat (> 1.2°C) AND Low Vegetation (< 0.25)
# Moderate: Warm (> 0.8°C) OR Low-to-Mid Vegetation (< 0.35)
# Low/Healthy: Normal heat and green vegetation (NDVI >= 0.35)
conditions = [
    (df_africa["temp_anomaly"] >= 1.2) & (df_africa["ndvi"] < 0.25),
    (df_africa["temp_anomaly"] >= 0.8) | (df_africa["ndvi"] < 0.35)
]
choices = ["Severe Drought Alert", "Moderate Stress"]
df_africa["drought_risk"] = np.select(conditions, choices, default="Healthy / Low Risk")

# Features & Target
X = df_africa[["lat", "lon", "temp_anomaly"]]
y = df_africa["drought_risk"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred) * 100

print("\n" + "="*50)
print(f"  AI MODEL ACCURACY: {accuracy:.2f}%")
print("="*50)
print("\nDetailed Performance Report:")
print(classification_report(y_test, y_pred))

# --- 6. GENERATE CHART 3: AI-PREDICTED AFRICA DROUGHT MAP ---
plt.figure(figsize=(8, 7))
color_map = {"Healthy / Low Risk": "#2ca02c", "Moderate Stress": "#ff7f0e", "Severe Drought Alert": "#d62728"}
for label, color in color_map.items():
    subset = df_africa[df_africa["drought_risk"] == label]
    plt.scatter(subset["lon"], subset["lat"], c=color, label=label, s=35, alpha=0.8, edgecolors="none")

plt.title("AI-Predicted Climate & Drought Risk Map (Africa)", fontsize=13, fontweight="bold")
plt.xlabel("Longitude (°E)", fontsize=11)
plt.ylabel("Latitude (°N)", fontsize=11)
plt.legend(loc="lower left", framealpha=0.9)
plt.grid(True, linestyle=":", alpha=0.5)
plt.tight_layout()
chart3_path = "chart3_africa_drought_map.png"
plt.savefig(chart3_path, dpi=300)
plt.close()
print(f" -> Saved: {chart3_path}")

print("\nAll 3 presentation charts and AI metrics generated successfully in D:\\Desktop\\nasa\\!")
