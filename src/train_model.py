import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

# Load data
df = pd.read_csv("./dataset/energy_consumption.csv")
X = df[["power_usage"]]

# Train Isolation Forest
model = IsolationForest(contamination=0.05, random_state=42)
df["anomaly"] = model.fit_predict(X)

# Save model
joblib.dump(model, "isolation_forest.pkl")
print("Model trained and saved!")
