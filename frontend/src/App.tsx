import React from "react";
import { Link, NavLink, Navigate, Route, Routes } from "react-router-dom";
import HomeShowcase from "./components/HomeShowcase";
import ProductPage from "./pages/ProductPage";
import AboutUsPage from "./pages/AboutUsPage";
import CategoryPage from "./pages/CategoryPage";
import CartPage from "./pages/CartPage";
import SearchPage from "./pages/SearchPage";
import SearchBar from "./components/SearchBar";
import AdminPage from "./pages/AdminPage";
import "./App.css";

function Home() {
  return <HomeShowcase />;
}

function App() {
  return (
    <div className="App">
      <header className="app-header">
        <div className="app-header__inner">
          <Link className="brand-block" to="/" aria-label="Product Store home">
            <img
              className="brand-block__logo"
              src="/rippling.webp"
              alt="Logo"
            />
            <span className="brand-block__title">Product Store</span>
          </Link>

          <SearchBar />

          <nav className="app-nav" aria-label="Main navigation">
            <NavLink to="/" end>
              Home
            </NavLink>
            <div className="nav-dropdown">
              <button type="button" className="nav-dropdown__toggle">
                Categories <span aria-hidden="true">&#9662;</span>
              </button>
              <div
                className="nav-dropdown__menu"
                role="menu"
                aria-label="Categories"
              >
                <Link to="/category/mens">Men&apos;s Clothing</Link>
                <Link to="/category/womens">Women&apos;s Clothing</Link>
                <Link to="/category/sneakers">Sneakers</Link>
                <Link to="/category/accessories">Accessories</Link>
                <Link to="/category/collabs">Collabs</Link>
                <Link to="/category/others">Others</Link>
              </div>
            </div>
            <NavLink to="/about" className="app-nav__button">
              About Us
            </NavLink>
            <NavLink to="/admin" className="app-nav__button">
              Admin
            </NavLink>
            <NavLink to="/cart" className="view-cart-button">
              View Cart
            </NavLink>
          </nav>
        </div>
      </header>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<AboutUsPage />} />
        <Route path="/admin" element={<AdminPage />} />
        <Route path="/category/:categoryId" element={<CategoryPage />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/products" element={<ProductPage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}

export default App;
