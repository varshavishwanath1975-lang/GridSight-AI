import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import os

HISTORY_FILE = "database/traffic_history.csv"

def get_realtime_prediction(location):
    if not os.path.exists(HISTORY_FILE):
        return None, None, None, "Collecting Data"

    df = pd.read_csv(HISTORY_FILE)

    if "Location" in df.columns:
        df = df[df["Location"] == location]

    if len(df) < 3:
        return None, None, None, "Collecting Data"

    df["VehicleCount"] = pd.to_numeric(
        df["VehicleCount"],
        errors="coerce"
    ).fillna(0)

    X = np.arange(len(df)).reshape(-1, 1)
    y = df["VehicleCount"].values

    model = LinearRegression()
    model.fit(X, y)

    p15 = int(max(0, round(model.predict([[len(df) + 1]])[0])))
    p30 = int(max(0, round(model.predict([[len(df) + 2]])[0])))
    p60 = int(max(0, round(model.predict([[len(df) + 4]])[0])))

    if p60 > p15:
        trend = "📈 Increasing"
    elif p60 < p15:
        trend = "📉 Decreasing"
    else:
        trend = "➡ Stable"

    return p15, p30, p60, trend