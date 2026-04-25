import React from "react";

export interface ProductItem {
  id: number;
  title: string;
  price: number;
  category: string;
  description: string;
  image: string;
}

interface ProductProps {
  product: ProductItem;
  categoryTitle: string;
  tileId: string;
  isFlipped: boolean;
  onToggle: (tileId: string) => void;
  onReset: (tileId: string) => void;
  getShortDescription: (description: string) => string;
}

export default function Product({
  product,
  categoryTitle,
  tileId,
  isFlipped,
  onToggle,
  onReset,
  getShortDescription,
}: ProductProps) {
  return (
    <article className="product-tile-wrap" onMouseLeave={() => onReset(tileId)}>
      <div className={`product-tile-flip ${isFlipped ? "is-flipped" : ""}`}>
        <div className="product-tile product-tile-front">
          <img
            className="product-tile__image"
            src={product.image}
            alt={product.title}
            loading="lazy"
          />
          <h3>{product.title}</h3>
          <p className="product-tile__price">${product.price.toFixed(2)}</p>
          <div className="product-tile__actions">
            <button type="button" className="add-cart-button">
              Add to Cart
            </button>
            <button
              type="button"
              className="view-button"
              onClick={() => onToggle(tileId)}
            >
              View
            </button>
          </div>
        </div>
        <div className="product-tile product-tile-back">
          <p className="product-tile__category">{categoryTitle}</p>
          <p className="product-tile__description">
            {getShortDescription(product.description)}
          </p>
          <button
            type="button"
            className="view-button"
            onClick={() => onToggle(tileId)}
          >
            Back
          </button>
        </div>
      </div>
    </article>
  );
}
