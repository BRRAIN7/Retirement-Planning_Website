import React, { useState, FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import api from "./api"; // your axios instance
import useAutoRedirect from "./useAutoRedirect";
interface FormData {
  username: string;
  password: string;
}

interface ApiResponse {
  token: string;
  newUser: boolean;
}

const AuthPage: React.FC = () => {
  const [isSignup, setIsSignup] = useState<boolean>(false);
  const [form, setForm] = useState<FormData>({ username: "", password: "" });
  const [error, setError] = useState<string>("");
  const navigate = useNavigate();
  useAutoRedirect();
  // fallback credentials for demo
  const DEMO_USERS: Record<string, string> = {
    "demo@example.com": "1234",
    "test@finwise.com": "pass123",
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");

    try {
      const endpoint = isSignup ? "/register/" : "/login/";

      // send only username + password
      const payload = {
        username: form.username,
        password: form.password,
      };

      const res = await api.post<ApiResponse>(endpoint, payload);

      localStorage.setItem("token", res.data.token);
      localStorage.setItem("username", form.username);

      if (res.data.newUser) navigate("/setup");
      else navigate("/chat");
    } catch (err: any) {
      console.warn("Backend unavailable:", err.message);

      if (!isSignup) {
        const match =
          DEMO_USERS[form.username] &&
          DEMO_USERS[form.username] === form.password;

        if (match) {
          localStorage.setItem("token", "demo-token-" + Date.now());
          localStorage.setItem("username", form.username);
          navigate("/chat");
          return;
        }

        setError("Invalid credentials (demo or backend)");
        return;
      }

      if (form.username && form.password) {
        localStorage.setItem("token", "demo-token-" + Date.now());
        localStorage.setItem("username", form.username);
        navigate("/setup");
        return;
      }

      setError("Please fill in all fields for signup");
    }
  };


  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <form
        onSubmit={handleSubmit}
        className="bg-gray-800 p-8 rounded-xl w-96 text-white shadow-lg"
      >
        <h2 className="text-2xl mb-4 font-bold text-center">
          {isSignup ? "Create Account" : "Login"}
        </h2>

        {isSignup && (
          <input
            type="text"
            name="name"
            placeholder="Full Name"
            onChange={handleChange}
            className="w-full p-2 mb-3 bg-gray-700 rounded"
          />
        )}

        <input
          type="text"
          name="username"
          placeholder="Username"
          value={form.username}
          onChange={handleChange}
          className="w-full p-2 mb-3 bg-gray-700 rounded"
          required
        />

        <input
          type="password"
          name="password"
          placeholder="Password"
          value={form.password}
          onChange={handleChange}
          className="w-full p-2 mb-3 bg-gray-700 rounded"
          required
        />

        {error && <p className="text-red-400 mb-3 text-sm">{error}</p>}

        <button
          type="submit"
          className="w-full bg-blue-600 py-2 rounded font-medium hover:bg-blue-700 transition"
        >
          {isSignup ? "Sign Up" : "Login"}
        </button>

        <p className="mt-4 text-sm text-gray-400 text-center">
          {isSignup ? "Already have an account?" : "Don't have an account?"}{" "}
          <button
            type="button"
            onClick={() => {
              setIsSignup(!isSignup);
              setError("");
            }}
            className="text-blue-400 hover:underline"
          >
            {isSignup ? "Login" : "Sign Up"}
          </button>
        </p>

        {!isSignup && (
          <div className="mt-4 text-xs text-gray-500 text-center">
            💡 Demo credentials:
            <br />
            demo@example.com / 1234
            <br />
            test@finwise.com / pass123
          </div>
        )}
      </form>
    </div>
  );
};

export default AuthPage;
