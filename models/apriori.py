"""
Apriori Association Rules for NearShop Product Recommendations
Finds products frequently bought together.
"""
import os
import pickle
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

RULES_PATH = os.path.join(os.path.dirname(__file__), 'apriori_rules.pkl')
DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataset', 'transactions.csv')

# Fallback hardcoded rules for Indian retail
FALLBACK_RULES = {
    'puncture kit': [('Tyre Lever', 0.85), ('Valve Cap', 0.75), ('Cycle Tube', 0.70)],
    'bike chain': [('Chain Lubricant', 0.90), ('Sprocket', 0.80), ('Chain Cover', 0.65)],
    'spark plug': [('Engine Oil', 0.82), ('Air Filter', 0.75), ('Fuel Filter', 0.65)],
    'engine oil': [('Oil Filter', 0.88), ('Funnel', 0.60), ('Spark Plug', 0.70)],
    'led bulb': [('LED Strip', 0.72), ('Switch', 0.68), ('Wire', 0.60)],
    'wire': [('Switch', 0.85), ('Socket', 0.80), ('MCB', 0.70)],
    'pvc pipe': [('Elbow Joint', 0.88), ('Gate Valve', 0.75), ('Thread Tape', 0.72), ('Solvent Cement', 0.82)],
    'cpvc pipe': [('CPVC Elbow', 0.90), ('CPVC Solvent Cement', 0.88), ('Brass MTA', 0.75)],
    'water tap': [('Teflon Thread Tape', 0.92), ('Angle Valve', 0.84), ('Connection Pipe', 0.76)],
    'bib tap': [('Teflon Thread Tape', 0.90), ('Wall Flange', 0.80)],
    'health faucet': [('Angle Valve', 0.88), ('Flexible Hose', 0.85), ('Teflon Tape', 0.75)],
    'water tank': [('Float Valve / Ball Cock', 0.90), ('Tank Nipple', 0.85), ('Gate Valve', 0.80)],
    'angle valve': [('Geyser Connection Pipe', 0.85), ('Teflon Tape', 0.80)],
    'wash basin': [('Pillar Tap', 0.88), ('Waste Coupling', 0.85), ('Waste Pipe', 0.82)],
    'flush tank': [('Ball Cock', 0.80), ('Inlet Connection Pipe', 0.78)],
    'notebook': [('Pen', 0.92), ('Pencil', 0.80), ('Eraser', 0.75)],
    'pen': [('Notebook', 0.90), ('Pencil', 0.75), ('Ruler', 0.60)],
    'running shoe': [('Sports Socks', 0.85), ('Insole', 0.70), ('Shoe Lace', 0.65)],
    'school shoe': [('White Socks', 0.88), ('Shoe Polish', 0.75), ('Shoe Brush', 0.60)],
    'hammer': [('Nails', 0.90), ('Drill Bit', 0.65), ('Screws', 0.72)],
    'brake pad': [('Brake Shoe', 0.80), ('Brake Oil', 0.75), ('Brake Wire', 0.65)],
    'air filter': [('Spark Plug', 0.78), ('Engine Oil', 0.72), ('Fuel Filter', 0.68)],
    'shampoo': [('Conditioner', 0.80), ('Hair Oil', 0.72), ('Soap', 0.65)],
}


def train_model():
    """Train Apriori model from transactions CSV."""
    if not os.path.exists(DATASET_PATH):
        print('transactions.csv not found, using fallback rules.')
        return None
    
    try:
        df = pd.read_csv(DATASET_PATH)
        transactions = []
        for _, row in df.iterrows():
            items = [item.strip().lower() for item in str(row['items']).split(',')]
            transactions.append(items)
        
        te = TransactionEncoder()
        te_array = te.fit_transform(transactions)
        df_encoded = pd.DataFrame(te_array, columns=te.columns_)
        
        frequent_itemsets = apriori(df_encoded, min_support=0.02, use_colnames=True)
        if frequent_itemsets.empty:
            print('No frequent itemsets found, using fallback.')
            return None
        
        rules = association_rules(frequent_itemsets, metric='confidence', min_threshold=0.3)
        
        with open(RULES_PATH, 'wb') as f:
            pickle.dump(rules, f)
        
        print(f'Apriori rules saved: {len(rules)} rules')
        return rules
    except Exception as e:
        print(f'Apriori training error: {e}')
        return None


def load_rules():
    """Load rules from disk."""
    if os.path.exists(RULES_PATH):
        with open(RULES_PATH, 'rb') as f:
            return pickle.load(f)
    return None


def get_recommendations(product_name: str, n: int = 4) -> list:
    """
    Returns recommended products for a given product.
    
    Returns:
        list of dicts: [{product, confidence}]
    """
    name_lower = product_name.lower()
    
    # Try trained model first
    rules = load_rules()
    if rules is not None and not rules.empty:
        recs = []
        for _, row in rules.iterrows():
            antecedents = [a.lower() for a in row['antecedents']]
            if any(name_lower in ant or ant in name_lower for ant in antecedents):
                for prod in row['consequents']:
                    recs.append({'product': prod.title(), 'confidence': round(float(row['confidence']), 2)})
        recs = sorted(recs, key=lambda x: -x['confidence'])[:n]
        if recs:
            return recs
    
    # Fallback to hardcoded rules
    for key, items in FALLBACK_RULES.items():
        if key in name_lower or name_lower in key:
            return [{'product': p, 'confidence': round(c, 2)} for p, c in items[:n]]
    
    # Generic fallback
    return [
        {'product': 'Related Item 1', 'confidence': 0.65},
        {'product': 'Related Item 2', 'confidence': 0.55},
    ]


if __name__ == '__main__':
    train_model()
    print('Recommendations for puncture kit:', get_recommendations('puncture kit'))
    print('Recommendations for notebook:', get_recommendations('notebook'))
