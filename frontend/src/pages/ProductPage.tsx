import React from "react";
import { Link } from "react-router-dom";
import "../styles/ProductPage.css";

export default function ProductPage() {
  return (
    <main className="product-page">
      <section className="product-section" aria-label="Products route notice">
        <h1>Products</h1>
        <p className="product-subtitle">
          The product carousel is now featured on the Home page.
        </p>
        <Link className="home-hero__cta" to="/">
          Go to Home
        </Link>
      </section>
    </main>
  );
}
