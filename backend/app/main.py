from contextlib import asynccontextmanager

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import Customer, Product, Purchase
from app.recommender import recommend_products
from app.seed import seed_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_database(session)
    yield


app = FastAPI(title="Personalized Product Recommendations", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_session():
    with SessionLocal() as session:
        yield session


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    customer_id: int | None = None


class PurchaseRequest(BaseModel):
    customer_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    quantity: int = Field(default=1, gt=0, le=100)


class ChatResponse(BaseModel):
    reply: str


def product_data(product: Product) -> dict[str, object]:
    return {
        "id": product.id,
        "name": product.name,
        "category": product.category,
        "description": product.description,
        "price": product.price,
        "image_url": product.image_url,
        "tags": product.tags,
    }


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/products")
def get_products(session: Session = Depends(get_session)):
    products = session.scalars(select(Product).order_by(Product.name)).all()
    return [product_data(product) for product in products]


@app.get("/api/customers")
def get_customers(session: Session = Depends(get_session)):
    customers = session.scalars(select(Customer).order_by(Customer.name)).all()
    return [{"id": customer.id, "name": customer.name} for customer in customers]


@app.get("/api/recommendations")
def get_recommendations(
    customer_id: int = Query(gt=0),
    limit: int = Query(default=8, ge=1, le=24),
    session: Session = Depends(get_session),
):
    results = recommend_products(session, customer_id, limit)
    return [
        {
            **product_data(result["product"]),
            "score": result["score"],
            "reason": result["reason"],
        }
        for result in results
    ]


@app.get("/api/purchases/{customer_id}")
def get_purchases(customer_id: int, session: Session = Depends(get_session)):
    products = session.scalars(
        select(Product)
        .join(Purchase, Purchase.product_id == Product.id)
        .where(Purchase.customer_id == customer_id)
        .order_by(Product.name)
    ).all()
    return [product_data(product) for product in products]


@app.post("/api/purchases", status_code=status.HTTP_201_CREATED)
def create_purchase(
    request: PurchaseRequest, session: Session = Depends(get_session)
):
    if session.get(Customer, request.customer_id) is None:
        raise HTTPException(status_code=404, detail="Shopper not found.")
    if session.get(Product, request.product_id) is None:
        raise HTTPException(status_code=404, detail="Product not found.")

    purchase = Purchase(
        customer_id=request.customer_id,
        product_id=request.product_id,
        quantity=request.quantity,
    )
    session.add(purchase)
    session.commit()
    return {
        "id": purchase.id,
        "customer_id": purchase.customer_id,
        "product_id": purchase.product_id,
        "quantity": purchase.quantity,
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, session: Session = Depends(get_session)):
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=503,
            detail="Chatbot is not configured. Add GEMINI_API_KEY to backend/.env and restart the API.",
        )

    products = session.scalars(select(Product).order_by(Product.name)).all()
    customer_purchases = []
    if request.customer_id is not None:
        customer_purchases = session.scalars(
            select(Product)
            .join(Purchase, Purchase.product_id == Product.id)
            .where(Purchase.customer_id == request.customer_id)
        ).all()

    catalog = "\n".join(
        f"- {product.name} ({product.category}, ${product.price}): {product.description}"
        for product in products
    )
    purchase_context = ", ".join(product.name for product in customer_purchases) or "No purchase history"
    prompt = (
        "You are a helpful shopping assistant for a general product store. "
        "Recommend only products listed in the catalog, be concise, and do not invent prices or features. "
        f"\nCustomer purchase history: {purchase_context}\nCatalog:\n{catalog}"
        f"\n\nCustomer message: {request.message}"
    )
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent"
    )
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                url,
                params={"key": settings.gemini_api_key},
                json={"contents": [{"parts": [{"text": prompt}]}]},
            )
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="The chatbot request timed out.") from exc
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail="Could not reach the chatbot provider.") from exc

    if response.is_error:
        raise HTTPException(
            status_code=502,
            detail=f"Chatbot provider returned an error ({response.status_code}).",
        )

    data = response.json()
    try:
        reply = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise HTTPException(status_code=502, detail="Chatbot provider returned an invalid response.") from exc
    return ChatResponse(reply=reply)
