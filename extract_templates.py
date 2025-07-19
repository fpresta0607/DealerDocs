
import pdfplumber
import os

def extract_pdf_text(pdf_path):
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        return f"Error reading {pdf_path}: {e}"

# Extract content from all template PDFs
template_files = [
    'contract-templates/Arbitration Agreement.pdf',
    'contract-templates/Bill of Sale.pdf', 
    'contract-templates/Buyers Guide.pdf',
    'contract-templates/Odometer Disclosure Statement.pdf',
    'contract-templates/RECEIPT FOR DOWNPAYMENT.pdf',
    'contract-templates/Vehicle-Repayment-Agreement.pdf',
    'contract-templates/WAIVER OF VEHICLE SERVICE CONTRACT.pdf'
]

for file_path in template_files:
    if os.path.exists(file_path):
        print(f"\n{'='*50}")
        print(f"TEMPLATE: {file_path}")
        print(f"{'='*50}")
        content = extract_pdf_text(file_path)
        print(content)
    else:
        print(f"File not found: {file_path}")
