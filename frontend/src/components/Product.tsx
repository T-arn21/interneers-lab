import React from "react";
import { useCart } from "../context/CartContext";

export interface ProductItem {
  id: number;
  name: string;
  price: number | string;
  categories: string[];
  description: string;
  image: string;
  brand?: string;
  warehouse_quantity?: number;
  is_deleted?: boolean;
  created_at?: string;
  updated_at?: string;
}

interface ProductProps {
  product: ProductItem;
  categoryName: string;
  tileId: string;
  isFlipped: boolean;
  onToggle: (tileId: string) => void;
  onReset: (tileId: string) => void;
  getShortDescription: (description: string) => string;
}

export default function Product({
  product,
  categoryName,
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
            alt={product.name}
            loading="lazy"
          />
          <h3>{product.name}</h3>
          <p className="product-tile__price">
            ₹{Number(product.price).toFixed(2)}
          </p>
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
          <p className="product-tile__category">{categoryName}</p>
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
