'use client';
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import api from '@/lib/api';
import { 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword, 
  sendPasswordResetEmail, 
  signOut as firebaseSignOut,
  onAuthStateChanged 
} from 'firebase/auth';
import { auth } from '@/lib/firebase';

export interface UserProfile {
  id: number;
  email: string;
  full_name: string;
  role: string;
  uid?: string;
}

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<any>;
  registerUser: (email: string, fullName: string, password: string, role?: string) => Promise<any>;
  logout: () => void;
  forgotPassword: (email: string) => Promise<any>;
  resetPassword: (email: string, resetToken: string, newPassword: string) => Promise<any>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    if (!auth) {
      const savedToken = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
      const savedUser = typeof window !== 'undefined' ? localStorage.getItem('user') : null;
      if (savedToken && savedUser) {
        try {
          setToken(savedToken);
          setUser(JSON.parse(savedUser));
          api.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`;
        } catch (e) {
          // Fallback demo user
        }
      } else {
        setUser({ id: 1, email: 'demo@financial.ai', full_name: 'Enterprise Financial Analyst', role: 'CFO' });
      }
      setLoading(false);
      return;
    }

    // Listen for Firebase Auth state changes
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        try {
          const idToken = await firebaseUser.getIdToken();
          setToken(idToken);
          api.defaults.headers.common['Authorization'] = `Bearer ${idToken}`;
          
          const profile: UserProfile = {
            id: 1,
            email: firebaseUser.email || 'user@captrix-ai.com',
            full_name: firebaseUser.displayName || firebaseUser.email?.split('@')[0] || 'Enterprise Analyst',
            role: 'CFO',
            uid: firebaseUser.uid
          };
          setUser(profile);
          if (typeof window !== 'undefined') {
            localStorage.setItem('token', idToken);
            localStorage.setItem('user', JSON.stringify(profile));
          }
        } catch (e) {
          console.error("Firebase auth token error:", e);
        }
      } else {
        const savedToken = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
        const savedUser = typeof window !== 'undefined' ? localStorage.getItem('user') : null;
        if (savedToken && savedUser) {
          try {
            setToken(savedToken);
            setUser(JSON.parse(savedUser));
            api.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`;
          } catch (e) {
            if (typeof window !== 'undefined') {
              localStorage.removeItem('token');
              localStorage.removeItem('user');
            }
          }
        } else {
          const demoUser: UserProfile = {
            id: 1,
            email: 'demo@financial.ai',
            full_name: 'Enterprise Financial Analyst',
            role: 'CFO'
          };
          setUser(demoUser);
        }
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const login = async (email: string, password: string) => {
    if (auth) {
      try {
        // Attempt Firebase Authentication first
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        const idToken = await userCredential.user.getIdToken();
        
        const userData: UserProfile = {
          id: 1,
          email: userCredential.user.email || email,
          full_name: userCredential.user.displayName || email.split('@')[0],
          role: 'CFO',
          uid: userCredential.user.uid
        };

        setToken(idToken);
        setUser(userData);
        if (typeof window !== 'undefined') {
          localStorage.setItem('token', idToken);
          localStorage.setItem('user', JSON.stringify(userData));
        }
        api.defaults.headers.common['Authorization'] = `Bearer ${idToken}`;

        try {
          await api.post('/api/auth/login', { email, password });
        } catch (e) {}

        return { access_token: idToken, user: userData };
      } catch (firebaseErr: any) {}
    }

    // Fallback to local DB Authentication router
    const res = await api.post('/api/auth/login', { email, password });
    const { access_token, user: userData } = res.data;

    setToken(access_token);
    setUser(userData);
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
    }
    return res.data;
  };

  const registerUser = async (email: string, fullName: string, password: string, role: string = 'Analyst') => {
    if (auth) {
      try {
        // Create Firebase Auth user
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        const idToken = await userCredential.user.getIdToken();

        const userData: UserProfile = {
          id: 1,
          email,
          full_name: fullName,
          role,
          uid: userCredential.user.uid
        };

        setToken(idToken);
        setUser(userData);
        if (typeof window !== 'undefined') {
          localStorage.setItem('token', idToken);
          localStorage.setItem('user', JSON.stringify(userData));
        }

        try {
          await api.post('/api/auth/register', { email, full_name: fullName, password, role });
        } catch (e) {}

        return { access_token: idToken, user: userData, message: "Account created successfully!" };
      } catch (firebaseErr: any) {}
    }

    // Fallback to local API database registration
    const res = await api.post('/api/auth/register', {
      email,
      full_name: fullName,
      password,
      role
    });
    const { access_token, user: userData } = res.data;

    setToken(access_token);
    setUser(userData);
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
    }
    return res.data;
  };

  const logout = async () => {
    if (auth) {
      try {
        await firebaseSignOut(auth);
      } catch (e) {}
    }
    setToken(null);
    setUser(null);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  };

  const forgotPassword = async (email: string) => {
    if (auth) {
      try {
        await sendPasswordResetEmail(auth, email);
        return { message: `Password reset email dispatched to ${email}. Check your inbox!`, email };
      } catch (e) {}
    }

    const res = await api.post('/api/auth/forgot-password', { email });
    return res.data;
  };

  const resetPassword = async (email: string, resetToken: string, newPassword: string) => {
    const res = await api.post('/api/auth/reset-password', {
      email,
      reset_token: resetToken,
      new_password: newPassword
    });
    return res.data;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        registerUser,
        logout,
        forgotPassword,
        resetPassword
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
