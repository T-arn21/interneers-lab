import React from "react";

export default function AboutUsPage() {
  return (
    <main className="app-page-container">
      <div className="about-us-content">
        <h1>About Us</h1>
        <p>
          Welcome to Product Store! We are dedicated to providing you with the
          best quality products across all categories. From fashion to electronics,
          we handpick the finest selection for your needs.
        </p>
        
        <div className="contact-info">
          <h2>Contact Us</h2>
          <address>
            <p><strong>Address:</strong> 1234 Market Street, Suite 500<br/>San Francisco, CA 94103</p>
            <p><strong>Phone:</strong> +1 (555) 123-4567</p>
            <p><strong>Email:</strong> support@productstore.example.com</p>
          </address>
        </div>
      </div>
    </main>
  );
}
