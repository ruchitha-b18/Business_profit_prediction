import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def train_and_evaluate():
    print("Starting Machine Learning Pipeline...")
    
    # 1. Load dataset
    dataset_path = 'dataset/50_Startups.csv'
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}")
        return
        
    df = pd.read_csv(dataset_path)
    print(f"Dataset loaded successfully. Shape: {df.shape}")
    
    # 2. Data Preprocessing
    # Remove missing values
    df.dropna(inplace=True)
    # Remove duplicates
    df.drop_duplicates(inplace=True)
    
    # Separate features and target
    X = df.iloc[:, :-1].values # All columns except last
    y = df.iloc[:, -1].values  # Last column (Profit)
    
    # Encode 'State' using LabelEncoder (State is the 4th column, index 3)
    le = LabelEncoder()
    X[:, 3] = le.fit_transform(X[:, 3])
    
    # Convert X to float
    X = np.array(X, dtype=float)
    
    # 3. Split into Train/Test (80/20)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. Initialize Models
    models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree Regressor": DecisionTreeRegressor(random_state=42),
        "Random Forest Regressor": RandomForestRegressor(n_estimators=100, random_state=42)
    }
    
    best_model_name = ""
    best_r2_score = -float('inf')
    best_model = None
    
    print("\nTraining and Evaluating Models...")
    print("-" * 50)
    
    # 5. Train and Evaluate
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        # Calculate Evaluation Metrics
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        
        print(f"Model: {name}")
        print(f"MAE: {mae:.2f}")
        print(f"MSE: {mse:.2f}")
        print(f"RMSE: {rmse:.2f}")
        print(f"R2 Score: {r2:.4f}")
        print("-" * 50)
        
        # Select best model based on R2 Score
        if r2 > best_r2_score:
            best_r2_score = r2
            best_model_name = name
            best_model = model

    print(f"\nBest Model Selected: {best_model_name} with R2 Score: {best_r2_score:.4f}")
    
    import json
    
    # 6. Save the model and label encoder
    os.makedirs('model', exist_ok=True)
    joblib.dump(best_model, 'model/profit_model.pkl')
    joblib.dump(le, 'model/label_encoder.pkl')
    
    # Extract Feature Importance
    feature_names = ['R&D Spend', 'Administration', 'Marketing Spend', 'State']
    if hasattr(best_model, 'feature_importances_'):
        importances = best_model.feature_importances_.tolist()
    elif hasattr(best_model, 'coef_'):
        importances = np.abs(best_model.coef_).tolist()
    else:
        importances = [0, 0, 0, 0]
        
    with open('model/feature_importance.json', 'w') as f:
        json.dump({'features': feature_names, 'importances': importances}, f)
        
    # Save Actual vs Predicted for the best model
    # We need to recalculate y_pred for the best model
    y_pred_best = best_model.predict(X_test)
    with open('model/actual_vs_predicted.json', 'w') as f:
        json.dump({'actual': y_test.tolist(), 'predicted': y_pred_best.tolist()}, f)
        
    print("Model, Label Encoder, and Chart Data saved in 'model' directory.")

if __name__ == "__main__":
    train_and_evaluate()
