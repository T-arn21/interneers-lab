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

const fallbackProduct: Product = {
  id: 0,
  title: "Sample Product",
  price: 0,
  category: "General",
  description: "Loading product details from API.",
  image: "",
};

export default function ProductPage() {
  const [product, setProduct] = useState<Product>(fallbackProduct);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("https://fakestoreapi.com/products/1")
      .then((response) => {
        console.log("Product API response object:", response);
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }
        return response.json();
      })
      .then((data: Product) => {
        console.log("Product API parsed JSON:", data);
        setProduct(data);
      })
      .catch((err: Error) => {
        console.error("Product API fetch error:", err);
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  return (
    <main className="product-page">
      <section className="product-section" aria-label="Product details">
        <h1>Product Display</h1>
        <article className="product-tile">
          <p className="product-tile__label">Featured Product</p>
          <h2>{product.title}</h2>
          <p className="product-tile__price">${product.price.toFixed(2)}</p>
          <p className="product-tile__category">{product.category}</p>
          <p className="product-tile__description">{product.description}</p>
          <button type="button">Add to Cart</button>
        </article>
        {loading && <p className="status-message">Fetching product data...</p>}
        {error && !loading && (
          <p className="status-message error-message">
            API error: {error}. Showing fallback product data.
          </p>
        )}
      </section>
    </main>
  );
}
