"""
startup.py — Run once before gunicorn starts on Render.
Initialises DB, seeds data, trains ML models if missing.
"""
import os

print("=" * 55)
print("  NearShop — Startup Script")
print("=" * 55)

# ── 1. Init DB + seed if empty ───────────────────────────────
from database.db import init_db, get_db
init_db()
conn = get_db()
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM users")
user_count = cur.fetchone()[0]

if user_count == 0:
    print("[startup] Empty DB detected — seeding data...")
    try:
        from seed_data import seed
        seed()
        print("[startup] Seed complete.")
    except Exception as e:
        print(f"[startup] Seed error: {e}")
else:
    print(f"[startup] DB already has {user_count} users — skipping seed.")

# ── 2. Train Word2Vec if model missing ───────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'word2vec.model')
if not os.path.exists(MODEL_PATH):
    print("[startup] Training Word2Vec model...")
    try:
        from models.word2vec import train_model
        train_model()
        print("[startup] Word2Vec trained.")
    except Exception as e:
        print(f"[startup] Word2Vec error: {e}")
else:
    print("[startup] Word2Vec model found — skipping training.")

print("[startup] Done! Starting Flask app...")
print("=" * 55)
