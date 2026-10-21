import React, { createContext, useContext, useEffect, useState } from "react";
import { authApi } from "../api/endpoints";
import { User } from "../api/types";

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (token: string, user: User) => void;
  logout: () => Promise<void>;
  updateUser: (updatedUser: User) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem("campus_connect_user");
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem("campus_connect_token");
  });
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const login = (newToken: string, newUser: User) => {
    localStorage.setItem("campus_connect_token", newToken);
    localStorage.setItem("campus_connect_user", JSON.stringify(newUser));
    setToken(newToken);
    setUser(newUser);
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch {
      // Ignore network errors on logout
    } finally {
      localStorage.removeItem("campus_connect_token");
      localStorage.removeItem("campus_connect_user");
      setToken(null);
      setUser(null);
    }
  };

  const updateUser = (updatedUser: User) => {
    localStorage.setItem("campus_connect_user", JSON.stringify(updatedUser));
    setUser(updatedUser);
  };

  useEffect(() => {
    const verifySession = async () => {
      const storedToken = localStorage.getItem("campus_connect_token");
      if (storedToken) {
        try {
          const freshUser = await authApi.getMe();
          setUser(freshUser);
          localStorage.setItem("campus_connect_user", JSON.stringify(freshUser));
        } catch {
          // Token expired or invalid
          localStorage.removeItem("campus_connect_token");
          localStorage.removeItem("campus_connect_user");
          setToken(null);
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    verifySession();

    const handleAutoLogout = () => {
      setToken(null);
      setUser(null);
    };
    window.addEventListener("auth:logout", handleAutoLogout);
    return () => window.removeEventListener("auth:logout", handleAutoLogout);
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
