import { useEffect, useMemo, useState } from "react";

const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

async function fetchJson(url, options) {
  const response = await fetch(`${API_BASE_URL}${url}`, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Something went wrong. Please try again.");
  }
  return data;
}

function ProductCard({ product, recommended = false, purchased = false, onMarkPurchased }) {
  return (
    <article className="product-card">
      <div className="product-image-wrap">
        <img src={product.image_url} alt={product.name} loading="lazy" />
        {recommended && <span className="match-pill">Picked for you</span>}
      </div>
      <div className="product-info">
        <div className="product-heading">
          <div>
            <p className="eyebrow">{product.category}</p>
            <h3>{product.name}</h3>
          </div>
          <span className="price">{money.format(product.price)}</span>
        </div>
        <p className="product-description">{product.description}</p>
        {recommended && <p className="recommendation-reason">{product.reason}</p>}
        {onMarkPurchased && (
          <button
            className="purchase-action"
            type="button"
            disabled={purchased}
            onClick={() => onMarkPurchased(product.id)}
          >
            {purchased ? "In your purchase history" : "Mark as purchased"}
          </button>
        )}
      </div>
    </article>
  );
}

function ChatPanel({ customerId }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Looking for something in particular? I can help you find a thoughtful pick." },
  ]);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendMessage(event) {
    event.preventDefault();
    const message = draft.trim();
    if (!message || loading) return;
    setMessages((current) => [...current, { role: "user", text: message }]);
    setDraft("");
    setLoading(true);
    try {
      const result = await fetchJson("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, customer_id: customerId }),
      });
      setMessages((current) => [...current, { role: "assistant", text: result.reply }]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        { role: "assistant", text: error.message },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat-widget">
      {isOpen && (
        <section className="chat-card chat-panel" aria-label="Curio shopping assistant">
          <div className="chat-intro">
            <span className="chat-icon" aria-hidden="true">✳</span>
            <div>
              <p className="eyebrow">YOUR SHOPPING SIDEKICK</p>
              <h2>Ask Curio</h2>
            </div>
            <span className="online-dot" title="Assistant ready" />
            <button
              className="chat-close"
              type="button"
              aria-label="Close chat"
              onClick={() => setIsOpen(false)}
            >
              ×
            </button>
          </div>
          <div className="chat-messages" aria-live="polite">
            {messages.map((item, index) => (
              <p className={`chat-message ${item.role}`} key={`${item.role}-${index}`}>
                {item.text}
              </p>
            ))}
            {loading && <p className="chat-message assistant muted">Finding a helpful answer…</p>}
          </div>
          <form className="chat-form" onSubmit={sendMessage}>
            <input
              aria-label="Ask the shopping assistant"
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Try “I need a gift for a coffee lover”"
              maxLength={1000}
            />
            <button type="submit" disabled={!draft.trim() || loading} aria-label="Send message">
              <span aria-hidden="true">↗</span>
            </button>
          </form>
          <p className="chat-disclaimer">Suggestions are based on the products in our catalog.</p>
        </section>
      )}
      <button
        className="chat-toggle"
        type="button"
        aria-label={isOpen ? "Close shopping assistant" : "Open shopping assistant"}
        aria-expanded={isOpen}
        onClick={() => setIsOpen((open) => !open)}
      >
        <span aria-hidden="true">{isOpen ? "×" : "✳"}</span>
        {!isOpen && <span className="chat-toggle-label">Ask Curio</span>}
      </button>
    </div>
  );
}

export default function App() {
  const isPicksPage = window.location.pathname === "/picks";
  const [products, setProducts] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [purchasedProductIds, setPurchasedProductIds] = useState([]);
  const [customerId, setCustomerId] = useState(
    () => new URLSearchParams(window.location.search).get("customer_id") || "",
  );
  const [activeCategory, setActiveCategory] = useState("All");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([fetchJson("/api/products"), fetchJson("/api/customers")])
      .then(([productData, customerData]) => {
        setProducts(productData);
        setCustomers(customerData);
        if (customerData.length) {
          const requestedCustomer = customerData.find(
            (customer) => String(customer.id) === customerId,
          );
          setCustomerId(String(requestedCustomer?.id || customerData[0].id));
        }
      })
      .catch((requestError) => setError(requestError.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!customerId) return;
    fetchJson(`/api/recommendations?customer_id=${customerId}`)
      .then(setRecommendations)
      .catch((requestError) => setError(requestError.message));
    fetchJson(`/api/purchases/${customerId}`)
      .then((purchases) => setPurchasedProductIds(purchases.map((product) => product.id)))
      .catch((requestError) => setError(requestError.message));
  }, [customerId]);

  async function markAsPurchased(productId) {
    try {
      await fetchJson("/api/purchases", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_id: Number(customerId),
          product_id: productId,
        }),
      });
      setPurchasedProductIds((current) => [...new Set([...current, productId])]);
      setRecommendations(
        await fetchJson(`/api/recommendations?customer_id=${customerId}`),
      );
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  const categories = useMemo(
    () => ["All", ...new Set(products.map((product) => product.category))],
    [products],
  );
  const visibleProducts = useMemo(() => {
    const query = search.trim().toLowerCase();
    return products.filter((product) => {
      const matchesCategory = activeCategory === "All" || product.category === activeCategory;
      const matchesSearch =
        !query ||
        `${product.name} ${product.category} ${product.description} ${product.tags.join(" ")}`
          .toLowerCase()
          .includes(query);
      return matchesCategory && matchesSearch;
    });
  }, [activeCategory, products, search]);
  const customerName = customers.find((customer) => String(customer.id) === customerId)?.name;
  const picksUrl = `/picks${customerId ? `?customer_id=${customerId}` : ""}`;

  return (
    <main>
      <header className="topbar">
        <a className="wordmark" href="/" aria-label="Curio home"><span>c</span>urio<span className="wordmark-dot">.</span></a>
        <nav aria-label="Main navigation">
          {isPicksPage ? (
            <>
              <a href="/#discover">Discover</a>
              <a href={picksUrl}>For you</a>
            </>
          ) : (
            <>
              <a href="#discover">Discover</a>
              <a href={picksUrl}>For you</a>
            </>
          )}
        </nav>
        <div className="profile-picker">
          <span className="profile-avatar" aria-hidden="true">{customerName?.[0] || "Y"}</span>
          <label className="visually-hidden" htmlFor="customer-select">Demo shopper profile</label>
          <select id="customer-select" value={customerId} onChange={(event) => setCustomerId(event.target.value)}>
            {customers.map((customer) => (
              <option value={customer.id} key={customer.id}>{customer.name}</option>
            ))}
          </select>
        </div>
      </header>

      {error && <div className="error-banner" role="alert">{error}</div>}

      {isPicksPage ? (
        <section className="picks-page section-shell">
          <a className="back-link" href="/">← Back to the collection</a>
          <div className="section-heading">
            <div>
              <p className="eyebrow"><span className="sparkle">✳</span> YOUR PERSONAL EDIT</p>
              <h1 className="picks-title">
                {customerName ? `Picked for ${customerName.split(" ")[0]}` : "Picked for you"}
              </h1>
              <p className="section-subtitle">
                A thoughtful collection shaped by your purchases and the things you enjoy.
              </p>
            </div>
            <span className="section-count">{recommendations.length.toString().padStart(2, "0")} FINDS</span>
          </div>
          {loading ? (
            <p className="loading-state">Getting your picks ready…</p>
          ) : recommendations.length ? (
            <div className="product-grid">
              {recommendations.map((product) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  recommended
                  onMarkPurchased={markAsPurchased}
                />
              ))}
            </div>
          ) : (
            <p className="loading-state">No picks yet. Browse the collection and record a purchase to get started.</p>
          )}
        </section>
      ) : (
        <>
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow hero-eyebrow"><span /> GOOD FINDS, BETTER FIT</p>
          <h1>A little more<br /> <em>you</em> in every find.</h1>
          <p className="hero-description">
            Discover thoughtful products picked around what you love, what you need, and what you haven’t found yet.
          </p>
          <a className="primary-button" href={picksUrl}>See your picks <span aria-hidden="true">↗</span></a>
          <div className="hero-note"><span className="sparkle">✳</span> Thoughtfully selected, never overwhelming</div>
        </div>
        <div className="hero-art" aria-label="A curated collection of everyday products">
          <div className="hero-orbit orbit-one" />
          <div className="hero-orbit orbit-two" />
          <img src="https://images.unsplash.com/photo-1490312278390-ab64016e0aa9?w=900" alt="Curated home and lifestyle objects" />
          <div className="floating-note"><span>✦</span><div><strong>Made for your kind of everyday</strong><small>Little discoveries, just for you</small></div></div>
          <span className="hero-sticker">FIND<br />YOUR<br />FAVORITE</span>
        </div>
        <div className="hero-index">01 <span /> 04</div>
      </section>

      <section className="recommend-section section-shell" id="recommendations">
        <div className="section-heading">
          <div>
            <p className="eyebrow"><span className="sparkle">✳</span> YOUR PERSONAL EDIT</p>
            <h2>{customerName ? `Picked for ${customerName.split(" ")[0]}` : "Picked for you"}</h2>
            <p className="section-subtitle">A mix of your style and a few happy surprises.</p>
          </div>
          <a className="section-count see-all-link" href={picksUrl}>SEE ALL PICKS ↗</a>
        </div>
        {loading ? (
          <p className="loading-state">Getting your picks ready…</p>
        ) : recommendations.length ? (
          <div className="product-grid">
            {recommendations.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                recommended
                onMarkPurchased={markAsPurchased}
              />
            ))}
          </div>
        ) : (
          <p className="loading-state">No picks yet. Browse the catalog below to find a place to start.</p>
        )}
      </section>

      <section className="catalog-section" id="discover">
        <div className="section-shell">
          <div className="section-heading catalog-heading">
            <div>
              <p className="eyebrow">A GOOD PLACE TO WANDER</p>
              <h2>Explore the collection</h2>
              <p className="section-subtitle">Useful things, lovely things, and things you didn’t know you needed.</p>
            </div>
            <label className="search-box">
              <span aria-hidden="true">⌕</span>
              <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search finds" aria-label="Search products" />
            </label>
          </div>
          <div className="category-list" role="group" aria-label="Filter by category">
            {categories.map((category) => (
              <button
                className={activeCategory === category ? "category-chip active" : "category-chip"}
                key={category}
                onClick={() => setActiveCategory(category)}
              >
                {category}
              </button>
            ))}
          </div>
          {loading ? <p className="loading-state">Loading the collection…</p> : (
            <div className="product-grid">
              {visibleProducts.map((product) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  purchased={purchasedProductIds.includes(product.id)}
                  onMarkPurchased={markAsPurchased}
                />
              ))}
            </div>
          )}
          {!loading && visibleProducts.length === 0 && <p className="loading-state">No products match that search. Try another term.</p>}
        </div>
      </section>

      <footer className="footer">
        <a className="wordmark" href="/"><span>c</span>urio<span className="wordmark-dot">.</span></a>
        <p>Find what feels like you.</p>
        <span>Made for curious people <span className="sparkle">✳</span></span>
      </footer>
        </>
      )}
      <ChatPanel customerId={customerId ? Number(customerId) : null} />
    </main>
  );
}
