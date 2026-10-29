import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Customer, Product, Purchase


def _product_text(product: Product) -> str:
    tags = " ".join(product.tags or [])
    return f"{product.name} {product.category} {product.description} {tags}"


def recommend_products(
    session: Session, customer_id: int, limit: int = 8
) -> list[dict[str, object]]:
    products = list(session.scalars(select(Product).order_by(Product.id)))
    if not products:
        return []

    purchases = list(session.scalars(select(Purchase)))
    product_ids = [product.id for product in products]
    product_index = {product_id: index for index, product_id in enumerate(product_ids)}

    interactions = pd.DataFrame(
        [
            {
                "customer_id": purchase.customer_id,
                "product_id": purchase.product_id,
                "quantity": purchase.quantity,
            }
            for purchase in purchases
        ],
        columns=["customer_id", "product_id", "quantity"],
    )
    customer_exists = session.get(Customer, customer_id) is not None
    purchased_ids = (
        set(interactions.loc[interactions.customer_id == customer_id, "product_id"])
        if not interactions.empty
        else set()
    )

    content_matrix = TfidfVectorizer(stop_words="english").fit_transform(
        [_product_text(product) for product in products]
    )
    product_similarities = cosine_similarity(content_matrix)
    content_scores = np.zeros(len(products))
    customer_interactions = interactions.loc[
        interactions.customer_id == customer_id
    ] if not interactions.empty else interactions
    if not customer_interactions.empty:
        profile_weights = np.zeros(len(products))
        for row in customer_interactions.itertuples(index=False):
            profile_weights[product_index[row.product_id]] += row.quantity
        content_scores = profile_weights @ product_similarities
        weight_total = profile_weights.sum()
        if weight_total > 0:
            content_scores /= weight_total

    collaborative_scores = np.zeros(len(products))
    if not interactions.empty:
        customer_ids = sorted(interactions.customer_id.unique().tolist())
        matrix = (
            interactions.pivot_table(
                index="customer_id",
                columns="product_id",
                values="quantity",
                aggfunc="sum",
                fill_value=0,
            )
            .reindex(index=customer_ids, columns=product_ids, fill_value=0)
            .to_numpy(dtype=float)
        )
        target_index = customer_ids.index(customer_id) if customer_id in customer_ids else None
        if target_index is not None and len(customer_ids) > 1:
            similarities = cosine_similarity(matrix)[target_index]
            similarities[target_index] = 0
            neighbor_scores = similarities @ matrix
            similarity_total = similarities.sum()
            if similarity_total > 0:
                collaborative_scores = neighbor_scores / similarity_total

    max_content = content_scores.max(initial=0)
    if max_content > 0:
        content_scores /= max_content
    max_collaborative = collaborative_scores.max(initial=0)
    if max_collaborative > 0:
        collaborative_scores /= max_collaborative

    popularity = np.zeros(len(products))
    for row in interactions.itertuples(index=False):
        popularity[product_index[row.product_id]] += row.quantity
    max_popularity = popularity.max(initial=0)
    if max_popularity > 0:
        popularity /= max_popularity

    ranked = []
    for index, product in enumerate(products):
        if product.id in purchased_ids:
            continue
        score = (
            0.45 * collaborative_scores[index]
            + 0.45 * content_scores[index]
            + 0.10 * popularity[index]
        )
        if not customer_exists:
            score = popularity[index]
        if customer_interactions.empty:
            reason = "Popular with shoppers and a great place to start."
        elif collaborative_scores[index] >= content_scores[index]:
            reason = "Chosen from patterns in what similar shoppers enjoy."
        else:
            reason = "Matches the categories and features in your purchase history."
        ranked.append(
            {
                "product": product,
                "score": round(float(score), 4),
                "reason": reason,
            }
        )

    ranked.sort(key=lambda result: result["score"], reverse=True)
    return ranked[:limit]
