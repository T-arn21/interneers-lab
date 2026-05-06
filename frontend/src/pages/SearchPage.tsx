import React, { useEffect, useState, useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import { ProductItem } from "../components/Product";
import StaticProductTile from "../components/StaticProductTile";

export default function SearchPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get("q") || "";
  const productId = searchParams.get("id") || "";

  const [products, setProducts] = useState<ProductItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    fetch("http://localhost:8000/products/?page_size=50")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch products");
        return res.json();
      })
      .then((data) => {
        setProducts(data.data.results || []);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const filteredProducts = useMemo(() => {
    if (productId) {
      return products.filter((p) => p.id === Number(productId));
    }

    if (query) {
      const lowerQuery = query.toLowerCase();
      return products.filter((p) =>
        (p.name || "").toLowerCase().includes(lowerQuery),
      );
    }

    return products;
  }, [products, query, productId]);

  const displayTitle = productId
    ? "Search Results"
    : query
      ? `Search Results for "${query}"`
      : "All Products";

  return (
    <main className="app-page-container">
      <section className="category-section">
        <header className="category-header">
          <h1>{displayTitle}</h1>
        </header>

        {loading && <p>Loading search results...</p>}
        {!loading && error && (
          <p className="error-message">API error: {error}</p>
        )}

        {!loading && !error && filteredProducts.length === 0 && (
          <p className="status-message">
            No products found matching your search.
          </p>
        )}

        {!loading && !error && filteredProducts.length > 0 && (
          <div className="category-grid">
            {filteredProducts.map((product, index) => (
              <StaticProductTile
                key={`search-${product.id}-${index}`}
                product={product}
              />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
