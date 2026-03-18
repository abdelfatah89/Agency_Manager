from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import sys
import os
import logging

from sqlalchemy.exc import SQLAlchemyError
from PyQt5.QtWidgets import QTableWidget, QComboBox, QDateEdit, QLabel, QWidget
from src.utils.printing import open_pdf_file
from src.utils.company_info import load_company_info, to_invoice_context


logger = logging.getLogger(__name__)

# Adjust Python path to allow absolute imports from 'services'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
try:
    from services import with_session, Client, select
except ImportError:
    logger.warning("Could not import DB models from 'services'")
    with_session = lambda f: f  # mock decorator if missing


@with_session
def extract_invoice_data(table, combo, date_widget_from, date_widget_to, lbl_total, lbl_paid, lbl_rest, session=None):
    """
    Extract data from FacturesWindow widgets and Database, then format 
    it as a dictionary suitable for Jinja PDF generation.
    """
    data = {
        **to_invoice_context(load_company_info()),
        "invoice_no": "",
    }

    # 1. Extract Date From/To
    def get_date_str(widget):
        if isinstance(widget, QDateEdit):
            return widget.date().toString("dd/MM/yyyy")
        return str(widget) if widget else ""

    d_from = get_date_str(date_widget_from)
    d_to = get_date_str(date_widget_to)
    
    # If both dates are identical, display as single Date. Otherwise, display range 'Période'.
    if d_from == d_to:
        data["date_label"] = "التاريخ"
        data["date"] = d_from
    else:
        data["date_label"] = "المدة"
        data["date"] = f"{d_from} - {d_to}"

    # 2. Extract Client Info
    client_name = combo.currentText() if isinstance(combo, QComboBox) else str(combo)
    data["client_name"] = client_name
    data["client_ice"] = "Ets"  # Default ICE
    
    if session and client_name and "اختر العميل" not in client_name:
        try:
            stmt = select(Client).where(Client.full_name == client_name)
            client = session.execute(stmt).scalar_one_or_none()
            if client:
                data["client_name"] = client.full_name
                data["client_ice"] = client.ice if client.ice else "Ets"
        except SQLAlchemyError as err:
            logger.exception("Error extracting client info for invoice")

    # 3. Extract Table Items
    items = []
    if isinstance(table, QTableWidget):
        for row in range(table.rowCount()):
            date_val = table.item(row, 0).text() if table.item(row, 0) else ""
            desc_val = table.item(row, 1).text() if table.item(row, 1) else ""
            
            # Amount
            amt_str = table.item(row, 2).text() if table.item(row, 2) else "0"
            amt_str = amt_str.replace(',', '')
            try:
                amount = float(amt_str)
            except ValueError:
                amount = 0.0
                
            # Paid
            paid_str = table.item(row, 3).text() if table.item(row, 3) else "0"
            paid_str = paid_str.replace(',', '')
            try:
                paid = float(paid_str)
            except ValueError:
                paid = 0.0

            items.append({
                "date": date_val,
                "description": desc_val,
                "amount": amount,
                "paid": paid
            })
    data["items"] = items

    # 4. Extract Totals
    def parse_label(lbl):
        text = lbl.text() if hasattr(lbl, 'text') else str(lbl)
        text = text.replace(',', '')
        try:
            return float(text)
        except ValueError:
            return 0.0
            
    data["total_amount"] = parse_label(lbl_total)
    data["total_paid"] = parse_label(lbl_paid)
    data["balance"] = parse_label(lbl_rest)

    return data


def generate_invoice(data, invoice_number=None):
    """Generate PDF invoice and open it with the default system viewer."""
    # Get absolute path to current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader(current_dir))
    
    try:
        template = env.get_template('invoice.html')
        
        # Add print date if not provided
        if 'print_date' not in data:
            data['print_date'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        if invoice_number:
            data['invoice_no'] = invoice_number
    
        # Render HTML with data
        html_out = template.render(data)
        
        # Convert HTML to PDF with external CSS
        file_name = f"{data.get('invoice_no') or 'facture'}_facture.pdf"
        pdf_path = os.path.join(current_dir, file_name)
        HTML(string=html_out, base_url=current_dir).write_pdf(
            pdf_path,
            stylesheets=[CSS(os.path.join(current_dir, 'style.css'))]
        )
        open_pdf_file(pdf_path)
        logger.info("Invoice generated: %s", pdf_path)
        return pdf_path
    except Exception:
        logger.exception("Invoice generation failed")
        return None


def extract_daily_invoice_data(
    table,
    combo_client,
    input_name,
    combo_account,
    date_widget,
    lbl_total,
    lbl_paid,
    lbl_rest,
    lbl_vat=None,
    vat_rate=0.20
):
    """
    Extract data from daily_entry widgets and Database, then format 
    it as a dictionary suitable for Jinja PDF generation.
    """
    data = {
        **to_invoice_context(load_company_info()),
        "invoice_no": "",
    }

    # 1. Extract Date
    if isinstance(date_widget, QDateEdit):
        data["date_label"] = "التاريخ"
        data["date"] = date_widget.date().toString("dd/MM/yyyy")
    else:
        data["date_label"] = "التاريخ"
        data["date"] = ""

    # 2. Extract Client & Account Info
    client_combo_text = combo_client.currentText() if isinstance(combo_client, QComboBox) else str(combo_client)
    customer_name = input_name.text() if hasattr(input_name, 'text') else str(input_name)
    account_name = combo_account.currentText() if isinstance(combo_account, QComboBox) else str(combo_account)
    
    data["client_name"] = customer_name if customer_name else "غير محدد"
    data["account_name"] = account_name if account_name and account_name != "-- اختر الحساب --" else "غير محدد"

    # 3. Extract Table Items (only cols 0-4)
    items = []
    if isinstance(table, QTableWidget):
        for row in range(table.rowCount()):
            date_val = data["date"]
            desc_val = table.item(row, 0).text() if table.item(row, 0) else ""
            qty_val = table.item(row, 1).text() if table.item(row, 1) else "1"
            
            # Amount
            amt_str = table.item(row, 2).text() if table.item(row, 2) else "0"
            amt_str = amt_str.replace(',', '')
            try:
                amount = float(amt_str)
            except ValueError:
                amount = 0.0
                
            # Paid
            paid_str = table.item(row, 3).text() if table.item(row, 3) else "0"
            paid_str = paid_str.replace(',', '')
            try:
                paid = float(paid_str)
            except ValueError:
                paid = 0.0
                
            # Remaining
            rem_str = table.item(row, 4).text() if table.item(row, 4) else "0"
            rem_str = rem_str.replace(',', '')
            try:
                remaining = float(rem_str)
            except ValueError:
                remaining = 0.0

            items.append({
                "date": date_val,
                "description": desc_val,
                "qty": qty_val,
                "amount": amount,
                "paid": paid,
                "remaining": remaining
            })
    data["items"] = items

    # 4. Extract Totals
    def parse_label(lbl):
        text = lbl.text() if hasattr(lbl, 'text') else str(lbl)
        text = text.replace(',', '')
        try:
            return float(text)
        except ValueError:
            return 0.0
            
    data["total_amount"] = parse_label(lbl_total)
    data["total_paid"] = parse_label(lbl_paid)

    # VAT can come from a dedicated label in the UI, otherwise it's derived from total.
    try:
        safe_vat_rate = float(vat_rate)
    except (TypeError, ValueError):
        safe_vat_rate = 0.20

    if safe_vat_rate < 0:
        safe_vat_rate = 0.0

    if lbl_vat is not None:
        data["total_vat"] = parse_label(lbl_vat)
    else:
        data["total_vat"] = round(data["total_amount"] * safe_vat_rate, 2)

    data["vat_rate"] = safe_vat_rate
    data["balance"] = data["total_amount"] + data["total_vat"] - data["total_paid"]

    return data


def generate_daily_invoice(data, invoice_number=None):
    """Generate daily PDF invoice and open it with the default system viewer."""
    # Get absolute path to current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader(current_dir))
    
    try:
        template = env.get_template('daily_invoice.html')
        
        # Add print date if not provided
        if 'print_date' not in data:
            data['print_date'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        if invoice_number:
            data['invoice_no'] = invoice_number
    
        # Render HTML with data
        html_out = template.render(data)
        
        # Convert HTML to PDF with external CSS
        file_name = f"{data.get('invoice_no') or 'daily_entry'}_facture.pdf"
        pdf_path = os.path.join(current_dir, file_name)
        HTML(string=html_out, base_url=current_dir).write_pdf(
            pdf_path,
            stylesheets=[CSS(os.path.join(current_dir, 'style.css'))]
        )
        open_pdf_file(pdf_path)
        logger.info("Daily invoice generated: %s", pdf_path)
        return pdf_path
    except Exception:
        logger.exception("Daily invoice generation failed")
        return None

