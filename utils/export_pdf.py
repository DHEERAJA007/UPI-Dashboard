from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def export_pdf(summary):
    c = canvas.Canvas("upi_report.pdf", pagesize=letter)
    c.setFont("Helvetica", 14)
    c.drawString(100, 750, "UPI Transaction Summary Report")
    y = 700
    for key, value in summary.items():
        c.drawString(100, y, f"{key}: {value}")
        y -= 30
    c.save()