import React, { useState, useEffect, useRef, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { ProductItem } from "./Product";
import "../App.css";

export default function SearchBar() {
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [query, setQuery] = useState("");
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const navigate = useNavigate();
  const searchRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch("http://localhost:8000/products/?page_size=50")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch products");
        return res.json();
      })
      .then((data) => setProducts(data.data.results || []))
      .catch((err) => console.error("Error fetching products for search", err));
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        searchRef.current &&
        !searchRef.current.contains(event.target as Node)
      ) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const filteredProducts = useMemo(() => {
    if (!query.trim()) return [];

    const lowerQuery = query.toLowerCase();
    const matched = products.filter((p) =>
      (p.name || "").toLowerCase().includes(lowerQuery),
    );

    const uniqueMap = new Map<string, ProductItem>();
    matched.forEach((p) => {
      const key = p.name || "";
      if (!uniqueMap.has(key)) {
        uniqueMap.set(key, p);
      }
    });

    return Array.from(uniqueMap.values()).slice(0, 5);
  }, [query, products]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    setIsDropdownOpen(true);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && query.trim()) {
      setIsDropdownOpen(false);
      navigate(`/search?q=${encodeURIComponent(query)}`);
    }
  };

  const handleProductSelect = (product: ProductItem) => {
    setIsDropdownOpen(false);
    setQuery(""); // Or keep it, but clearing is cleaner
    navigate(`/search?id=${product.id}`);
  };

  return (
    <div className="search-container" ref={searchRef}>
      <div className="search-shell" role="search" aria-label="Search products">
        <span className="search-shell__icon" aria-hidden="true">
          &#128269;
        </span>
        <input
          className="search-shell__input"
          type="search"
          placeholder="what are you looking for?"
          aria-label="Search"
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => {
            if (query.trim()) setIsDropdownOpen(true);
          }}
        />
      </div>

      {isDropdownOpen && filteredProducts.length > 0 && (
        <ul className="search-dropdown" aria-label="Search suggestions">
          {filteredProducts.map((product) => (
            <li
              key={product.id}
              className="search-dropdown__item"
              onClick={() => handleProductSelect(product)}
            >
              <img
                src={product.image}
                alt={product.name}
                className="search-dropdown__image"
              />
              <span className="search-dropdown__title">{product.name}</span>
              <span className="search-dropdown__price">
                ₹{Number(product.price).toFixed(2)}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
