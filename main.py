from flask import Flask, render_template, request, send_file
import os
import shutil
import zipfile
from fpdf import FPDF
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, BooleanObject
import datetime

app = Flask(__name__)

OUTPUT_DIR = 'output'
TEMPLATE_DIR = 'contract-templates'


def fill_pdf_form(template_name, output_name, field_values):
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    if not os.path.exists(template_path):
        return False
    reader = PdfReader(template_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    if reader.trailer['/Root'].get('/AcroForm'):
        acro = reader.trailer['/Root']['/AcroForm'].get_object()
        acro.update({NameObject('/NeedAppearances'): BooleanObject(True)})
        writer._root_object.update({NameObject('/AcroForm'): acro})
        for page in writer.pages:
            writer.update_page_form_field_values(page, field_values)
    with open(os.path.join(OUTPUT_DIR, output_name), 'wb') as f:
        writer.write(f)
    return True


def ensure_output_dir():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/static/<filename>')
def static_files(filename):
    return send_file(f'static/{filename}')


@app.route('/generate', methods=['POST'])
def generate():
    ensure_output_dir()

    seller = request.form['seller']
    buyer = request.form['buyer']
    seller_address = request.form['seller_address']
    buyer_address = request.form['buyer_address']
    buyer_dob = request.form.get('buyer_dob', '')
    buyer_ssn = request.form.get('buyer_ssn', '')
    buyer_income = request.form.get('buyer_income', '')
    vin = request.form['vin']
    make = request.form['make']
    model = request.form['model']
    year = request.form['year']
    mileage = request.form['mileage']
    price = request.form['price']
    state = request.form['state']
    down_payment = request.form.get('down_payment', '0')
    interest_rate = request.form.get('interest_rate', '0')
    term_months = request.form.get('term_months', '0')

    # Use pre-configured Car Match Chicago logo
    logo_path = 'static/car-match-logo.png'

    current_date = datetime.date.today().strftime('%Y-%m-%d')

    # Generate PDFs
    generate_bill_of_sale(seller, buyer, vin, make, model, year, mileage,
                          price, state, current_date)
    generate_odometer_statement(seller, buyer, vin, make, model, year, mileage,
                                current_date)
    generate_invoice(seller, buyer, vin, make, model, year, mileage, price,
                     current_date, logo_path)
    generate_sellers_report(seller, seller_address, buyer, buyer_address, vin,
                            make, year, current_date)
    generate_poa(buyer, seller, vin, make, model, year, current_date)
    generate_buyers_guide(vin, make, model, year, mileage, current_date)
    generate_arbitration_agreement(seller, buyer, current_date)
    generate_waiver_service_contract(seller, buyer, current_date)
    generate_loan_application(buyer, buyer_address, buyer_dob, buyer_ssn,
                              buyer_income, price, current_date)
    generate_loan_repayment(seller, seller_address, buyer, buyer_address, vin,
                            make, model, year, price, down_payment, interest_rate,
                            term_months, current_date)

    # Create ZIP
    zip_path = os.path.join(OUTPUT_DIR, 'sale_packet.zip')
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for filename in [
                'bill_of_sale.pdf', 'odometer_statement.pdf', 'invoice.pdf',
                'sellers_report.pdf', 'poa.pdf', 'buyers_guide.pdf',
                'arbitration_agreement.pdf', 'waiver_service_contract.pdf',
                'loan_application.pdf', 'loan_repayment.pdf'
        ]:
            pdf_path = os.path.join(OUTPUT_DIR, filename)
            if os.path.exists(pdf_path):
                zipf.write(pdf_path, arcname=filename)

    # Logo is static file, no cleanup needed

    return render_template('complete.html')


@app.route('/download')
def download():
    zip_path = os.path.join(OUTPUT_DIR, 'sale_packet.zip')
    if os.path.exists(zip_path):
        return send_file(zip_path,
                         as_attachment=True,
                         download_name='sale_packet.zip')
    return 'File not found', 404


def generate_bill_of_sale(seller, buyer, vin, make, model, year, mileage,
                          price, state, date):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Bill of Sale', ln=1, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.ln(10)
    pdf.cell(0, 10, f'Date: {date}', ln=1)
    pdf.cell(0, 10, f'State: {state}', ln=1)
    pdf.ln(5)
    pdf.cell(0, 10, 'Seller Information:', ln=1)
    pdf.cell(0, 10, f'Name: {seller}', ln=1)
    pdf.ln(5)
    pdf.cell(0, 10, 'Buyer Information:', ln=1)
    pdf.cell(0, 10, f'Name: {buyer}', ln=1)
    pdf.ln(5)
    pdf.cell(0, 10, 'Vehicle Information:', ln=1)
    pdf.cell(0, 10, f'Year: {year}  Make: {make}  Model: {model}', ln=1)
    pdf.cell(0, 10, f'VIN: {vin}  Mileage: {mileage}', ln=1)
    pdf.ln(5)
    pdf.cell(0, 10, f'Sale Price: ${price}', ln=1)
    pdf.ln(10)
    pdf.cell(0, 10, 'The vehicle is sold "AS-IS" with no warranties.', ln=1)
    pdf.ln(20)
    pdf.cell(0, 10, 'Seller Signature: ___________________________', ln=1)
    pdf.cell(0, 10, 'Buyer Signature: ___________________________', ln=1)
    pdf.output(os.path.join(OUTPUT_DIR, 'bill_of_sale.pdf'))


def generate_odometer_statement(seller, buyer, vin, make, model, year, mileage,
                                date):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0,
             10,
             'Odometer Disclosure Statement (VSD 333 Equivalent)',
             ln=1,
             align='C')
    pdf.set_font('Arial', '', 12)
    pdf.ln(10)
    pdf.cell(0, 10, f'Date: {date}', ln=1)
    pdf.ln(5)
    pdf.cell(0, 10, 'Vehicle Information:', ln=1)
    pdf.cell(0, 10, f'Year: {year}  Make: {make}  Model: {model}', ln=1)
    pdf.cell(0, 10, f'VIN: {vin}', ln=1)
    pdf.ln(5)
    pdf.cell(0, 10, f'Odometer Reading: {mileage} miles', ln=1)
    pdf.ln(5)
    pdf.multi_cell(
        0, 10,
        'I, the undersigned, certify to the best of my knowledge that the odometer reading is the actual mileage of the vehicle described above.'
    )
    pdf.ln(10)
    pdf.cell(0, 10, f'Seller: {seller}', ln=1)
    pdf.cell(0, 10, f'Buyer: {buyer}', ln=1)
    pdf.ln(20)
    pdf.cell(0, 10, 'Seller Signature: ___________________________', ln=1)
    pdf.cell(0, 10, 'Buyer Signature: ___________________________', ln=1)
    pdf.output(os.path.join(OUTPUT_DIR, 'odometer_statement.pdf'))


def generate_invoice(seller, buyer, vin, make, model, year, mileage, price,
                     date, logo_path):
    pdf = FPDF()
    pdf.add_page()
    if logo_path:
        pdf.image(logo_path, x=10, y=10, w=50)
        pdf.ln(40)  # Space after logo
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Invoice', ln=1, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.ln(10)
    pdf.cell(0, 10, f'Date: {date}', ln=1)
    pdf.ln(5)
    pdf.cell(0, 10, 'From (Seller):', ln=1)
    pdf.cell(0, 10, f'Name: {seller}', ln=1)
    pdf.ln(5)
    pdf.cell(0, 10, 'To (Buyer):', ln=1)
    pdf.cell(0, 10, f'Name: {buyer}', ln=1)
    pdf.ln(5)
    pdf.cell(0, 10, 'Vehicle Details:', ln=1)
    pdf.cell(0, 10, f'Year: {year}  Make: {make}  Model: {model}', ln=1)
    pdf.cell(0, 10, f'VIN: {vin}  Mileage: {mileage}', ln=1)
    pdf.ln(10)
    pdf.cell(0, 10, f'Amount Due: ${price}', ln=1)
    pdf.ln(20)
    pdf.cell(0, 10, 'Thank you for your purchase.', ln=1)
    pdf.output(os.path.join(OUTPUT_DIR, 'invoice.pdf'))


def generate_sellers_report(seller, seller_address, buyer, buyer_address, vin,
                            make, year, date):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0,
             10,
             "Seller's Report of Sale (VSD-703 Equivalent)",
             ln=1,
             align='C')
    pdf.set_font('Arial', '', 12)
    pdf.ln(10)
    pdf.cell(0, 10, f'Date of Sale: {date}', ln=1)
    pdf.ln(5)
    pdf.cell(0, 10, 'Vehicle Information:', ln=1)
    pdf.cell(0, 10, f'Year: {year}  Make: {make}', ln=1)
    pdf.cell(0, 10, f'VIN: {vin}', ln=1)
    pdf.ln(5)
    pdf.cell(0, 10, 'Seller Information:', ln=1)
    pdf.cell(0, 10, f'Name: {seller}', ln=1)
    pdf.multi_cell(0, 10, f'Address: {seller_address}')
    pdf.ln(5)
    pdf.cell(0, 10, 'Buyer Information:', ln=1)
    pdf.cell(0, 10, f'Name: {buyer}', ln=1)
    pdf.multi_cell(0, 10, f'Address: {buyer_address}')
    pdf.ln(10)
    pdf.cell(0, 10, f'Executed on: {date}', ln=1)
    pdf.ln(10)
    pdf.multi_cell(
        0, 10,
        'I certify under penalties of perjury that the foregoing information is true and correct.'
    )
    pdf.ln(20)
    pdf.cell(0, 10, 'Signature of Seller: ___________________________', ln=1)
    pdf.cell(0, 10, 'Printed Name: {seller}', ln=1)
    pdf.output(os.path.join(OUTPUT_DIR, 'sellers_report.pdf'))


def generate_poa(principal, agent, vin, make, model, year, date):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0,
             10,
             'Power of Attorney for Vehicle Transactions (VSD-392 Equivalent)',
             ln=1,
             align='C')
    pdf.set_font('Arial', '', 12)
    pdf.ln(10)
    pdf.cell(0, 10, f'Date: {date}', ln=1)
    pdf.ln(5)
    pdf.cell(0, 10, f'Principal (Buyer): {principal}', ln=1)
    pdf.cell(0, 10, f'Agent (Seller/Dealership): {agent}', ln=1)
    pdf.ln(5)
    pdf.cell(0, 10, 'Vehicle Information:', ln=1)
    pdf.cell(0, 10, f'Year: {year}  Make: {make}  Model: {model}', ln=1)
    pdf.cell(0, 10, f'VIN: {vin}', ln=1)
    pdf.ln(5)
    pdf.multi_cell(
        0, 10,
        'I appoint the above agent to sign all papers and documents required to secure title and registration for the above vehicle.'
    )
    pdf.ln(10)
    pdf.multi_cell(
        0, 10, 'This power of attorney is valid until revoked in writing.')
    pdf.ln(20)
    pdf.cell(0, 10, 'Principal Signature: ___________________________', ln=1)
    pdf.output(os.path.join(OUTPUT_DIR, 'poa.pdf'))


def generate_buyers_guide(vin, make, model, year, mileage, date):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Buyers Guide (AS-IS)', ln=1, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.ln(10)
    pdf.cell(0, 10, f'Date: {date}', ln=1)
    pdf.ln(5)
    pdf.cell(0, 10, 'Vehicle Information:', ln=1)
    pdf.cell(0, 10, f'Year: {year}  Make: {make}  Model: {model}', ln=1)
    pdf.cell(0, 10, f'VIN: {vin}  Odometer: {mileage}', ln=1)
    pdf.ln(10)
    pdf.multi_cell(
        0, 10,
        'IMPORTANT: Spoken promises are difficult to enforce. Ask the dealer to put all promises in writing. Keep this form.'
    )
    pdf.ln(5)
    pdf.multi_cell(
        0, 10,
        'AS IS - NO WARRANTY: The seller does not provide a warranty for any repairs after sale.'
    )
    pdf.ln(5)
    pdf.multi_cell(
        0, 10,
        'Pre-purchase inspection: Ask the dealer if you may have this vehicle inspected by your mechanic either on or off the lot.'
    )
    pdf.ln(20)
    pdf.cell(0, 10, 'Buyer Acknowledgment: ___________________________', ln=1)
    pdf.output(os.path.join(OUTPUT_DIR, 'buyers_guide.pdf'))


def generate_arbitration_agreement(seller, buyer, date):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Arbitration Agreement', ln=1, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.ln(10)
    pdf.cell(0, 10, f'Date: {date}', ln=1)
    pdf.ln(5)
    pdf.cell(0, 10, f'Between: {seller} (Seller) and {buyer} (Buyer)', ln=1)
    pdf.ln(10)
    pdf.multi_cell(
        0, 10,
        'Any controversy or claim arising out of or relating to this contract or the breach thereof shall be settled by arbitration in accordance with the Commercial Arbitration Rules of the American Arbitration Association.'
    )
    pdf.ln(5)
    pdf.multi_cell(
        0, 10,
        'Judgment upon the award rendered by the arbitrator(s) may be entered in any court having jurisdiction thereof.'
    )
    pdf.ln(20)
    pdf.cell(0, 10, 'Seller Signature: ___________________________', ln=1)
    pdf.cell(0, 10, 'Buyer Signature: ___________________________', ln=1)
    pdf.output(os.path.join(OUTPUT_DIR, 'arbitration_agreement.pdf'))


def generate_waiver_service_contract(seller, buyer, date):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Waiver of Vehicle Service Contract', ln=1, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.ln(10)
    pdf.cell(0, 10, f'Date: {date}', ln=1)
    pdf.ln(5)
    pdf.cell(0, 10, f'Buyer: {buyer}', ln=1)
    pdf.cell(0, 10, f'Seller: {seller}', ln=1)
    pdf.ln(10)
    pdf.multi_cell(
        0, 10,
        'I, the undersigned buyer, hereby waive the purchase of any vehicle service contract or extended warranty for the vehicle purchased.'
    )
    pdf.ln(5)
    pdf.multi_cell(
        0, 10,
        'I understand that by waiving this, I am responsible for all future repair costs.'
    )
    pdf.ln(20)
    pdf.cell(0, 10, 'Buyer Signature: ___________________________', ln=1)
    pdf.output(os.path.join(OUTPUT_DIR, 'waiver_service_contract.pdf'))


def generate_loan_application(buyer, buyer_address, buyer_dob, buyer_ssn,
                              buyer_income, price, date):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Loan Application', ln=1, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.ln(10)
    pdf.cell(0, 10, f'Date: {date}', ln=1)
    pdf.ln(5)
    pdf.cell(0, 10, 'Applicant Information:', ln=1)
    pdf.cell(0, 10, f'Name: {buyer}', ln=1)
    pdf.multi_cell(0, 10, f'Address: {buyer_address}')
    pdf.cell(0, 10, f'DOB: {buyer_dob}', ln=1)
    pdf.cell(0, 10, f'SSN: {buyer_ssn}', ln=1)
    pdf.cell(0, 10, f'Monthly Income: ${buyer_income}', ln=1)
    pdf.ln(5)
    pdf.cell(0, 10, f'Loan Amount Requested: ${price}', ln=1)
    pdf.ln(10)
    pdf.multi_cell(
        0, 10, 'I certify that the information provided is true and complete.')
    pdf.ln(20)
    pdf.cell(0, 10, 'Applicant Signature: ___________________________', ln=1)
    pdf.output(os.path.join(OUTPUT_DIR, 'loan_application.pdf'))


def generate_loan_repayment(seller, seller_address, buyer, buyer_address, vin,
                            make, model, year, price, down_payment,
                            interest_rate, term_months, date):
    try:
        down_payment_f = float(down_payment)
        price_f = float(price)
        interest_rate_f = float(interest_rate)
        term_months_i = int(term_months)
    except ValueError:
        down_payment_f = 0.0
        price_f = float(price or 0)
        interest_rate_f = 0.0
        term_months_i = int(term_months or 0)

    field_map = {
        'Lender': seller,
        'Lender mailing address': seller_address,
        'Borrower': buyer,
        'Borrower mailing address': buyer_address,
        'Make': make,
        'Model': model,
        'Year': year,
        'VIN': vin,
        'Loan': str(price_f),
        'Amount': str(price_f),
        'Amount 2': str(down_payment_f),
        'per annum': f"{interest_rate_f}%",
        'Repayment Terms': f"{term_months_i} months",
        'Date': date,
    }

    if fill_pdf_form('Vehicle-Repayment-Agreement.pdf', 'loan_repayment.pdf', field_map):
        return

    # Fallback to basic PDF if template not found
    monthly_rate = interest_rate_f / 100 / 12 if interest_rate_f else 0
    loan_amount = price_f - down_payment_f
    if term_months_i > 0 and monthly_rate > 0:
        payment = (loan_amount * monthly_rate * (1 + monthly_rate)**term_months_i) / (
            (1 + monthly_rate)**term_months_i - 1)
        payment = round(payment, 2)
    else:
        payment = loan_amount / term_months_i if term_months_i > 0 else loan_amount

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Loan Repayment Agreement', ln=1, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.ln(10)
    pdf.cell(0, 10, f'Date: {date}', ln=1)
    pdf.ln(5)
    pdf.cell(0, 10, f'Lender: {seller}', ln=1)
    pdf.cell(0, 10, f'Borrower: {buyer}', ln=1)
    pdf.ln(5)
    pdf.cell(0, 10, f'Loan Amount: ${loan_amount}', ln=1)
    pdf.cell(0, 10, f'Interest Rate: {interest_rate_f}% APR', ln=1)
    pdf.cell(0, 10, f'Term: {term_months_i} months', ln=1)
    pdf.cell(0, 10, f'Monthly Payment: ${payment}', ln=1)
    pdf.ln(10)
    pdf.multi_cell(0, 10,
        'The borrower agrees to repay the loan in monthly installments until paid in full.')
    pdf.ln(20)
    pdf.cell(0, 10, 'Borrower Signature: ___________________________', ln=1)
    pdf.output(os.path.join(OUTPUT_DIR, 'loan_repayment.pdf'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
