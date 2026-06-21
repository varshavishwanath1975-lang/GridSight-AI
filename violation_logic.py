def classify_traffic(vehicle_count):
    if vehicle_count >= 30:
        return "Severe Congestion", "High"

    elif vehicle_count >= 15:
        return "Traffic Congestion", "Medium"

    else:
        return "Normal Traffic", "Low"