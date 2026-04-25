import React from "react";
import { useCart } from "../context/CartContext";

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
  const { cartItems, addToCart, updateQuantity } = useCart();
  const cartItem = cartItems.find((item) => item.product.id === product.id);
  const quantity = cartItem ? cartItem.quantity : 0;
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
            {quantity === 0 ? (
              <button
                type="button"
                className="add-cart-button"
                onClick={() => addToCart(product)}
              >
                Add to Cart
              </button>
            ) : (
              <div className="cart-pill">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    updateQuantity(product.id, -1);
                  }}
                  className="cart-pill-btn"
                >
                  -
                </button>
                <span className="cart-pill-qty">{quantity}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    updateQuantity(product.id, 1);
                  }}
                  className="cart-pill-btn"
                >
                  +
                </button>
              </div>
            )}
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
