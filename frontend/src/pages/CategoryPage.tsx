import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { ProductItem } from "../components/Product";
import StaticProductTile from "../components/StaticProductTile";

const categoryMap: Record<string, string | null> = {
  mens: "men's clothing",
  womens: "women's clothing",
  accessories: "jewelery",
  others: "electronics",
  collabs: null,
  sneakers: null,
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
    fetch("https://fakestoreapi.com/products")
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }
        return response.json();
      })
      .then((data: ProductItem[]) => {
        const id = categoryId || "others";
        const targetApiCategory = categoryMap[id];

        let filteredItems: ProductItem[] = [];

        if (id === "collabs" || id === "sneakers") {
          // just shuffle all items for collabs and sneakers
          filteredItems = [...data].sort(() => 0.5 - Math.random());
        } else if (targetApiCategory) {
          filteredItems = data.filter(
            (item) => item.category === targetApiCategory,
          );
        } else {
          filteredItems = data;
        }

        // Duplicate items if length < 20 to strictly hit 20 slots
        if (filteredItems.length === 0) {
          filteredItems = data; // Last resort fallback to avoid empty page
        }

        const gridItems: ProductItem[] = [];
        let index = 0;
        while (gridItems.length < 20) {
          gridItems.push(filteredItems[index % filteredItems.length]);
          index += 1;
        }

        setProducts(gridItems);
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
      copy.sort((a, b) => a.title.localeCompare(b.title));
    } else if (sortMethod === "price-asc") {
      copy.sort((a, b) => a.price - b.price);
    } else if (sortMethod === "price-desc") {
      copy.sort((a, b) => b.price - a.price);
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

        {loading && <p>Loading products...</p>}
        {!loading && error && (
          <p className="error-message">API error: {error}</p>
        )}

        {!loading && !error && (
          <div className="category-grid">
            {sortedProducts.map((product, index) => (
              <StaticProductTile
                key={`static-${product.id}-${index}`}
                product={product}
              />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
