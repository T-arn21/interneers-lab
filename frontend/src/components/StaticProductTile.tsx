import React from "react";
import { ProductItem } from "./Product";

interface StaticProductTileProps {
  product: ProductItem;
}

const getShortDescription = (description: string) => {
  if (!description) return "";
  if (description.length <= 100) return description;
  return `${description.slice(0, 97)}...`;
};

export default function StaticProductTile({ product }: StaticProductTileProps) {
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
          <button type="button" className="add-cart-button static-add-cart">
            Add to Cart
          </button>
        </div>
      </div>
    </article>
  );
}
