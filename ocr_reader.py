import easyocr
import cv2
import re

reader = easyocr.Reader(["en"], gpu=False)

def read_number_plate(image_path):
    image = cv2.imread(image_path)

    if image is None:
        return [], []

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = reader.readtext(image)

    all_texts = []
    plates = []

    for result in results:
        text = result[1]

        cleaned = (
            text.replace(" ", "")
            .replace("-", "")
            .replace(".", "")
            .replace("_", "")
            .upper()
        )

        cleaned = cleaned.replace("O", "0")
        cleaned = cleaned.replace("I", "1")
        cleaned = cleaned.replace("L", "1")

        all_texts.append(text)

        has_digits = re.search(r"[0-9]", cleaned)

        if len(cleaned) >= 5 and has_digits:
            if cleaned not in plates:
                plates.append(cleaned)

    return all_texts, plates