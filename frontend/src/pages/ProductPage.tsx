import React, { useEffect, useState } from "react";
import "../styles/ProductPage.css";

interface Product {
  id: number;
  title: string;
  price: number;
  category: string;
  description: string;
  image: string;
}

export default function ProductPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("https://fakestoreapi.com/products")
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }
        return response.json();
      })
      .then((data: Product[]) => {
        setProducts(data);
      })
      .catch((err: Error) => {
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const hasProducts = products.length > 0;

  return (
    <main className="product-page">
      <section className="product-section" aria-label="Product list">
        <h1>Product Display</h1>

        {loading && (
          <div className="product-grid product-grid--loading" aria-hidden="true">
            {Array.from({ length: 4 }).map((_, index) => (
              <article className="product-tile product-tile--skeleton" key={index}>
                <div className="skeleton skeleton-image" />
                <div className="skeleton skeleton-title" />
                <div className="skeleton skeleton-text" />
                <div className="skeleton skeleton-text short" />
              </article>
            ))}
          </div>
        )}

        {!loading && error && (
          <p className="status-message error-message">API error: {error}</p>
        )}

        {!loading && !error && !hasProducts && (
          <p className="status-message">No products found.</p>
        )}

        {!loading && hasProducts && (
          <div className="product-grid">
            {products.map((product) => (
              <article className="product-tile" key={product.id}>
                <p className="product-tile__label">Product #{product.id}</p>
                <img
                  className="product-tile__image"
                  src={product.image}
                  alt={product.title}
                  loading="lazy"
                />
                <h2>{product.title}</h2>
                <p className="product-tile__price">${product.price.toFixed(2)}</p>
                <p className="product-tile__category">{product.category}</p>
                <p className="product-tile__description">{product.description}</p>
                <button type="button">Add to Cart</button>
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
