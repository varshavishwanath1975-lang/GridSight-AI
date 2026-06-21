import random

def read_number_plate(image_path):
    demo_plates = [
        "KA01AB1234",
        "KA05MN6789",
        "KA03CD4587",
        "KA51EF9021",
        "KA02GH7744"
    ]

    plate = random.choice(demo_plates)

    all_texts = [
        plate,
        "BENGALURU",
        "TRAFFIC"
    ]

    plates = [plate]

    return all_texts, plates
