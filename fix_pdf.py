"""Fix PDF generation - fpdf output returns bytearray, not str."""
import re

path = "backend/app/routers/erp.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace pdf.output(dest='S').encode('latin-1') with bytes(pdf.output(dest='S'))
content = content.replace(
    "pdf.output(dest='S').encode('latin-1')",
    "bytes(pdf.output(dest='S'))"
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("PDF fixes applied")