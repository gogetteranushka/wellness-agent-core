import React from "react";
import { Link } from "react-router-dom";

const NotFound = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <h1 className="text-7xl font-extrabold mb-4">404</h1>
      <p className="text-2xl mb-8 text-muted-foreground">Page not found.</p>
      <Link
        to="/"
        className="px-6 py-3 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 transition"
      >
        Go Home
      </Link>
    </div>
  );
};

export default NotFound;
