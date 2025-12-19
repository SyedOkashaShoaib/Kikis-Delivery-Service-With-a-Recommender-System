# recommender/vectorizer.py

import numpy as np
from sqlalchemy import func
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime

from app import db
from app.models import Menu, TagCatalog, ItemTags, ItemFeatures

def load_tag_index():
    """Returns dictionary: tag_id → index in multi-hot vector."""
    tags = TagCatalog.query.order_by(TagCatalog.tag_id).all()
    return {tag.tag_id: i for i, tag in enumerate(tags)}, len(tags)

def compute_price_min_max():
    """Returns min and max price from DB."""
    prices = db.session.query(Menu.price).all()
    prices = [float(p[0]) for p in prices if p[0] is not None]
    return (min(prices), max(prices)) if prices else (0, 1)


def normalize_price(price, min_p, max_p):
    return (price - min_p) / (max_p - min_p + 1e-6)


def normalize_rating(r):
    return (r or 0) / 5.0

def compute_global_mean_rating():
    ratings = db.session.query(Menu.rating).all()
    ratings = [r[0] for r in ratings if r[0] is not None]
    return np.mean(ratings) if ratings else 3.0


def bayesian_rating(r, v, global_mean, m=20):
    """Bayesian averaging to avoid popularity dominance."""
    if r is None:
        return global_mean
    return (v / (v + m)) * r + (m / (v + m)) * global_mean

def get_tag_vector(item_id, tag_index, tag_count):
    vec = np.zeros(tag_count)
    tags = ItemTags.query.filter_by(item_id=item_id).all()
    for t in tags:
        if t.tag_id in tag_index:
            vec[tag_index[t.tag_id]] = 1
    return vec

def build_item_vector(menu_item, tag_index, tag_count, min_p, max_p, global_mean):

    tag_vec = get_tag_vector(menu_item.item_id, tag_index, tag_count)

    price_norm = normalize_price(float(menu_item.price), min_p, max_p)
    rating_norm = normalize_rating(menu_item.rating or 0)
    bayes_norm = bayesian_rating(menu_item.rating, menu_item.ratings_count or 0,
                                 global_mean) / 5.0

    return np.concatenate([
        tag_vec,
        np.array([price_norm, rating_norm, bayes_norm])
    ])

def save_item_vector(item_id, vec):
    """Stores feature vector in ItemFeatures table."""
    rec = ItemFeatures.query.filter_by(item_id=item_id).first()
    if rec is None:
        rec = ItemFeatures(item_id=item_id)

    rec.features_json = vec.tolist()
    rec.feature_version = (rec.feature_version or 0) + 1
    rec.computed_at = datetime.utcnow()

    db.session.add(rec)

def load_item_vector(item_id):

    rec = ItemFeatures.query.filter_by(item_id=item_id).first()
    if rec is None:
        return None
    return np.array(rec.features_json, dtype=float)


def load_all_item_vectors():

    rows = ItemFeatures.query.all()
    return {
        r.item_id: np.array(r.features_json, dtype=float)
        for r in rows
    }

def compute_all_item_vectors():
    """
    Loads all items, computes vectors, saves to DB.
    Returns dictionary: item_id → numpy vector
    """

    tag_index, tag_count = load_tag_index()
    min_p, max_p = compute_price_min_max()
    global_mean = compute_global_mean_rating()

    all_items = Menu.query.all()
    vectors = {}

    for item in all_items:
        vec = build_item_vector(item, tag_index, tag_count, min_p, max_p, global_mean)
        vectors[item.item_id] = vec
        save_item_vector(item.item_id, vec)

    db.session.commit()
    return vectors


def compute_item_similarity_matrix(vectors=None):
    if vectors is None:
        items = ItemFeatures.query.order_by(ItemFeatures.item_id).all()
        vectors = {i.item_id: np.array(i.features_json) for i in items}

    ids = list(vectors.keys())
    mat = cosine_similarity([vectors[i] for i in ids])

    similarity_dict = {}

    for i, id1 in enumerate(ids):
        sims = []
        for j, id2 in enumerate(ids):
            if id1 != id2:
                sims.append((id2, float(mat[i][j])))
        sims.sort(key=lambda x: x[1], reverse=True)
        similarity_dict[id1] = sims

    return similarity_dict

def recommend_similar_items(item_id, top_n=10, similarity_dict=None):
    if similarity_dict is None:
        # Load matrices from DB features
        similarity_dict = compute_item_similarity_matrix()

    return similarity_dict.get(item_id, [])[:top_n]

