import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { ProductItem } from "../components/Product";
import StaticProductTile from "../components/StaticProductTile";

const categoryMap: Record<string, string | null> = {
  mens: "men's clothing",
  womens: "women's clothing",
  accessories: "accessories",
  others: "others",
  collabs: "collabs",
  sneakers: "sneakers",
};

const categoryTitles: Record<string, string> = {
  mens: "Men's Clothing",
  womens: "Women's Clothing",
  accessories: "Accessories",
  collabs: "Collabs",
  others: "Electronics",
  sneakers: "Sneakers",
};

export default function CategoryPage() {
  const { categoryId } = useParams<{ categoryId: string }>();
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [sortMethod, setSortMethod] = useState<string>("default");

  useEffect(() => {
    setLoading(true);
    fetch("http://localhost:8000/products/?page_size=50")
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        const rawProducts: ProductItem[] = data.data.results || [];
        const id = categoryId || "others";
        const targetApiCategory = categoryMap[id];

        let filteredItems: ProductItem[] = [];

        if (targetApiCategory) {
          filteredItems = rawProducts.filter(
            (item) => item.categories && item.categories.includes(targetApiCategory),
          );
        } else {
          filteredItems = rawProducts;
        }

        setProducts(filteredItems);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [categoryId]);

  const displayTitle =
    categoryId && categoryTitles[categoryId]
      ? categoryTitles[categoryId]
      : "Category";

  const sortedProducts = React.useMemo(() => {
    const copy = [...products];
    if (sortMethod === "a-z") {
      copy.sort((a, b) => (a.name || "").localeCompare(b.name || ""));
    } else if (sortMethod === "price-asc") {
      copy.sort((a, b) => Number(a.price) - Number(b.price));
    } else if (sortMethod === "price-desc") {
      copy.sort((a, b) => Number(b.price) - Number(a.price));
    }
    return copy;
  }, [products, sortMethod]);

  return (
    <main className="app-page-container">
      <section className="category-section">
        <header className="category-header">
          <h1>{displayTitle}</h1>
          <div className="category-filter">
            <label
              htmlFor="sort-filter"
              style={{ color: "#f8fafc", marginRight: "10px" }}
            >
              Sort by:{" "}
            </label>
            <select
              id="sort-filter"
              value={sortMethod}
              onChange={(e) => setSortMethod(e.target.value)}
              style={{
                padding: "6px",
                borderRadius: "4px",
                border: "1px solid #1e293b",
                background: "#0b1120",
                color: "#e2e8f0",
              }}
            >
              <option value="default">Recommended</option>
              <option value="a-z">A-Z (Alphabetically)</option>
              <option value="price-asc">Price (Low to High)</option>
              <option value="price-desc">Price (High to Low)</option>
            </select>
          </div>
        </header>

        {loading && (
          <div className="spinner-container" aria-hidden="true">
            <div className="spinner"></div>
            <p className="spinner-text">Good things take time</p>
          </div>
        )}
        {!loading && error && (
          <p className="error-message">API error: {error}</p>
        )}

        {!loading && !error && sortedProducts.length > 0 && (
          <div className="category-grid">
            {sortedProducts.map((product, index) => (
              <StaticProductTile
                key={`static-${product.id}-${index}`}
                product={product}
              />
            ))}
          </div>
        )}
        {!loading && !error && sortedProducts.length === 0 && (
          <p className="status-message">No products found!</p>
        )}
      </section>
    </main>
  );
}
