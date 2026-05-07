import React, { useState, useEffect } from "react";
import { ProductItem } from "./Product";

const CATEGORIES = [
  "men's clothing",
  "women's clothing",
  "jewelery",
  "sneakers",
  "accessories",
  "collabs",
  "others",
];

export default function AdminProductManagement() {
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [includeDeleted, setIncludeDeleted] = useState(false);
  const [search, setSearch] = useState("");

  const [isEditing, setIsEditing] = useState(false);
  const [currentProduct, setCurrentProduct] = useState<Partial<ProductItem>>(
    {},
  );

  const [formError, setFormError] = useState("");
  const [formLoading, setFormLoading] = useState(false);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    fetchProducts();
  }, [includeDeleted, search]);

  const fetchProducts = () => {
    setLoading(true);
    let url = `http://localhost:8000/products/?page_size=50`;
    if (includeDeleted) url += "&include_deleted=1";
    if (search) url += `&search=${encodeURIComponent(search)}`;

    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch products");
        return res.json();
      })
      .then((data) => setProducts(data.data.results || []))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("Are you sure you want to delete this product?"))
      return;
    try {
      const res = await fetch(`http://localhost:8000/products/${id}/`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Failed to delete product");
      fetchProducts();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleEditClick = (product: ProductItem) => {
    setCurrentProduct(product);
    setIsEditing(true);
    setFormError("");
  };

  const handleCreateNew = () => {
    setCurrentProduct({
      name: "",
      brand: "",
      price: "",
      categories: [CATEGORIES[0]],
      warehouse_quantity: 0,
      description: "",
      image: "",
    });
    setIsEditing(true);
    setFormError("");
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setCurrentProduct((prev) => ({
          ...prev,
          image: reader.result as string,
        }));
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormLoading(true);
    setFormError("");

    const isUpdate = !!currentProduct.id;
    const url = isUpdate
      ? `http://localhost:8000/products/${currentProduct.id}/`
      : `http://localhost:8000/products/`;
    const method = isUpdate ? "PATCH" : "POST";

    const payload = {
      ...currentProduct,
      price: Number(currentProduct.price),
      warehouse_quantity: Number(currentProduct.warehouse_quantity),
    };

    try {
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) {
        let errorMsg = data.message || "Failed to save product";
        if (data.errors && typeof data.errors === "object") {
          const details = Object.entries(data.errors)
            .map(
              ([field, msgs]) =>
                `${field}: ${Array.isArray(msgs) ? msgs.join(", ") : msgs}`,
            )
            .join(" | ");
          if (details) errorMsg += ` (${details})`;
        }
        throw new Error(errorMsg);
      }
      setIsEditing(false);
      fetchProducts();
    } catch (err: any) {
      setFormError(err.message);
    } finally {
      setFormLoading(false);
    }
  };

  return (
    <div style={{ marginTop: "20px" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "20px",
        }}
      >
        <h3>Product Inventory</h3>
        <button
          onClick={handleCreateNew}
          style={{
            padding: "8px 16px",
            backgroundColor: "#10b981",
            color: "#022c22",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            fontWeight: "bold",
          }}
        >
          + Create Product
        </button>
      </div>

      <div style={{ display: "flex", gap: "20px", marginBottom: "20px" }}>
        <input
          type="text"
          placeholder="Search by ID or Name..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            padding: "8px",
            width: "300px",
            borderRadius: "4px",
            border: "1px solid #1e293b",
            background: "#0b1120",
            color: "#e2e8f0",
          }}
        />
        <label style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <input
            type="checkbox"
            checked={includeDeleted}
            onChange={(e) => setIncludeDeleted(e.target.checked)}
          />
          Show Deleted
        </label>
      </div>

      {error && <p style={{ color: "red" }}>{error}</p>}
      {loading && (
        <div className="spinner-container" aria-hidden="true">
          <div className="spinner"></div>
          <p className="spinner-text">Good things take time</p>
        </div>
      )}

      {!loading && products.length === 0 && <p>No products found!</p>}

      {!loading && products.length > 0 && (
        <div style={{ overflowX: "auto" }}>
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              textAlign: "left",
              fontSize: "14px",
            }}
          >
            <thead>
              <tr
                style={{
                  borderBottom: "2px solid #1e293b",
                  backgroundColor: "#0b1120",
                }}
              >
                <th style={{ padding: "10px" }}>ID</th>
                <th style={{ padding: "10px" }}>Image</th>
                <th style={{ padding: "10px" }}>Name</th>
                <th style={{ padding: "10px" }}>Brand</th>
                <th style={{ padding: "10px" }}>Category</th>
                <th style={{ padding: "10px" }}>Price</th>
                <th style={{ padding: "10px" }}>Qty</th>
                <th style={{ padding: "10px" }}>Created</th>
                <th style={{ padding: "10px" }}>Updated</th>
                <th style={{ padding: "10px" }}>Status</th>
                <th style={{ padding: "10px" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {products.map((p) => (
                <tr
                  key={p.id}
                  style={{
                    borderBottom: "1px solid #1e293b",
                    opacity: p.is_deleted ? 0.5 : 1,
                  }}
                >
                  <td style={{ padding: "10px" }}>{p.id}</td>
                  <td style={{ padding: "10px" }}>
                    {p.image ? (
                      <img
                        src={p.image}
                        alt={p.name}
                        style={{
                          width: "40px",
                          height: "40px",
                          objectFit: "cover",
                          borderRadius: "4px",
                        }}
                      />
                    ) : (
                      "No Image"
                    )}
                  </td>
                  <td style={{ padding: "10px" }}>{p.name}</td>
                  <td style={{ padding: "10px" }}>{p.brand}</td>
                  <td style={{ padding: "10px" }}>{p.categories ? p.categories.join(", ") : ""}</td>
                  <td style={{ padding: "10px" }}>
                    ₹{Number(p.price).toFixed(2)}
                  </td>
                  <td style={{ padding: "10px" }}>{p.warehouse_quantity}</td>
                  <td style={{ padding: "10px" }}>
                    {p.created_at
                      ? new Date(p.created_at).toLocaleDateString()
                      : ""}
                  </td>
                  <td style={{ padding: "10px" }}>
                    {p.updated_at
                      ? new Date(p.updated_at).toLocaleDateString()
                      : ""}
                  </td>
                  <td
                    style={{
                      padding: "10px",
                      color: p.is_deleted ? "#ef4444" : "#10b981",
                    }}
                  >
                    {p.is_deleted ? "Deleted" : "Active"}
                  </td>
                  <td style={{ padding: "10px", display: "flex", gap: "10px" }}>
                    <button
                      onClick={() => handleEditClick(p)}
                      style={{
                        padding: "4px 8px",
                        cursor: "pointer",
                        background: "#3b82f6",
                        color: "#fff",
                        border: "none",
                        borderRadius: "4px",
                      }}
                    >
                      Edit
                    </button>
                    {!p.is_deleted && (
                      <button
                        onClick={() => handleDelete(p.id)}
                        style={{
                          padding: "4px 8px",
                          cursor: "pointer",
                          background: "#ef4444",
                          color: "#fff",
                          border: "none",
                          borderRadius: "4px",
                        }}
                      >
                        Delete
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {isEditing && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0,0,0,0.8)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 100,
          }}
        >
          <div
            style={{
              background: "#0f172a",
              padding: "30px",
              borderRadius: "8px",
              width: "500px",
              maxWidth: "90%",
              border: "1px solid #1e293b",
              maxHeight: "90vh",
              overflowY: "auto",
            }}
          >
            <h3 style={{ marginTop: 0 }}>
              {currentProduct.id ? "Edit Product" : "Create Product"}
            </h3>
            <form
              onSubmit={handleSubmit}
              style={{ display: "flex", flexDirection: "column", gap: "15px" }}
            >
              <div>
                <label style={{ display: "block", marginBottom: "5px" }}>
                  Name *
                </label>
                <input
                  required
                  type="text"
                  value={currentProduct.name || ""}
                  onChange={(e) =>
                    setCurrentProduct({
                      ...currentProduct,
                      name: e.target.value,
                    })
                  }
                  style={{
                    width: "100%",
                    padding: "8px",
                    borderRadius: "4px",
                    border: "1px solid #1e293b",
                    background: "#0b1120",
                    color: "#e2e8f0",
                  }}
                />
              </div>
              <div>
                <label style={{ display: "block", marginBottom: "5px" }}>
                  Brand *
                </label>
                <input
                  required
                  type="text"
                  value={currentProduct.brand || ""}
                  onChange={(e) =>
                    setCurrentProduct({
                      ...currentProduct,
                      brand: e.target.value,
                    })
                  }
                  style={{
                    width: "100%",
                    padding: "8px",
                    borderRadius: "4px",
                    border: "1px solid #1e293b",
                    background: "#0b1120",
                    color: "#e2e8f0",
                  }}
                />
              </div>
              <div style={{ display: "flex", gap: "15px" }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: "block", marginBottom: "5px" }}>
                    Price *
                  </label>
                  <input
                    required
                    type="number"
                    step="0.01"
                    min="0"
                    value={currentProduct.price || ""}
                    onChange={(e) =>
                      setCurrentProduct({
                        ...currentProduct,
                        price: e.target.value,
                      })
                    }
                    style={{
                      width: "100%",
                      padding: "8px",
                      borderRadius: "4px",
                      border: "1px solid #1e293b",
                      background: "#0b1120",
                      color: "#e2e8f0",
                    }}
                  />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: "block", marginBottom: "5px" }}>
                    Quantity *
                  </label>
                  <input
                    required
                    type="number"
                    min="0"
                    value={currentProduct.warehouse_quantity || ""}
                    onChange={(e) =>
                      setCurrentProduct({
                        ...currentProduct,
                        warehouse_quantity: Number(e.target.value),
                      })
                    }
                    style={{
                      width: "100%",
                      padding: "8px",
                      borderRadius: "4px",
                      border: "1px solid #1e293b",
                      background: "#0b1120",
                      color: "#e2e8f0",
                    }}
                  />
                </div>
              </div>
              <div>
                <label style={{ display: "block", marginBottom: "5px" }}>
                  Categories * (Hold Ctrl/Cmd to select multiple)
                </label>
                <select
                  multiple
                  value={currentProduct.categories || []}
                  onChange={(e) => {
                    const options = Array.from(e.target.selectedOptions, option => option.value);
                    setCurrentProduct({
                      ...currentProduct,
                      categories: options,
                    })
                  }}
                  style={{
                    width: "100%",
                    padding: "8px",
                    borderRadius: "4px",
                    border: "1px solid #1e293b",
                    background: "#0b1120",
                    color: "#e2e8f0",
                  }}
                >
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label style={{ display: "block", marginBottom: "5px" }}>
                  Description
                </label>
                <textarea
                  rows={3}
                  value={currentProduct.description || ""}
                  onChange={(e) =>
                    setCurrentProduct({
                      ...currentProduct,
                      description: e.target.value,
                    })
                  }
                  style={{
                    width: "100%",
                    padding: "8px",
                    borderRadius: "4px",
                    border: "1px solid #1e293b",
                    background: "#0b1120",
                    color: "#e2e8f0",
                    resize: "vertical",
                  }}
                />
              </div>
              <div>
                <label style={{ display: "block", marginBottom: "5px" }}>
                  Image Upload
                </label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  style={{ width: "100%", color: "#e2e8f0" }}
                />
                {currentProduct.image && (
                  <img
                    src={currentProduct.image}
                    alt="Preview"
                    style={{
                      marginTop: "10px",
                      width: "100px",
                      height: "100px",
                      objectFit: "cover",
                      borderRadius: "4px",
                    }}
                  />
                )}
              </div>

              {formError && (
                <p style={{ color: "#ef4444", margin: 0 }}>{formError}</p>
              )}

              <div style={{ display: "flex", gap: "10px", marginTop: "10px" }}>
                <button
                  type="submit"
                  disabled={formLoading}
                  style={{
                    flex: 1,
                    padding: "10px",
                    backgroundColor: "#10b981",
                    color: "#022c22",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                    fontWeight: "bold",
                  }}
                >
                  {formLoading ? "Saving..." : "Save Product"}
                </button>
                <button
                  type="button"
                  onClick={() => setIsEditing(false)}
                  style={{
                    flex: 1,
                    padding: "10px",
                    backgroundColor: "transparent",
                    color: "#e2e8f0",
                    border: "1px solid #1e293b",
                    borderRadius: "4px",
                    cursor: "pointer",
                  }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
