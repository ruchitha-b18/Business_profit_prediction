# Business Profit Prediction using Machine Learning

A professional, full-stack web application that predicts a startup's profit based on its investments using Machine Learning. Built for an NVIDIA AI/ML Capstone project, this application features a premium UI, dark mode, an interactive analytics dashboard, and export capabilities.

## Features

- **Machine Learning Pipeline**: Automatically trains and evaluates Linear Regression, Decision Tree, and Random Forest models, selecting the best one based on R² score.
- **Single & Batch Predictions**: Predict profit for a single startup via the UI or upload a CSV for batch processing.
- **Interactive Dashboard**: Visualizes prediction history and profit distribution using Chart.js.
- **Prediction History**: Tracks all predictions in a local SQLite database.
- **Export Options**: Download prediction history as CSV or PDF reports.
- **Premium UI/UX**: Built with Bootstrap 5, custom CSS (glassmorphism, gradients, animations), and dark mode toggle.

## Technology Stack

- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript, Chart.js, Font Awesome.
- **Backend**: Python, Flask, SQLite.
- **Machine Learning**: Pandas, NumPy, Scikit-learn, Joblib.
- **PDF Generation**: ReportLab.

## Setup Instructions

### 1. Prerequisites
Ensure you have Python 3.8+ installed on your system.

### 2. Install Dependencies
Navigate to the project directory and install the required packages:
```bash
pip install -r requirements.txt
```

### 3. Train the Machine Learning Model
Before running the web application, you must run the training script. This script loads the dataset, cleans it, trains multiple models, selects the best one, and saves it to the `model/` directory.
```bash
python train_model.py
```

### 4. Run the Web Application
Start the Flask development server:
```bash
python app.py
```
Open your web browser and navigate to `http://127.0.0.1:5000/`.

## Folder Structure

```
Business-Profit-Prediction/
│
├── app.py                  # Flask backend application
├── train_model.py          # Machine learning training pipeline
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── database.db             # SQLite database (auto-generated)
│
├── model/                  # Trained ML models and encoders
│   ├── profit_model.pkl
│   └── label_encoder.pkl
│
├── templates/              # HTML frontend templates
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   ├── dashboard.html
│   └── history.html
│
├── static/                 # Static assets
│   ├── css/style.css
│   └── js/script.js
│
└── dataset/                # Datasets
    └── 50_Startups.csv
```

## Usage

1. **Home Page**: Enter the R&D Spend, Administration Cost, Marketing Spend, and select the State. Click "Predict Profit".
2. **Batch Prediction**: On the home page, switch to the "Batch Prediction" tab and upload a CSV file with the required columns. It will download a new CSV with the predicted profits appended.
3. **Dashboard**: Navigate to the Dashboard to see analytics on past predictions.
4. **History**: View a table of all past predictions. Use the buttons on the top right to export the data as a CSV or PDF report.
5. **Theme**: Toggle Dark/Light mode using the icon in the navigation bar.
