import numpy as np
import pandas as pd

# Generate hourly timestamps for a year
timestamps = pd.date_range(start="2024-01-01", periods=8760, freq="H")

# Normal energy consumption range
np.random.seed(42)
power_usage = np.random.normal(loc=500, scale=50, size=len(timestamps))

# Introduce anomalies (spikes/drops)
anomaly_indices = np.random.choice(len(timestamps), size=200, replace=False)
power_usage[anomaly_indices] *= np.random.uniform(1.5, 3.0, size=len(anomaly_indices))

# Create dataset
df = pd.DataFrame({"timestamp": timestamps, "power_usage": power_usage})
df.to_csv("dataset/energy_consumption.csv", index=False)
print("Dataset saved!")
