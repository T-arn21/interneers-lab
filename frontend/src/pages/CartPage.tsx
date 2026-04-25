import React from "react";
import { useCart } from "../context/CartContext";

export default function CartPage() {
  const { cartItems, updateQuantity } = useCart();

  const totalItems = cartItems.reduce((sum, item) => sum + item.quantity, 0);
  const totalPrice = cartItems.reduce(
    (sum, item) => sum + item.product.price * item.quantity,
    0,
  );

  return (
    <main className="app-page-container">
      <section className="category-section">
        <header className="category-header">
          <h1>Your Cart</h1>
        </header>

        {cartItems.length === 0 ? (
          <p style={{ color: "#f8fafc", fontSize: "18px" }}>No items added.</p>
        ) : (
          <div className="cart-contents" style={{ color: "#e2e8f0" }}>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                marginBottom: "30px",
              }}
            >
              <thead>
                <tr
                  style={{
                    borderBottom: "1px solid #1e293b",
                    textAlign: "left",
                  }}
                >
                  <th style={{ padding: "12px 0" }}>Product</th>
                  <th style={{ padding: "12px 0", textAlign: "center" }}>
                    Price
                  </th>
                  <th style={{ padding: "12px 0", textAlign: "center" }}>
                    Quantity
                  </th>
                  <th style={{ padding: "12px 0", textAlign: "right" }}>
                    Total
                  </th>
                </tr>
              </thead>
              <tbody>
                {cartItems.map((item) => (
                  <tr
                    key={item.product.id}
                    style={{ borderBottom: "1px solid #1e293b" }}
                  >
                    <td
                      style={{
                        padding: "16px 0",
                        display: "flex",
                        alignItems: "center",
                        gap: "12px",
                      }}
                    >
                      <img
                        src={item.product.image}
                        alt={item.product.title}
                        style={{
                          width: "50px",
                          height: "50px",
                          objectFit: "contain",
                          background: "#fff",
                          borderRadius: "4px",
                        }}
                      />
                      <span
                        style={{ maxWidth: "300px", display: "inline-block" }}
                      >
                        {item.product.title}
                      </span>
                    </td>
                    <td style={{ padding: "16px 0", textAlign: "center" }}>
                      ${item.product.price.toFixed(2)}
                    </td>
                    <td style={{ padding: "16px 0", textAlign: "center" }}>
                      <div
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          background: "#1e293b",
                          borderRadius: "99px",
                          overflow: "hidden",
                        }}
                      >
                        <button
                          onClick={() => updateQuantity(item.product.id, -1)}
                          style={{
                            background: "transparent",
                            border: "none",
                            color: "#fff",
                            padding: "8px 12px",
                            cursor: "pointer",
                            fontSize: "18px",
                          }}
                        >
                          -
                        </button>
                        <span
                          style={{
                            padding: "0 8px",
                            width: "30px",
                            textAlign: "center",
                          }}
                        >
                          {item.quantity}
                        </span>
                        <button
                          onClick={() => updateQuantity(item.product.id, 1)}
                          style={{
                            background: "transparent",
                            border: "none",
                            color: "#fff",
                            padding: "8px 12px",
                            cursor: "pointer",
                            fontSize: "18px",
                          }}
                        >
                          +
                        </button>
                      </div>
                    </td>
                    <td
                      style={{
                        padding: "16px 0",
                        textAlign: "right",
                        fontWeight: "bold",
                      }}
                    >
                      ${(item.product.price * item.quantity).toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div
              style={{
                background: "#0b1120",
                padding: "24px",
                borderRadius: "12px",
                border: "1px solid #1e293b",
                maxWidth: "400px",
                marginLeft: "auto",
              }}
            >
              <h2
                style={{ marginTop: 0, marginBottom: "20px", color: "#f8fafc" }}
              >
                Order Summary
              </h2>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  marginBottom: "12px",
                }}
              >
                <span>Total Items:</span>
                <span>{totalItems}</span>
              </div>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  marginBottom: "24px",
                  fontSize: "20px",
                  fontWeight: "bold",
                  color: "#f8fafc",
                }}
              >
                <span>Total Price:</span>
                <span>${totalPrice.toFixed(2)}</span>
              </div>
              <button
                type="button"
                style={{
                  width: "100%",
                  background: "#4f46e5",
                  color: "#fff",
                  border: "none",
                  padding: "14px",
                  borderRadius: "8px",
                  fontSize: "16px",
                  fontWeight: "bold",
                  cursor: "default",
                  opacity: 0.8,
                }}
                onClick={() => {}}
              >
                Proceed
              </button>
            </div>
          </div>
        )}
      </section>
    </main>
  );
}
