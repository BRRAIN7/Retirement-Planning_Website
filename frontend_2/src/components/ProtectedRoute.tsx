import React, { useEffect, useState, ReactNode } from "react";
import { Navigate } from "react-router-dom";
import api from "./api";

interface ProtectedRouteProps {
  children: ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const [isValid, setIsValid] = useState<boolean | null>(null);

  useEffect(() => {
    const verifyUser = async () => {
      const token = localStorage.getItem("token");

      // 🚫 No token → not authenticated
      if (!token) {
        setIsValid(false);
        return;
      }

      try {
        // 🔍 Try verifying with backend first
        const res = await api.post("/verify-token", { token });

        if (res.data.valid) {
          setIsValid(true);
        } else {
          setIsValid(false);
        }
      } catch (err) {
        console.warn(
          "⚠️ Backend verification failed. Using demo fallback mode."
        );

        // 🧩 Fallback: check for demo token
        if (token.startsWith("demo-token-")) {
          setIsValid(true);
        } else {
          setIsValid(false);
        }
      }
    };

    verifyUser();
  }, []);

  // 🕒 Show loading while verifying
  if (isValid === null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900 text-white">
        <p>Verifying session...</p>
      </div>
    );
  }

  // 🚫 Invalid session → clear and redirect
  if (!isValid) {
    localStorage.clear();
    return <Navigate to="/auth" replace />;
  }

  // ✅ Valid session → render child route
  return <>{children}</>;
};

export default ProtectedRoute;
