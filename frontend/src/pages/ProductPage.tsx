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
  const [flippedTiles, setFlippedTiles] = useState<Record<string, boolean>>({});

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

  const toggleTileView = (tileId: string) => {
    setFlippedTiles((previous) => ({
      ...previous,
      [tileId]: !previous[tileId],
    }));
  };

  const resetTileView = (tileId: string) => {
    setFlippedTiles((previous) => {
      if (!previous[tileId]) {
        return previous;
      }
      return { ...previous, [tileId]: false };
    });
  };

  const categories = [
    {
      title: "Men's Clothing",
      apiCategory: "men's clothing",
      speedClass: "speed-fast",
    },
    {
      title: "Women's Clothing",
      apiCategory: "women's clothing",
      speedClass: "speed-medium",
    },
    { title: "Accessories", apiCategory: "jewelery", speedClass: "speed-slow" },
  ];

  const getShortDescription = (description: string) => {
    if (description.length <= 120) {
      return description;
    }
    return `${description.slice(0, 117)}...`;
  };

  const ensureMinimumItems = (items: Product[], minimumCount = 6) => {
    if (items.length === 0) {
      return items;
    }

    if (items.length >= minimumCount) {
      return items;
    }

    const expanded = [...items];
    let index = 0;
    while (expanded.length < minimumCount) {
      expanded.push(items[index % items.length]);
      index += 1;
    }
    return expanded;
  };

  const hasProducts = products.length > 0;

  return (
    <main className="product-page">
      <section className="product-section" aria-label="Product list">
        <h1>Product Showcase</h1>
        <p className="product-subtitle">
          Browse category lanes with interactive cards. Hover to pause a row.
        </p>

        {loading && (
          <div className="loading-rows" aria-hidden="true">
            {Array.from({ length: 3 }).map((_, rowIndex) => (
              <div className="loading-row" key={rowIndex}>
                {Array.from({ length: 4 }).map((__, index) => (
                  <article
                    className="product-tile product-tile--skeleton"
                    key={index}
                  >
                    <div className="skeleton skeleton-image" />
                    <div className="skeleton skeleton-title" />
                    <div className="skeleton skeleton-text short" />
                  </article>
                ))}
              </div>
            ))}
          </div>
        )}

        {!loading && error && (
          <p className="status-message error-message">API error: {error}</p>
        )}

        {!loading && !error && !hasProducts && (
          <p className="status-message">No products found.</p>
        )}

        {!loading &&
          hasProducts &&
          categories.map((category) => {
            const baseProducts = products.filter(
              (product) => product.category === category.apiCategory,
            );

            if (baseProducts.length === 0) {
              return null;
            }

            const rowProducts = ensureMinimumItems(baseProducts, 6);
            const marqueeProducts = [...rowProducts, ...rowProducts];

            return (
              <section
                className="product-row-section"
                key={category.apiCategory}
              >
                <header className="product-row-header">
                  <h2>{category.title}</h2>
                </header>
                <div className="product-row-marquee">
                  <div className={`product-row-track ${category.speedClass}`}>
                    {marqueeProducts.map((product, index) => {
                      const tileId = `${category.apiCategory}-${product.id}-${index}`;
                      const isFlipped = Boolean(flippedTiles[tileId]);
                      return (
                        <article
                          className="product-tile-wrap"
                          key={`${product.id}-${index}`}
                          onMouseLeave={() => resetTileView(tileId)}
                        >
                          <div
                            className={`product-tile-flip ${isFlipped ? "is-flipped" : ""}`}
                          >
                            <div className="product-tile product-tile-front">
                              <img
                                className="product-tile__image"
                                src={product.image}
                                alt={product.title}
                                loading="lazy"
                              />
                              <h3>{product.title}</h3>
                              <p className="product-tile__price">
                                ${product.price.toFixed(2)}
                              </p>
                              <div className="product-tile__actions">
                                <button
                                  type="button"
                                  className="add-cart-button"
                                >
                                  Add to Cart
                                </button>
                                <button
                                  type="button"
                                  className="view-button"
                                  onClick={() => toggleTileView(tileId)}
                                >
                                  View
                                </button>
                              </div>
                            </div>
                            <div className="product-tile product-tile-back">
                              <p className="product-tile__category">
                                {category.title}
                              </p>
                              <p className="product-tile__description">
                                {getShortDescription(product.description)}
                              </p>
                              <button
                                type="button"
                                className="view-button"
                                onClick={() => toggleTileView(tileId)}
                              >
                                Back
                              </button>
                            </div>
                          </div>
                        </article>
                      );
                    })}
                  </div>
                </div>
              </section>
            );
          })}
      </section>
    </main>
  );
}
