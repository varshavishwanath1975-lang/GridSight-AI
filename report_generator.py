import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(report):
    os.makedirs("outputs", exist_ok=True)

    pdf_file = "outputs/report.pdf"

    doc = SimpleDocTemplate(pdf_file)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("GridSight AI Traffic Intelligence Report", styles["Title"]))
    content.append(Spacer(1, 20))

    content.append(Paragraph("<b>Evidence Details</b>", styles["Heading2"]))
    content.append(Spacer(1, 10))

    for key, value in report.items():
        safe_value = str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        content.append(Paragraph(f"<b>{key}</b>: {safe_value}", styles["BodyText"]))
        content.append(Spacer(1, 8))

    content.append(Spacer(1, 20))

    content.append(Paragraph("<b>AI Observation</b>", styles["Heading2"]))
    content.append(Paragraph(
        "The uploaded traffic image was analyzed using YOLOv8 vehicle detection and EasyOCR number plate recognition. "
        "The system calculated current congestion, predicted future traffic risk, and generated enforcement recommendations.",
        styles["BodyText"]
    ))

    content.append(Spacer(1, 20))

    content.append(Paragraph("<b>Recommended Action</b>", styles["Heading2"]))
    content.append(Paragraph(
        "This report can be used by traffic authorities for congestion monitoring, hotspot identification, "
        "resource deployment, and enforcement decision support.",
        styles["BodyText"]
    ))

    doc.build(content)
    return pdf_file
