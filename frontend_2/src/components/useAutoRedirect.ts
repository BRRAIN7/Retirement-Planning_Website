import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const useAutoRedirect = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      // ✅ If user already logged in, skip auth page
      navigate("/chat", { replace: true });
    }
  }, [navigate]);
};

export default useAutoRedirect;
