from ultralytics import YOLO

model = YOLO("yolov8n.pt")

def detect_vehicles(image_path):
    results = model(image_path)

    vehicle_classes = ["car", "motorcycle", "bus", "truck"]
    count = 0

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]

            if class_name in vehicle_classes:
                count += 1

    return results, count