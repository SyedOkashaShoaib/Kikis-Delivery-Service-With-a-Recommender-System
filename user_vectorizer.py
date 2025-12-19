import numpy as np
from collections import defaultdict

from app import db
from app.models import Order, Order_Items
from app.vectorizer import load_all_item_vectors, compute_item_similarity_matrix  # reuse item vectors

def compute_all_user_vectors():
    """
    Builds user vectors from delivered orders.
    Returns dict[user_id] -> normalized numpy vector
    """

    item_vectors = load_all_item_vectors()
    if not item_vectors:
        return {}

    vec_dim = len(next(iter(item_vectors.values())))
    user_vectors = defaultdict(lambda: np.zeros(vec_dim))

    delivered_orders = Order.query.filter(
        Order.order_status == "DELIVERED"
    ).all()

    for order in delivered_orders:
        uid = order.customer_id

        for oi in order.order_items:
            item_vec = item_vectors.get(oi.item_id)
            if item_vec is None:
                continue

            user_vectors[uid] += item_vec * oi.quantity

    # Normalize vectors
    for uid in user_vectors:
        norm = np.linalg.norm(user_vectors[uid])
        if norm > 0:
            user_vectors[uid] /= norm

    return dict(user_vectors)

def compute_user_similarity(user_vectors):
    similarity = {}
    users = list(user_vectors.keys())

    for i, u1 in enumerate(users):
        similarity[u1] = []
        for j, u2 in enumerate(users):
            if i == j:
                continue
            sim = float(np.dot(user_vectors[u1], user_vectors[u2]))
            similarity[u1].append((u2, sim))

        similarity[u1].sort(key=lambda x: x[1], reverse=True)

    return similarity

def get_similar_users(target_user_id, user_vectors, top_k=5):
    if target_user_id not in user_vectors:
        return []

    target_vec = user_vectors[target_user_id]
    sims = []

    for uid, vec in user_vectors.items():
        if uid == target_user_id:
            continue
        sim = float(np.dot(target_vec, vec))
        sims.append((uid, sim))

    sims.sort(key=lambda x: x[1], reverse=True)
    return sims[:top_k]

def recommend_from_similar_users(user_id, user_vectors, top_k=10):
    similar_users = get_similar_users(user_id, user_vectors)

    seen_items = set(
        o.menu_id for o in Order.query.filter_by(user_id=user_id).all()
    )

    scores = defaultdict(float)

    for sim_user_id, weight in similar_users:
        orders = Order.query.filter_by(user_id=sim_user_id).all()
        for o in orders:
            if o.menu_id not in seen_items:
                scores[o.menu_id] += weight

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [menu_id for menu_id, _ in ranked[:top_k]]

def recommend_items_for_user(user_id, user_vectors, top_n=10):
    """
    Recommends items not yet ordered by the user
    """

    item_vectors = load_all_item_vectors()
    user_vec = user_vectors.get(user_id)

    if user_vec is None:
        return []

    # Items already ordered by user
    seen_items = set()

    past_orders = Order.query.filter(
        Order.customer_id == user_id,
        Order.order_status == "DELIVERED"
    ).all()

    for order in past_orders:
        for oi in order.order_items:
            seen_items.add(oi.item_id)

    scores = {}
    for item_id, item_vec in item_vectors.items():
        if item_id in seen_items:
            continue
        scores[item_id] = float(np.dot(user_vec, item_vec))

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]

def recommend_items_hybrid(user_id, user_vectors, item_vectors, similarity_dict=None, top_n=5):
    
    if similarity_dict is None:
        similarity_dict = compute_item_similarity_matrix(item_vectors)

    user_vec = user_vectors.get(user_id)
    if user_vec is None:
        return []

    orders = Order.query.filter(
        Order.customer_id == user_id,
        Order.order_status == "DELIVERED"
    ).all()

    if not orders:
        return []

    seen_items = set()
    for o in orders:
        for oi in o.order_items:
            seen_items.add(oi.item_id)

    user_evidence = len(seen_items)
    item_evidence = sum(len(similarity_dict.get(i, [])) for i in seen_items)

    total_evidence = user_evidence + item_evidence + 1e-6
    w_user = user_evidence / total_evidence
    w_item = item_evidence / total_evidence

    scores = {}

    for item_id, item_vec in item_vectors.items():
        if item_id in seen_items:
            continue

        # User-based score
        user_score = float(np.dot(user_vec, item_vec))

        # Item-based score
        item_score = 0.0
        count = 0
        for seen in seen_items:
            for sim_item, sim_val in similarity_dict.get(seen, []):
                if sim_item == item_id:
                    item_score += sim_val
                    count += 1

        if count > 0:
            item_score /= count

        # Hybrid score
        final_score = (w_user * user_score) + (w_item * item_score)
        scores[item_id] = final_score

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]

def recommend_cart_complements(user_id, cart_item_ids, user_vectors, item_vectors, item_similarity, top_n=5):

    user_vec = user_vectors.get(user_id)
    if user_vec is None or not cart_item_ids:
        return []

    past_orders = Order.query.filter(
        Order.order_status == "DELIVERED"
    ).all()

    cart_counts = defaultdict(int)
    joint_counts = defaultdict(int)

    for order in past_orders:
        order_items = {oi.item_id for oi in order.order_items}

        for c in cart_item_ids:
            if c in order_items:
                cart_counts[c] += 1
                for j in order_items:
                    if j not in cart_item_ids:
                        joint_counts[(c, j)] += 1

    scores = {}

    for item_id, item_vec in item_vectors.items():
        if item_id in cart_item_ids:
            continue

        co_score = 0.0
        evidence = 0

        for c in cart_item_ids:
            if cart_counts[c] > 0:
                co_score += joint_counts.get((c, item_id), 0) / cart_counts[c]
                evidence += 1

        if evidence > 0:
            co_score /= evidence

        user_score = float(np.dot(user_vec, item_vec))

        sim_score = 0.0
        sim_count = 0
        for c in cart_item_ids:
            for sim_item, sim_val in item_similarity.get(c, []):
                if sim_item == item_id:
                    sim_score += sim_val
                    sim_count += 1

        if sim_count > 0:
            sim_score /= sim_count

        w_co = min(0.6, 0.2 + 0.1 * len(cart_item_ids))
        w_user = 0.3
        w_sim = 1.0 - (w_co + w_user)

        final_score = (
            w_co * co_score +
            w_user * user_score +
            w_sim * sim_score
        )

        scores[item_id] = final_score

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]
