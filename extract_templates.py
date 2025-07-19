
import PyPDF2
import os

def extract_pdf_text(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading {pdf_path}: {e}"

# Extract content from all template PDFs
template_files = [
    'attached_assets/Arbitration Agreement_1752947353758.pdf',
    'attached_assets/Bill of Sale_1752947353758.pdf', 
    'attached_assets/Buyers Guide_1752947353758.pdf',
    'attached_assets/Odometer Disclosure Statement_1752947353758.pdf',
    'attached_assets/RECEIPT FOR DOWNPAYMENT_1752947353758.pdf',
    'attached_assets/Vehicle-Repayment-Agreement_1752947353759.pdf',
    'attached_assets/WAIVER OF VEHICLE SERVICE CONTRACT_1752947353759.pdf'
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
