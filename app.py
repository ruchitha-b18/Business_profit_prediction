import os
import sqlite3
from datetime import datetime
import pandas as pd
import numpy as np
import joblib
import io
import csv
import json
from flask import Flask, render_template, request, jsonify, send_file, Response, redirect, url_for
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
DB_NAME = 'database.db'

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rd_spend REAL,
            administration REAL,
            marketing_spend REAL,
            state TEXT,
            profit REAL,
            prediction_date TEXT,
            model_used TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Load Models (handling case where they might not exist yet)
MODEL_PATH = 'model/profit_model.pkl'
LE_PATH = 'model/label_encoder.pkl'

try:
    if os.path.exists(MODEL_PATH) and os.path.exists(LE_PATH):
        model = joblib.load(MODEL_PATH)
        le = joblib.load(LE_PATH)
        MODEL_NAME = type(model).__name__
    else:
        model, le, MODEL_NAME = None, None, "None (Model not trained)"
except Exception as e:
    print(f"Error loading models: {e}")
    model, le, MODEL_NAME = None, None, "Error"

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if model is None or le is None:
        return render_template('result.html', error="Model not trained. Please run train_model.py first.")

    try:
        # Get data from form
        rd_spend = float(request.form['rd_spend'])
        admin = float(request.form['administration'])
        marketing = float(request.form['marketing_spend'])
        state = request.form['state']
        
        # Validation for positive numbers is done on frontend, but double check here
        if rd_spend < 0 or admin < 0 or marketing < 0:
            return render_template('result.html', error="Values cannot be negative.")

        # Encode state
        state_encoded = le.transform([state])[0]

        # Predict
        prediction = model.predict([[rd_spend, admin, marketing, state_encoded]])[0]
        prediction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save to database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO predictions (rd_spend, administration, marketing_spend, state, profit, prediction_date, model_used)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (rd_spend, admin, marketing, state, prediction, prediction_date, MODEL_NAME))
        conn.commit()
        conn.close()

        return redirect(url_for('dashboard'))
    except Exception as e:
        return render_template('result.html', error=str(e))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/dashboard_data')
def api_dashboard_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM predictions", conn)
    conn.close()

    if df.empty:
        return jsonify({"status": "empty"})

    total_predictions = len(df)
    highest_profit = df['profit'].max()
    lowest_profit = df['profit'].min()
    average_profit = df['profit'].mean()

    # Data for profit distribution
    profit_data = df['profit'].tolist()

    # Actual vs Predicted logic is trickier since we only have predicted here.
    # We will just show history of predicted profits for the chart.
    history_dates = df['prediction_date'].apply(lambda x: x.split(' ')[0]).tolist()
    
    # Load Feature Importance
    feature_importance = None
    if os.path.exists('model/feature_importance.json'):
        with open('model/feature_importance.json', 'r') as f:
            feature_importance = json.load(f)
            
    # Load Actual vs Predicted
    actual_vs_predicted = None
    if os.path.exists('model/actual_vs_predicted.json'):
        with open('model/actual_vs_predicted.json', 'r') as f:
            actual_vs_predicted = json.load(f)
            
    # Compute Correlation Matrix
    correlation_matrix = None
    if os.path.exists('dataset/50_Startups.csv'):
        dataset_df = pd.read_csv('dataset/50_Startups.csv')
        # Only numeric columns
        numeric_df = dataset_df.select_dtypes(include=['number'])
        corr = numeric_df.corr().round(2)
        correlation_matrix = {
            'labels': corr.columns.tolist(),
            'values': corr.values.tolist()
        }
    
    return jsonify({
        "status": "success",
        "total_predictions": total_predictions,
        "highest_profit": round(highest_profit, 2),
        "lowest_profit": round(lowest_profit, 2),
        "average_profit": round(average_profit, 2),
        "profit_data": profit_data,
        "history_dates": history_dates,
        "feature_importance": feature_importance,
        "actual_vs_predicted": actual_vs_predicted,
        "correlation": correlation_matrix
    })

@app.route('/history')
def history():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM predictions ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return render_template('history.html', history=rows)

@app.route('/export_csv')
def export_csv():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM predictions", conn)
    conn.close()
    
    output = io.StringIO()
    df.to_csv(output, index=False)
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=prediction_history.csv"}
    )

@app.route('/export_pdf')
def export_pdf():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT rd_spend, administration, marketing_spend, state, profit, prediction_date FROM predictions ORDER BY id DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    elements.append(Paragraph("Business Profit Prediction Report", styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Table headers
    data = [["R&D Spend", "Admin", "Marketing", "State", "Profit", "Date"]]
    for row in rows:
        data.append([
            f"${row[0]:,.2f}", 
            f"${row[1]:,.2f}", 
            f"${row[2]:,.2f}", 
            row[3], 
            f"${row[4]:,.2f}", 
            row[5].split(' ')[0]
        ])

    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ])
    table.setStyle(style)
    elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name='prediction_report.pdf',
        mimetype='application/pdf'
    )

@app.route('/batch_predict', methods=['POST'])
def batch_predict():
    if model is None or le is None:
        return render_template('result.html', error="Model not trained. Please run train_model.py first.")
        
    if 'file' not in request.files:
        return render_template('result.html', error="No file part in the request.")
        
    file = request.files['file']
    if file.filename == '':
        return render_template('result.html', error="No selected file.")
        
    if file and file.filename.endswith('.csv'):
        try:
            df = pd.read_csv(file.stream)
            required_cols = ['R&D Spend', 'Administration', 'Marketing Spend', 'State']
            
            # Check if all required columns exist
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                return render_template('result.html', error=f"CSV missing columns: {', '.join(missing_cols)}")
                
            # Encode states, catching unseen labels
            try:
                states_encoded = le.transform(df['State'])
            except ValueError:
                return render_template('result.html', error=f"CSV contains unknown states. Allowed states: {', '.join(list(le.classes_))}")
                
            df_features = df[required_cols].copy()
            df_features['State'] = states_encoded
            
            # Predict
            features_array = df_features.values.astype(float)
            predictions = model.predict(features_array)
            df['Predicted Profit'] = np.round(predictions, 2)
            
            # Save batch to database
            prediction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            
            db_rows = []
            for index, row in df.iterrows():
                db_rows.append((
                    row['R&D Spend'], 
                    row['Administration'], 
                    row['Marketing Spend'], 
                    row['State'], 
                    row['Predicted Profit'], 
                    prediction_date, 
                    MODEL_NAME
                ))
                
            cursor.executemany('''
                INSERT INTO predictions (rd_spend, administration, marketing_spend, state, profit, prediction_date, model_used)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', db_rows)
            conn.commit()
            conn.close()
            
            return redirect(url_for('dashboard'))
        except Exception as e:
            return render_template('result.html', error=f"Error processing CSV: {str(e)}")
            
    return render_template('result.html', error="Invalid file format. Please upload a CSV.")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
