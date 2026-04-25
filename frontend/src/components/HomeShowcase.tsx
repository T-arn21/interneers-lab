import React, { useEffect, useMemo, useState } from "react";
import ProductList, { ProductCategory } from "./ProductList";
import { ProductItem } from "./Product";
import "../styles/ProductPage.css";

const categories: ProductCategory[] = [
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

const slideshowDescription = "LOREM IPSUM";

export default function HomeShowcase() {
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [flippedTiles, setFlippedTiles] = useState<Record<string, boolean>>({});
  const [activeSlideIndex, setActiveSlideIndex] = useState(0);

  useEffect(() => {
    fetch("https://fakestoreapi.com/products")
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }
        return response.json();
      })
      .then((data: ProductItem[]) => {
        setProducts(data);
      })
      .catch((err: Error) => {
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const slideshowProducts = useMemo(() => {
    const uniqueProducts: ProductItem[] = [];
    const seenImages = new Set<string>();
    for (const product of products) {
      if (!seenImages.has(product.image)) {
        seenImages.add(product.image);
        uniqueProducts.push(product);
      }
    }
    return uniqueProducts.slice(0, 3);
  }, [products]);

  useEffect(() => {
    if (slideshowProducts.length <= 1) {
      return undefined;
    }

    const intervalId = window.setInterval(() => {
      setActiveSlideIndex(
        (currentIndex) => (currentIndex + 1) % slideshowProducts.length,
      );
    }, 3500);

    return () => window.clearInterval(intervalId);
  }, [slideshowProducts]);

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

  const getShortDescription = (description: string) => {
    if (description.length <= 120) {
      return description;
    }
    return `${description.slice(0, 117)}...`;
  };

  const ensureMinimumItems = (items: ProductItem[], minimumCount = 6) => {
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

  const goToPrevious = () => {
    setActiveSlideIndex((prev) =>
      prev === 0 ? slideshowProducts.length - 1 : prev - 1,
    );
  };

  const goToNext = () => {
    setActiveSlideIndex((prev) => (prev + 1) % slideshowProducts.length);
  };

  const hasProducts = products.length > 0;
  const safeSlideIndex =
    slideshowProducts.length > 0
      ? activeSlideIndex % slideshowProducts.length
      : 0;
  const activeSlideProduct = slideshowProducts[safeSlideIndex];

  return (
    <main className="app-home">
      <section
        className="home-slideshow"
        aria-label="Featured products slideshow"
      >
        {activeSlideProduct ? (
          <img
            className="home-slideshow__image"
            src={activeSlideProduct.image}
            alt={activeSlideProduct.title}
          />
        ) : (
          <div className="home-slideshow__image home-slideshow__placeholder" />
        )}
        <p className="home-slideshow__caption">
          {activeSlideProduct?.title || slideshowDescription}
        </p>

        {slideshowProducts.length > 1 && (
          <>
            <button
              type="button"
              className="home-slideshow__control home-slideshow__control--prev"
              onClick={goToPrevious}
              aria-label="Previous slide"
            >
              &#10094;
            </button>
            <button
              type="button"
              className="home-slideshow__control home-slideshow__control--next"
              onClick={goToNext}
              aria-label="Next slide"
            >
              &#10095;
            </button>
          </>
        )}
      </section>

      <section
        className="product-section app-home__product-section"
        aria-label="Product list"
      >
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
              <ProductList
                key={category.apiCategory}
                category={category}
                products={marqueeProducts}
                flippedTiles={flippedTiles}
                onToggleTileView={toggleTileView}
                onResetTileView={resetTileView}
                getShortDescription={getShortDescription}
              />
            );
          })}
      </section>
    </main>
  );
}
