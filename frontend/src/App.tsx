import React from "react";
import { Link, NavLink, Navigate, Route, Routes } from "react-router-dom";
import ProductPage from "./pages/ProductPage";
import "./App.css";

function Home() {
  return (
    <main className="app-home">
      <section className="home-hero">
        <p className="home-hero__eyebrow">Interactive Storefront</p>
        <h1>Interneers Frontend Lab</h1>
        <p>
          Explore animated product showcases and rich product interactions in
          the Products page.
        </p>
        <Link className="home-hero__cta" to="/products">
          Explore Products
        </Link>
      </section>
    </main>
  );
}

function App() {
  return (
    <div className="App">
      <header className="app-header">
        <div className="app-header__inner">
          <nav className="app-nav" aria-label="Main navigation">
            <NavLink to="/" end>
              Home
            </NavLink>
            <NavLink to="/products">Products</NavLink>
          </nav>
          <button className="view-cart-button" type="button">
            View Cart
          </button>
        </div>
      </header>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/products" element={<ProductPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}

export default App;
