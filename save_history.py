import pandas as pd
import os
from datetime import datetime

HISTORY_FILE = "database/traffic_history.csv"

def save_traffic_history(location, vehicle_count):
    row = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Location": location,
        "VehicleCount": vehicle_count
    }

    df = pd.DataFrame([row])

    if os.path.exists(HISTORY_FILE):
        df.to_csv(HISTORY_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(HISTORY_FILE, index=False)