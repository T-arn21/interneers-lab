import React from "react";

export default function AboutUsPage() {
  return (
    <main className="app-page-container">
      <div className="about-us-content">
        <h1>About Us</h1>
        <p>
          Welcome to Product Store! This is a demo website created by Arnav Tiku from IIT Guwahati as a part of the Interneer's Lab. Make sure to
          checkout all the features and enjoy shopping!!
        </p>

        <div className="contact-info">
          <h2>Contact Us</h2>
          <address>
            <p>
              <strong>Address:</strong> IIT Guwahati
              <br />
              North Guwahati, Assam, India, 781 039
            </p>
            <p>
              <strong>Phone:</strong> +91 7011374377
            </p>
            <p>
              <strong>Email:</strong> arnavtiku@gmail.com
            </p>
          </address>
        </div>
      </div>
    </main>
  );
}
