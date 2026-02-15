"use client";

import { createClient } from "@/lib/supabase/client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Lock, Mail, ArrowRight } from "lucide-react";
import { Button } from "@/components/red-kit/Button";
import { Input } from "@/components/red-kit/Input";
import { Card } from "@/components/red-kit/Card";

export default function LoginPage() {
  const [mode, setMode] = useState<"client" | "admin">("client");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const router = useRouter();
  const supabase = createClient();

  const handleAdminLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      const { error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });
      if (error) throw error;
      router.push("/admin");
      router.refresh();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleClientLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      const { error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          shouldCreateUser: false,
        },
      });
      if (error) throw error;
      setMessage("Check your email for the login link!");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-50">
      <div className="w-full max-w-md px-6">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="w-16 h-16 bg-revolt-red flex items-center justify-center mx-auto mb-6 text-white">
            <Lock size={28} strokeWidth={2.5} />
          </div>
          <h1 className="heading-lg text-neutral-900 mb-2">DRA PLATFORM</h1>
          <p className="body text-neutral-500">Secure Access Portal</p>
        </div>

        <Card variant="outlined" className="p-8">
          {/* Toggle */}
          <div className="flex border border-neutral-200 mb-8 sharp">
            <button
              onClick={() => setMode("client")}
              className={`flex-1 py-3 text-xs font-semibold uppercase tracking-wide transition-colors duration-150 ${
                mode === "client"
                  ? "bg-neutral-900 text-white"
                  : "bg-white text-neutral-500 hover:text-neutral-900"
              }`}
            >
              Client Login
            </button>
            <button
              onClick={() => setMode("admin")}
              className={`flex-1 py-3 text-xs font-semibold uppercase tracking-wide transition-colors duration-150 ${
                mode === "admin"
                  ? "bg-neutral-900 text-white"
                  : "bg-white text-neutral-500 hover:text-neutral-900"
              }`}
            >
              Admin Login
            </button>
          </div>

          {/* Feedback */}
          {error && (
            <div className="mb-6 p-4 border-l-2 border-revolt-red bg-red-50">
              <p className="text-sm font-semibold text-revolt-red uppercase tracking-wide">
                {error}
              </p>
            </div>
          )}
          {message && (
            <div className="mb-6 p-4 border-l-2 border-neutral-900 bg-neutral-50">
              <Mail className="mb-2 text-neutral-900" size={24} />
              <p className="body-sm text-neutral-700">{message}</p>
            </div>
          )}

          {/* Client Form */}
          {mode === "client" && !message && (
            <form onSubmit={handleClientLogin} className="space-y-6">
              <Input
                label="Email Address"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                required
              />
              <Button
                type="submit"
                variant="primary"
                size="lg"
                className="w-full"
                disabled={loading}
              >
                {loading ? "Sending..." : "Send Magic Link"}{" "}
                <ArrowRight size={18} />
              </Button>
              <p className="text-xs text-center text-neutral-500 uppercase tracking-wide">
                We&apos;ll email you a secure link to log in instantly
              </p>
            </form>
          )}

          {/* Admin Form */}
          {mode === "admin" && (
            <form onSubmit={handleAdminLogin} className="space-y-6">
              <Input
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <Input
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <Button
                type="submit"
                variant="primary"
                size="lg"
                className="w-full"
                disabled={loading}
              >
                {loading ? "Signing in..." : "Sign In"}
              </Button>
            </form>
          )}
        </Card>

        {/* Footer */}
        <p className="text-center mt-8 text-xs text-neutral-400 uppercase tracking-wide">
          © 2026 DRA Platform. All rights reserved.
        </p>
      </div>
    </div>
  );
}
