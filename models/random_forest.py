"""
Random Forest Stock Depletion Predictor for NearShop
Predicts estimated days remaining before a product goes out of stock.
"""
import os
import pickle
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'rf_model.pkl')
SCALER_PATH = os.path.join(os.path.dirname(__file__), 'rf_scaler.pkl')


def _generate_training_data(n=2000):
    """Generate synthetic training data for stock depletion prediction."""
    np.random.seed(42)
    
    current_stock = np.random.randint(0, 500, n)
    search_freq = np.random.randint(1, 100, n)       # searches per day
    past_sales_rate = np.random.randint(1, 50, n)    # units sold per day
    month = np.random.randint(1, 13, n)
    season = np.array([1 if m in [10, 11, 12, 1] else 2 if m in [3, 4, 5] else 3 for m in month])  # 1=festive, 2=summer, 3=normal
    price = np.random.uniform(10, 5000, n)
    
    # Days remaining = stock / (sales_rate * season_factor)
    season_factor = np.where(season == 1, 1.5, np.where(season == 2, 1.2, 1.0))
    effective_rate = np.maximum(past_sales_rate * season_factor + search_freq * 0.1, 0.5)
    days_remaining = np.clip(current_stock / effective_rate, 0, 365)
    
    X = np.column_stack([current_stock, search_freq, past_sales_rate, month, season, price])
    y = days_remaining
    return X, y


def train_model():
    """Train and save the Random Forest model."""
    X, y = _generate_training_data()
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_scaled, y)
    
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    with open(SCALER_PATH, 'wb') as f:
        pickle.dump(scaler, f)
    
    print(f'Random Forest model saved to {MODEL_PATH}')
    return model, scaler


def load_model():
    """Load model from disk, train if not exists."""
    if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        with open(SCALER_PATH, 'rb') as f:
            scaler = pickle.load(f)
        return model, scaler
    return train_model()


def predict_stock_depletion(current_stock: int, search_freq: int,
                             past_sales_rate: int, month: int,
                             price: float) -> dict:
    """
    Predict days remaining before stockout.
    
    Returns:
        dict with keys: days_remaining (int), alert_level (str), message (str)
    """
    model, scaler = load_model()
    
    if month in [10, 11, 12, 1]:
        season = 1  # festive
    elif month in [3, 4, 5]:
        season = 2  # summer
    else:
        season = 3  # normal
    
    features = np.array([[current_stock, search_freq, past_sales_rate, month, season, price]])
    features_scaled = scaler.transform(features)
    days = float(model.predict(features_scaled)[0])
    days = max(0, round(days))
    
    if days <= 3:
        alert_level = 'critical'
        message = f'Critical: Only ~{days} days of stock remaining!'
        color = 'danger'
    elif days <= 10:
        alert_level = 'warning'
        message = f'Restock Soon: ~{days} days remaining.'
        color = 'warning'
    elif days <= 30:
        alert_level = 'caution'
        message = f'Monitor Stock: ~{days} days remaining.'
        color = 'info'
    else:
        alert_level = 'healthy'
        message = f'Stock Healthy: ~{days} days remaining.'
        color = 'success'
    
    return {
        'days_remaining': days,
        'alert_level': alert_level,
        'message': message,
        'color': color
    }


if __name__ == '__main__':
    train_model()
    result = predict_stock_depletion(50, 20, 5, 11, 250.0)
    print('Test prediction:', result)
