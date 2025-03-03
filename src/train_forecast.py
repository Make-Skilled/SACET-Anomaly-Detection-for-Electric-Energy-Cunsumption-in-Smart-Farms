import pandas as pd
import joblib
from statsmodels.tsa.arima.model import ARIMA

# Load data from CSV
def load_data():
    df = pd.read_csv("../dataset/energy_consumption.csv", parse_dates=["timestamp"])
    df.set_index("timestamp", inplace=True)
    return df

# Train ARIMA Forecast Model
def train_arima():
    df = load_data()

    if len(df) < 10:
        print("❌ Not enough data to train the model.")
        return
    
    model = ARIMA(df["power_usage"], order=(5,1,0))  # (p,d,q) values can be tuned
    model_fit = model.fit()
    
    joblib.dump(model_fit, "forecast_model.pkl")
    print("✅ Forecast model trained and saved as 'forecast_model.pkl'.")

if __name__ == "__main__":
    train_arima()
