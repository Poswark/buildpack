from flask import Flask, request, jsonify, session, redirect, url_for, render_template
from database import expenses_collection, month_collection, users_collection
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
import requests
import os
import datetime
import logging
from bson.objectid import ObjectId


app = Flask(__name__)


# Categorías y colores para el gráfico
CATEGORIES = ["Deuda", "Sofia", "Transporte", "Vivienda", "Entretenimiento", "Educación"]
COLORS = ["#AEDCC0", "#56B4D3", "#F4D06F", "#FF8A80", "#7DD3F0", "#FF5C8D"]

app.secret_key = os.getenv("FLASK_SECRET", "fallback-secret")
API_KEY = os.getenv("API_KEY")

# Middleware para proteger rutas
@app.before_request
def require_auth():
    public_routes = ['login', 'static']
    if request.endpoint not in public_routes and 'user' not in session:
        return redirect(url_for('login'))


# Ruta de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        api_key = request.form.get('api_key')

        user = users_collection.find_one({"email": email})

        if user and check_password_hash(user['password'], password) and api_key == API_KEY:
            session['user'] = email
            return redirect(url_for('index'))  # o la ruta que desees proteger
        else:
            return render_template('401.html'), 401

    return render_template('login.html')

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.get_json()
    user = data.get('user')
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email y contraseña son requeridos"}), 400

    # Verificar si ya existe
    if users_collection.find_one({"email": email}):
        return jsonify({"error": "El usuario ya existe"}), 409

    # Hashear contraseña
    hashed_password = generate_password_hash(password)

    # Insertar en la base de datos
    users_collection.insert_one({
        "user": user,
        "email": email,
        "password": hashed_password
    })

    return jsonify({"message": f"Usuario {email} creado exitosamente"}), 201

@app.route('/')
def index():
    today = datetime.datetime.now()
    month = request.args.get('month', today.month, type=int)
    year = request.args.get('year', today.year, type=int)

    start_date = datetime.datetime(year, month, 1)
    end_date = datetime.datetime(year + (month // 12), (month % 12) + 1, 1)

    expenses = list(expenses_collection.find({"date": {"$gte": start_date, "$lt": end_date}}))

    for expense in expenses:
        expense['_id'] = str(expense['_id'])
        expense['date'] = expense['date'].strftime('%Y-%m-%d')
        expense['created_at'] = expense['created_at'].strftime('%Y-%m-%d %H:%M:%S')

    category_totals = {category: 0 for category in CATEGORIES}
    for expense in expenses:
        if expense["category"] in category_totals:
            category_totals[expense["category"]] += expense["amount"]

    total_amount = sum(category_totals.values())
    chart_data = [
        {'category': category, 'amount': amount, 'percentage': round((amount / total_amount) * 100, 1) if total_amount else 0, 'color': COLORS[i]}
        for i, (category, amount) in enumerate(category_totals.items())
    ]

    month_name = start_date.strftime('%B %Y')
    prev_month, prev_year = (12, year - 1) if month == 1 else (month - 1, year)
    next_month, next_year = (1, year + 1) if month == 12 else (month + 1, year)

    return render_template('index.html', chart_data=chart_data, total_amount=total_amount, categories=CATEGORIES,
                           month_name=month_name, current_month=month, current_year=year,
                           prev_month=prev_month, prev_year=prev_year, next_month=next_month, next_year=next_year)

@app.route('/add_expense', methods=['POST'])
def add_expense():
    try:
        name = request.form.get('name')
        category = request.form.get('category')
        amount = float(request.form.get('amount'))
        date_str = request.form.get('date')

        date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        expense = {"name": name, "category": category, "amount": amount, "user": "poswark", "date": date, "created_at": datetime.datetime.now()}

        expenses_collection.insert_one(expense)

        return redirect(url_for('index', month=date.month, year=date.year))
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    
@app.route('/crearmeses', methods=['GET'])
def add_mount():
    try:
        month = { "January": 250000, "February": 3000000, "March": 4000000, "April":900000, "May":2000040, "June":63520000, "July":3183873, "August":89376974, "September":1718937, "October":1839873, "November":73648376, "December":237671286}
        month_collection.insert_one(month)
        
        return jsonify({"status": "Se Almaceno el demo en la BD" }), 200
    except Exception as e:
        return jsonify({"status": "error", "en almacenar": str(e)}), 500
    
    
@app.route('/generate_monthly_summary', methods=['GET'])
def generate_monthly_summary():
    try:
        # Obtener todos los gastos
        expenses = list(expenses_collection.find())

        monthly_summary = {}

        for expense in expenses:
            month_name = expense['date'].strftime('%B')  # Obtener nombre del mes
            if month_name not in monthly_summary:
                monthly_summary[month_name] = {category: 0 for category in CATEGORIES}  # Inicializar categorías

            category = expense['category']
            amount = expense['amount']

            if category in monthly_summary[month_name]:
                monthly_summary[month_name][category] += amount  # Sumar al total de la categoría

        # Calcular el total de cada mes
        for month, data in monthly_summary.items():
            data['total'] = sum(data.values())

        # Guardar o actualizar en la base de datos
        month_collection.update_one({}, {"$set": monthly_summary}, upsert=True)

        return jsonify({"status": "success", "message": "Monthly summary generated!", "data": monthly_summary}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/mes', methods=['GET'])
def view_mes():
    
    requests.get("http://localhost:5000/generate_monthly_summary")
    monthly_data = month_collection.find_one({}, {"_id": 0})
    
    if not monthly_data:
        logging.warning('"No data available')
        return render_template('error.html'), 500

    return render_template("mes.html", monthly_data={month: data['total'] for month, data in monthly_data.items()})

################# REPORTS

# Add this code to your existing Flask app (app.py)
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from database import reports_collection
import requests
import os
import datetime
import uuid
from bson.objectid import ObjectId
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Add this line to initialize the reports collection


# Add this route to view reports
@app.route('/reporte')
def view_report():
    report_id = request.args.get('id')
    
    try:
        if report_id:
            # Buscar por ID
            report = reports_collection.find_one({"_id": ObjectId(report_id)})
            if not report:
                return jsonify({"status": "error", "message": "Report not found"}), 404
        else:
            # Obtener el último reporte por fecha de creación
            report = reports_collection.find_one(sort=[("created_at", -1)])
            if not report:
                return jsonify({"status": "error", "message": "No reports found"}), 404

        # Asegúrate de convertir el ObjectId a string
        report['_id'] = str(report['_id'])

        return render_template("reporte.html", report=report)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/save_report', methods=['POST'])
def save_report():
    try:
        data = request.get_json()
        report_id = data.get('report_id')
        now = datetime.datetime.now()

        if report_id and report_id != 'null':
            existing_report = reports_collection.find_one({"_id": ObjectId(report_id)})
            if existing_report:
                update_data = {
                    "updated_at": now,
                    "business1": data.get("business1"),
                    "business2": data.get("business2"),
                }
                reports_collection.update_one(
                    {"_id": ObjectId(report_id)},
                    {"$set": update_data}
                )
                return jsonify({
                    "status": "success",
                    "message": "Report updated successfully",
                    "report_id": report_id
                })

        # Si no hay report_id, se crea un nuevo reporte
        new_report = {
            "date": now.strftime('%Y-%m-%d'),
            "user": "poswark",  # Esto podrías hacerlo dinámico si lo mandas desde Postman también
            "created_at": now,
            "business1": data.get("business1"),
            "business2": data.get("business2"),
            "business3": data.get("business3"),
            "business4": data.get("business4"),
        }

        inserted = reports_collection.insert_one(new_report)
        return jsonify({
            "status": "success",
            "message": "Report saved successfully",
            "report_id": str(inserted.inserted_id)
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
# Route to download a report as PDF
@app.route('/download_report/<report_id>', methods=['GET'])
def download_report(report_id):
    try:
        # Fetch the report
        report = reports_collection.find_one({"_id": ObjectId(report_id)})
        
        if not report:
            return jsonify({"status": "error", "message": "Report not found"}), 404
        
        # Create a PDF buffer
        buffer = io.BytesIO()
        
        # Create the PDF with reportlab
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Add PDF content
        p.setFont("Helvetica-Bold", 18)
        p.drawString(50, height - 50, "MiBilletera - Reporte de Negocios")
        
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 80, f"Fecha: {report.get('date', 'N/A')}")
        p.drawString(50, height - 100, f"Usuario: {report.get('user', 'N/A')}")
        p.drawString(50, height - 120, f"ID: {str(report['_id'])}")
        
        # Business 1
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, height - 160, "Negocio 1")
        
        p.setFont("Helvetica", 12)
        p.drawString(70, height - 190, f"I owe money: ${report['business1']['owe']}")
        p.drawString(70, height - 210, f"They owe me: ${report['business1']['owed']}")
        p.drawString(70, height - 230, f"Balance: ${report['business1']['balance']}")
        
        # Business 2
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, height - 280, "Negocio 2")
        
        p.setFont("Helvetica", 12)
        p.drawString(70, height - 310, f"I owe money: ${report['business2']['owe']}")
        p.drawString(70, height - 330, f"They owe me: ${report['business2']['owed']}")
        p.drawString(70, height - 350, f"Balance: ${report['business2']['balance']}")
        
        p.save()
        
        # Get the PDF data from the buffer
        buffer.seek(0)
        
        # Return the PDF as a downloadable file
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"reporte-negocio-{report_id}.pdf",
            mimetype="application/pdf"
        )
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Add this route to list all saved reports
@app.route('/reportes', methods=['GET'])
def list_reports():
    try:
        reports = list(reports_collection.find().sort("created_at", -1))
        
        # Convert ObjectId to string for JSON serialization
        for report in reports:
            report["_id"] = str(report["_id"])
            if "created_at" in report:
                report["created_at"] = report["created_at"].strftime('%Y-%m-%d %H:%M:%S')
            if "updated_at" in report:
                report["updated_at"] = report["updated_at"].strftime('%Y-%m-%d %H:%M:%S')
        
        return render_template("reportes_list.html", reports=reports)
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)