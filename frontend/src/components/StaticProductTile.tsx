import React from "react";
import { ProductItem } from "./Product";
import { useCart } from "../context/CartContext";

interface StaticProductTileProps {
  product: ProductItem;
}

const getShortDescription = (description: string) => {
  if (!description) return "";
  if (description.length <= 100) return description;
  return `${description.slice(0, 97)}...`;
};

export default function StaticProductTile({ product }: StaticProductTileProps) {
  const { cartItems, addToCart, updateQuantity } = useCart();
  const cartItem = cartItems.find((item) => item.product.id === product.id);
  const quantity = cartItem ? cartItem.quantity : 0;
  return (
    <article className="static-product-tile-wrap">
      <div className="product-tile static-product-tile">
        <img
          className="product-tile__image"
          src={product.image}
          alt={product.title}
          loading="lazy"
        />
        <h3>{product.title}</h3>
        <p className="product-tile__price">${product.price.toFixed(2)}</p>
        <p className="product-tile__description static-product-tile__description">
          {getShortDescription(product.description)}
        </p>
        <div className="product-tile__actions">
          {quantity === 0 ? (
            <button
              type="button"
              className="add-cart-button static-add-cart"
              onClick={() => addToCart(product)}
            >
              Add to Cart
            </button>
          ) : (
            <div className="cart-pill static-add-cart">
              <button
                onClick={() => updateQuantity(product.id, -1)}
                className="cart-pill-btn"
              >
                -
              </button>
              <span className="cart-pill-qty">{quantity} in cart</span>
              <button
                onClick={() => updateQuantity(product.id, 1)}
                className="cart-pill-btn"
              >
                +
              </button>
            </div>
          )}
        </div>
      </div>
    </article>
  );
}
