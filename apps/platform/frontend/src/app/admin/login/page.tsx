"use client";

import { createClient } from "@/lib/supabase/client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Lock, ArrowRight, Users } from "lucide-react";
import { Button } from "@/components/red-kit/Button";
import { Input } from "@/components/red-kit/Input";
import { Card } from "@/components/red-kit/Card";
import Link from "next/link";

export default function AdminLoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const router = useRouter();
  const supabase = createClient();

  const handleAdminLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

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

  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-900">
      <div className="w-full max-w-md px-6">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="w-16 h-16 bg-revolt-red flex items-center justify-center mx-auto mb-6 text-white">
            <Lock size={28} strokeWidth={2.5} />
          </div>
          <h1 className="heading-lg text-white mb-2">DRA PLATFORM</h1>
          <p className="body text-neutral-400">Administrator Access</p>
        </div>

        <Card variant="outlined" className="p-8 bg-neutral-800 border-neutral-700">
          {/* Error */}
          {error && (
            <div className="mb-6 p-4 border-l-2 border-revolt-red bg-red-950/50">
              <p className="text-sm font-semibold text-red-400 uppercase tracking-wide">
                {error}
              </p>
            </div>
          )}

          {/* Admin Form */}
          <form onSubmit={handleAdminLogin} className="space-y-6">
            <Input
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@dra.com"
              className="bg-neutral-700 border-neutral-600 text-white placeholder:text-neutral-400"
              labelClassName="text-neutral-300"
              required
            />
            <Input
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="bg-neutral-700 border-neutral-600 text-white placeholder:text-neutral-400"
              labelClassName="text-neutral-300"
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
              <ArrowRight size={18} />
            </Button>
          </form>
        </Card>

        {/* Client Link */}
        <div className="mt-6 text-center">
          <Link
            href="/login"
            className="inline-flex items-center gap-2 text-xs text-neutral-500 hover:text-neutral-300 uppercase tracking-wide transition-colors"
          >
            <Users size={14} />
            Client Portal
          </Link>
        </div>

        {/* Footer */}
        <p className="text-center mt-8 text-xs text-neutral-600 uppercase tracking-wide">
          © 2026 DRA Platform. All rights reserved.
        </p>
      </div>
    </div>
  );
}
