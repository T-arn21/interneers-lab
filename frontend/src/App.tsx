import React from "react";
import { Link, Navigate, Route, Routes } from "react-router-dom";
import ProductPage from "./pages/ProductPage";
import "./App.css";

function Home() {
  return (
    <main className="app-home">
      <h1>Interneers Frontend Lab</h1>
      <p>Use the navigation above to open the Product page task.</p>
    </main>
  );
}

function App() {
  return (
    <div className="App">
      <header className="app-header">
        <nav className="app-nav" aria-label="Main navigation">
          <Link to="/">Home</Link>
          <Link to="/products">Products</Link>
        </nav>
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
