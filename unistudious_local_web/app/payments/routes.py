# app/payments/routes.py
from csv import excel_tab

from flask import Blueprint, render_template,request, jsonify, session, redirect, url_for,send_file
from app.payments.service import(
	get_paymet_session_service,
	update_payment_service,
	get_payment_user_info_service,
	update_payment_user_service,
	fetch_invoices_payment_service,
	fetch_invoice_by_id_service

)

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/api/get_payment_session/<int:session_id>', methods=['GET'])
def get_payment_session(session_id):
	try:
		status,response = get_paymet_session_service(session_id)
		if status:
			return jsonify(response),200
		else:
			return jsonify(response),400

	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		}),500

@payment_bp.route('/api/get_payment_user_info_service/<int:session_id>/<int:user_id>')
def get_payment_user_info(session_id,user_id):
	try:
		status,response = get_payment_user_info_service(user_id,session_id)
		print(response)
		if status :
			return jsonify(response),200
		else:
			return jsonify(response),400
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from server"
		})

@payment_bp.route('/api/update_payment_session/<int:payment_session>',methods=['POST'])
def update_payment_session(payment_session):
	try:
		data = request.get_json()
		status,response = update_payment_service(payment_session,data)
		if status:
			return jsonify(response),200
		else:
			return jsonify(response),400
	except Exception as e:
		return jsonify({"Message": f"Error {e} coming from backend"}), 500

@payment_bp.route('/api/update_payment_session_user/<int:payment_id>/<int:session_id>/<int:user_id>',methods=['POST'])
def update_payment_user(payment_id,session_id,user_id):
	try:
		data = request.get_json()
		status,response = update_payment_user_service(payment_id,session_id,user_id,data)
		print("status coming from the server: ",status)
		print("response coming from the server: ",response)
		return jsonify({
			"Message":data
		})
	except Exception as e:
		print(f"Error: {e} coming from update_payment_user")
		return jsonify({
			"Message":f"Error: {e} coming from update_payment_user"
		}),500


#====================================== Invoices payment ======================================
@payment_bp.route('/api/get_all_invoice_session/<int:account_id>',methods=['GET'])
def get_all_invoice_session(account_id):
	try:
		status,response = fetch_invoices_payment_service(account_id)
		return jsonify(response.json()),response.status_code
	except Exception as e:
		return jsonify({
			"Message":f"Error: {e} coming from backend"
		})

@payment_bp.route('/api/get_invoice_by_id/<int:invoice_id>/<int:account_id>/<int:admin_user_id>', methods=['GET'])
def get_invoice_by_id(invoice_id, account_id, admin_user_id):
    try:
        status, response = fetch_invoice_by_id_service(invoice_id, account_id, admin_user_id)
        if not status or response is None:
            return jsonify({"Message": "Invoice not found"}), 404
        return jsonify(response.json()), response.status_code  # ✅ fixed
    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from backend"})

@payment_bp.route('/api/download_invoice/<int:invoice_id>', methods=['GET'])
def download_invoice(invoice_id):
    try:
        from app.utils.generate_invoice_pdf import generate_invoice_pdf
        import io

        account_id    = session.get('account_id')
        admin_user_id = session.get('user_id')

        if not account_id or not admin_user_id:
            return jsonify({"Message": "Unauthorized"}), 401

        status, response = fetch_invoice_by_id_service(invoice_id, account_id, admin_user_id)

        if not status or response is None:
            return jsonify({"Message": "Invoice not found"}), 404

        row = response.json()

        invoice = {
            "invoice_number": row["id"],
            "created_at":     row["created_at"],
            "from_name":      row.get("academy_name",    ""),
            "from_address":   row.get("academy_address", ""),
            "from_phone":     row.get("agent_phone",     ""),
            "from_email":     row.get("agent_email",     ""),
            "to_name":        row.get("student_name",    ""),
            "to_address":     row.get("student_address", ""),
            "to_phone":       row.get("student_phone",   ""),
            "to_email":       row.get("student_email",   ""),
            "order_id":       row["payment_session_id"],
            "order_type":     row["type"],
            "description":    row["description"],
            "status":         "Paid" if row["is_status"] else "Unpaid",
            "price":          row["total_amount"],
            "total_amount":   row["total_amount"],
            "agent_name":     row.get("agent_name",  ""),
            "agent_phone":    row.get("agent_phone", ""),
            "agent_email":    row.get("agent_email", ""),
        }

        pdf_bytes = generate_invoice_pdf(invoice)

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"invoice_{invoice_id}.pdf"
        )

    except Exception as e:
        return jsonify({"Message": f"Error: {e} coming from backend"}), 500