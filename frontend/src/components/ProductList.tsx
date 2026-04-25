import React from "react";
import Product, { ProductItem } from "./Product";

export interface ProductCategory {
  title: string;
  apiCategory: string;
  speedClass: string;
}

interface ProductListProps {
  category: ProductCategory;
  products: ProductItem[];
  flippedTiles: Record<string, boolean>;
  onToggleTileView: (tileId: string) => void;
  onResetTileView: (tileId: string) => void;
  getShortDescription: (description: string) => string;
}

export default function ProductList({
  category,
  products,
  flippedTiles,
  onToggleTileView,
  onResetTileView,
  getShortDescription,
}: ProductListProps) {
  return (
    <section className="product-row-section">
      <header className="product-row-header">
        <h2>{category.title}</h2>
      </header>
      <div className="product-row-marquee">
        <div className={`product-row-track ${category.speedClass}`}>
          {products.map((product, index) => {
            const tileId = `${category.apiCategory}-${product.id}-${index}`;
            const isFlipped = Boolean(flippedTiles[tileId]);

            return (
              <Product
                key={`${product.id}-${index}`}
                product={product}
                categoryTitle={category.title}
                tileId={tileId}
                isFlipped={isFlipped}
                onToggle={onToggleTileView}
                onReset={onResetTileView}
                getShortDescription={getShortDescription}
              />
            );
          })}
        </div>
      </div>
    </section>
  );
}
