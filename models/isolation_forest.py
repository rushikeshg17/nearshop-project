"""
Isolation Forest Price Anomaly Detector for NearShop
Detects if a product is priced unusually high compared to nearby shops.
"""
import os
import sys
import pickle
import numpy as np
from sklearn.ensemble import IsolationForest

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'iforest_model.pkl')


def _generate_training_prices(n=1000):
    """Generate synthetic price data for training."""
    np.random.seed(42)
    # Normal prices
    normal_prices = np.random.normal(loc=500, scale=200, size=int(n * 0.9))
    # Anomalous prices (too high or too low)
    anomalous = np.random.uniform(2000, 5000, size=int(n * 0.1))
    prices = np.concatenate([normal_prices, anomalous])
    np.random.shuffle(prices)
    return prices.reshape(-1, 1)


def train_model():
    """Train and save Isolation Forest model."""
    X = _generate_training_prices()
    
    model = IsolationForest(
        n_estimators=100,
        contamination=0.1,
        random_state=42
    )
    model.fit(X)
    
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    
    print(f'Isolation Forest model saved to {MODEL_PATH}')
    return model


def load_model():
    """Load model from disk, train if not exists."""
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as f:
            return pickle.load(f)
    return train_model()


def check_price_anomaly(price: float, similar_prices: list) -> dict:
    """
    Check if a price is anomalous compared to similar products.
    
    Args:
        price: Price to check
        similar_prices: List of prices for the same product from other shops
    
    Returns:
        dict with: is_anomaly, avg_price, deviation_pct, message
    """
    if not similar_prices:
        return {
            'is_anomaly': False,
            'avg_price': price,
            'deviation_pct': 0,
            'message': ''
        }
    
    avg_price = np.mean(similar_prices)
    std_price = np.std(similar_prices) if len(similar_prices) > 1 else avg_price * 0.2
    deviation_pct = ((price - avg_price) / avg_price) * 100
    
    # Use Isolation Forest on the price relative to distribution
    all_prices = similar_prices + [price]
    model = load_model()
    
    # Normalize to model's scale
    scaled_price = np.array([[price]])
    prediction = model.predict(scaled_price)  # -1 = anomaly, 1 = normal
    
    # Also use simple threshold: > 25% above average
    is_high = deviation_pct > 25 or prediction[0] == -1
    
    if is_high and price > avg_price:
        return {
            'is_anomaly': True,
            'avg_price': round(avg_price, 2),
            'deviation_pct': round(deviation_pct, 1),
            'message': f'⚠️ This product is priced {round(deviation_pct, 1)}% higher than nearby shops.'
        }
    elif price < avg_price * 0.7:
        return {
            'is_anomaly': True,
            'avg_price': round(avg_price, 2),
            'deviation_pct': round(deviation_pct, 1),
            'message': f'✅ Great deal! This product is {abs(round(deviation_pct, 1))}% below average price.'
        }
    else:
        return {
            'is_anomaly': False,
            'avg_price': round(avg_price, 2),
            'deviation_pct': round(deviation_pct, 1),
            'message': ''
        }


def analyze_shop_prices(db_conn, product_name: str, shop_id: int, current_price: float) -> dict:
    """
    Fetch prices from DB and analyze anomaly.
    """
    cursor = db_conn.execute(
        '''SELECT p.price FROM products p
           JOIN shops s ON p.shop_id = s.id
           WHERE LOWER(p.product_name) LIKE ? AND p.shop_id != ?''',
        (f'%{product_name.lower()}%', shop_id)
    )
    prices = [row[0] for row in cursor.fetchall()]
    return check_price_anomaly(current_price, prices)


if __name__ == '__main__':
    train_model()
    result = check_price_anomaly(850, [400, 420, 390, 410, 430])
    print('Anomaly test:', result)
