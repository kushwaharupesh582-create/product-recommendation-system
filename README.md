# Curio — Personalized Product Recommendations

Curio is a general-purpose product discovery app. The React frontend displays a searchable catalog of 64 sample products, a dedicated picks page, and a floating glass-style Gemini shopping assistant. The FastAPI backend uses PostgreSQL to store products, shoppers, and purchase history. Its recommendation engine combines customer-based collaborative filtering with product-content similarity and a small popularity signal.

## Requirements

- Python 3.11+
- Node.js 18+
- Docker Desktop (or a local PostgreSQL 16 instance)
- A Gemini API key to enable the AI shopping assistant

## Run locally

1. Start PostgreSQL:

   ```powershell
   docker compose up -d db
   ```

2. Configure and start the API:

   ```powershell
   Copy-Item backend\.env.example backend\.env
   # Add your Gemini API key to backend\.env to enable the chatbot.
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   uvicorn app.main:app --reload --reload-dir app
   ```

   The API creates its tables and adds sample catalog, shopper, and purchase data on first startup. API docs are available at <http://localhost:8000/docs>.

3. In a separate terminal, start the frontend:

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

   Open <http://localhost:5173>. Use **See your picks** to open the recommendations-only page.

The Gemini integration is server-side; keep `GEMINI_API_KEY` in `backend/.env` and never put it in frontend code. If the key is not configured, the chat endpoint returns a clear configuration error while the catalog and recommendations remain available.

## Recommendation approach

- **Collaborative filtering:** compares implicit purchase histories with cosine similarity and recommends products favored by similar shoppers.
- **Content similarity:** uses TF-IDF over product names, categories, descriptions, and tags to find products related to a shopper's purchases.
- **Cold-start/popularity:** shoppers without purchase history get popular catalog items; recommendations exclude products they have already purchased.

The included catalog and purchase history are sample data for development. On startup, the seed script adds newly introduced catalog items without deleting existing products or purchases. The demo's **Mark as purchased** action records an interaction and refreshes that shopper's recommendations; the same `POST /api/purchases` endpoint can be connected to a real checkout flow. Add authentication and validate purchase events from a trusted source before using real shoppers.
