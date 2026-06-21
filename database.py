import pandas as pd
from datetime import datetime
import os

CSV_FILE = "database/violations.csv"

def save_record(record):
    record["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record["Violation ID"] = "V" + datetime.now().strftime("%H%M%S")

    df = pd.DataFrame([record])

    if os.path.exists(CSV_FILE):
        df.to_csv(CSV_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(CSV_FILE, index=False)

    return record