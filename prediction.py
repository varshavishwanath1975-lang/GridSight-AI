import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import os

HISTORY_FILE = "database/traffic_history.csv"

def predict_future_vehicle_count(location):
    if not os.path.exists(HISTORY_FILE):
        return None

    df = pd.read_csv(HISTORY_FILE)

    if "Location" in df.columns:
        df = df[df["Location"] == location]

    if len(df) < 3:
        return None

    df["VehicleCount"] = pd.to_numeric(df["VehicleCount"], errors="coerce").fillna(0)

    X = np.arange(len(df)).reshape(-1, 1)
    y = df["VehicleCount"].values

    model = LinearRegression()
    model.fit(X, y)

    future_x = np.array([[len(df)]])
    prediction = model.predict(future_x)[0]

    return max(0, int(round(prediction)))