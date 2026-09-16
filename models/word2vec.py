"""
Word2Vec Semantic Search Model for NearShop
Trains on Indian retail product corpus and finds semantically similar products.
"""
import os
import logging
from gensim.models import Word2Vec
from gensim.utils import simple_preprocess

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'word2vec.model')

# Large corpus of Indian retail product names and synonyms
CORPUS = [
    # Vehicle Spare Parts
    ['bike', 'chain', 'motorcycle', 'cycle', 'two', 'wheeler'],
    ['puncture', 'kit', 'repair', 'tyre', 'tube', 'flat'],
    ['spark', 'plug', 'iridium', 'engine', 'ignition'],
    ['engine', 'oil', 'lubricant', 'motor', 'mobil', 'castrol'],
    ['air', 'filter', 'cleaner', 'intake', 'carb'],
    ['disc', 'brake', 'pad', 'caliper', 'stopping'],
    ['clutch', 'cable', 'wire', 'plate', 'pressure'],
    ['accelerator', 'throttle', 'cable', 'twist', 'grip'],
    ['headlight', 'bulb', 'halogen', 'led', 'lamp'],
    ['indicator', 'turn', 'signal', 'blinker', 'light'],
    ['battery', 'terminal', 'clamp', 'connector', 'cable'],
    ['gear', 'oil', 'transmission', 'box', 'lubricant'],
    ['brake', 'shoe', 'drum', 'lining', 'pad'],
    ['fuel', 'filter', 'petrol', 'strainer', 'inline'],
    ['tyre', 'tube', 'inner', 'outer', 'rubber'],
    ['wheel', 'bearing', 'hub', 'axle', 'sealed'],
    ['piston', 'ring', 'cylinder', 'bore', 'sleeve'],
    ['valve', 'guide', 'stem', 'seat', 'spring'],
    ['drive', 'belt', 'timing', 'v-belt', 'pulley'],
    ['rear', 'shock', 'absorber', 'suspension', 'spring'],
    # Electrical
    ['mcb', 'miniature', 'circuit', 'breaker', 'switch', 'electrical'],
    ['wire', 'cable', 'copper', 'electrical', 'flex', 'house'],
    ['switch', 'socket', 'modular', 'plate', 'electrical'],
    ['led', 'bulb', 'light', 'lamp', 'energy', 'saving'],
    ['tube', 'light', 'fluorescent', 'cfl', 'fitting'],
    ['inverter', 'battery', 'ups', 'power', 'backup'],
    ['fan', 'capacitor', 'ceiling', 'exhaust', 'motor'],
    ['voltage', 'stabilizer', 'regulator', 'servo'],
    ['extension', 'board', 'multiplug', 'socket', 'strip'],
    # Hardware
    ['hammer', 'claw', 'rubber', 'mallet', 'tool'],
    ['nails', 'screw', 'bolt', 'nut', 'fastener'],
    ['drill', 'bit', 'wood', 'metal', 'masonry'],
    ['hacksaw', 'blade', 'cut', 'metal', 'hand'],
    ['measuring', 'tape', 'scale', 'ruler', 'length'],
    ['pliers', 'grip', 'nose', 'combination', 'tool'],
    ['wrench', 'spanner', 'adjustable', 'torque', 'tool'],
    # Footwear
    ['chappal', 'sandal', 'slipper', 'hawai', 'rubber'],
    ['sports', 'shoes', 'running', 'canvas', 'sneaker'],
    ['school', 'shoes', 'black', 'leather', 'formal'],
    ['gumboots', 'rubber', 'boots', 'rain', 'waterproof'],
    # Stationery
    ['notebook', 'register', 'ruled', 'writing', 'book'],
    ['pen', 'ball', 'point', 'gel', 'ink', 'writing'],
    ['pencil', 'hb', 'drawing', 'sketch', 'graphite'],
    ['compass', 'geometry', 'box', 'divider', 'set'],
    ['eraser', 'rubber', 'white', 'dust', 'free'],
    ['stapler', 'pins', 'binding', 'paper', 'office'],
    # Books
    ['maths', 'mathematics', 'textbook', 'sslc', 'puc', 'ncert'],
    ['physics', 'science', 'textbook', 'class', 'standard'],
    ['english', 'grammar', 'language', 'literature', 'guide'],
    ['competitive', 'exam', 'ias', 'ips', 'upsc', 'preparation'],
    # Footwear
    ['slipper', 'sandal', 'chappal', 'hawai', 'rubber', 'eva', 'sole'],
    ['shoes', 'running', 'sports', 'canvas', 'sneaker', 'school', 'formal'],
    ['leather', 'formal', 'oxford', 'lace', 'moccasin', 'loafer'],
    ['heel', 'pump', 'block', 'ladies', 'women', 'flat', 'wedge'],
    ['paragon', 'bata', 'liberty', 'action', 'woodland', 'relaxo', 'vkc'],
    # Plumbing
    ['pvc', 'pipe', 'water', 'supply', 'upvc', 'cpvc', 'pipeline'],
    ['elbow', 'tee', 'joint', 'coupling', 'fitting', 'connector', 'socket', 'adapter'],
    ['gate', 'valve', 'ball', 'water', 'flow', 'control', 'brass', 'zoloto'],
    ['water', 'tap', 'faucet', 'bib', 'cock', 'mixer', 'bathroom', 'kitchen', 'pillar'],
    ['angle', 'valve', 'stop', 'cock', 'geyser', 'connection', 'pipe', 'hose'],
    ['health', 'faucet', 'jet', 'spray', 'toilet', 'bidet', 'shower'],
    ['water', 'tank', 'overhead', 'storage', 'sintex', 'vectus', 'float', 'valve'],
    ['teflon', 'tape', 'thread', 'seal', 'mseal', 'solvent', 'cement', 'adhesive'],
    ['waste', 'pipe', 'drain', 'jali', 'coupling', 'sink', 'wash', 'basin', 'flush', 'tank'],
    # General Store
    ['rice', 'sona', 'masoori', 'basmati', 'grain'],
    ['sugar', 'white', 'refined', 'crystal', 'sweet'],
    ['soap', 'bath', 'hand', 'wash', 'detergent'],
    ['shampoo', 'hair', 'wash', 'conditioner', 'head'],
    ['toothpaste', 'gel', 'brush', 'dental', 'care'],
]


def train_model():
    """Train Word2Vec model on the corpus."""
    # Augment corpus with permutations
    augmented = []
    for sentence in CORPUS:
        augmented.append(sentence)
        augmented.append(sentence[::-1])
        if len(sentence) > 2:
            augmented.append(sentence[1:])
    
    model = Word2Vec(
        sentences=augmented,
        vector_size=100,
        window=5,
        min_count=1,
        workers=4,
        epochs=50,
        sg=1  # Skip-gram
    )
    model.save(MODEL_PATH)
    print(f'Word2Vec model saved to {MODEL_PATH}')
    return model


_MODEL = None


def load_model():
    """Load model from disk or cache, train if not exists."""
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    if os.path.exists(MODEL_PATH):
        try:
            _MODEL = Word2Vec.load(MODEL_PATH)
            return _MODEL
        except Exception as e:
            print(f"Error loading Word2Vec: {e}")
    _MODEL = train_model()
    return _MODEL


def get_similar_terms(query: str, topn: int = 10) -> list:
    """
    Returns semantically similar terms for the given query.
    Used to expand search queries.
    """
    model = load_model()
    if model is None or not hasattr(model, 'wv'):
        return query.lower().split()
    tokens = simple_preprocess(query)
    similar_terms = set(tokens)
    
    for token in tokens:
        if token in model.wv:
            similars = model.wv.most_similar(token, topn=topn)
            for word, score in similars:
                if score > 0.5:
                    similar_terms.add(word)
    
    return list(similar_terms)


def get_query_expansion(query: str) -> list:
    """
    Returns expanded query terms for database LIKE search.
    """
    terms = get_similar_terms(query, topn=5)
    # Add original query words
    original = simple_preprocess(query)
    terms.extend(original)
    return list(set(terms))


if __name__ == '__main__':
    model = train_model()
    print('Testing: bike chain ->', get_similar_terms('bike chain'))
    print('Testing: puncture kit ->', get_similar_terms('puncture kit'))
