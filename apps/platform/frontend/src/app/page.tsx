import Link from "next/link";
import { ArrowRight, ShieldCheck, Zap, BarChart3 } from "lucide-react";
import { Button } from "@/components/red-kit/Button";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navbar */}
      <nav className="fixed top-0 inset-x-0 z-50 bg-white border-b border-neutral-200">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-revolt-red flex items-center justify-center text-white font-black text-sm">
              D
            </div>
            <span className="font-bold text-lg tracking-tight text-neutral-900">
              DRA PLATFORM
            </span>
          </div>
          <div>
            <Link href="/login">
              <Button variant="outline" size="sm">
                Client Login <ArrowRight size={14} />
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-24">
        <div className="max-w-7xl mx-auto px-6">
          <div className="max-w-3xl">
            {/* Status Badge */}
            <div className="inline-flex items-center gap-3 px-4 py-2 border border-neutral-200 sharp mb-8">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full sharp bg-revolt-red opacity-75"></span>
                <span className="relative inline-flex sharp h-2 w-2 bg-revolt-red"></span>
              </span>
              <span className="label text-neutral-600">
                Live Transaction Monitoring
              </span>
            </div>

            {/* Headline */}
            <h1 className="heading-xl text-neutral-900 mb-6">
              RECOVER LOST
              <br />
              <span className="text-revolt-red">REVENUE.</span>
            </h1>

            <p className="body-lg text-neutral-500 mb-10 max-w-2xl">
              The automated reconciliation platform for high-volume e-commerce.
              Detect untracked orders between GA4, Shopify, and your Backend in
              real-time.
            </p>

            <div className="flex flex-col sm:flex-row gap-4">
              <Link href="/login">
                <Button size="lg">
                  Access Portal <ArrowRight size={20} />
                </Button>
              </Link>
              <Button variant="outline" size="lg" disabled>
                Book Demo
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-24 bg-neutral-50 border-t border-neutral-200">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-3 gap-px bg-neutral-200">
            {/* Feature 1 */}
            <div className="bg-white p-8 group">
              <div className="w-12 h-12 border border-neutral-200 flex items-center justify-center mb-6 group-hover:border-revolt-red transition-colors sharp">
                <BarChart3
                  size={24}
                  className="text-neutral-400 group-hover:text-revolt-red transition-colors"
                />
              </div>
              <h3 className="heading-sm text-neutral-900 mb-3">
                REAL-TIME ANALYTICS
              </h3>
              <p className="body-sm text-neutral-500">
                Monitor match rates and discrepancy trends as they happen with
                our live dashboard.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-white p-8 group">
              <div className="w-12 h-12 border border-neutral-200 flex items-center justify-center mb-6 group-hover:border-revolt-red transition-colors sharp">
                <Zap
                  size={24}
                  className="text-neutral-400 group-hover:text-revolt-red transition-colors"
                />
              </div>
              <h3 className="heading-sm text-neutral-900 mb-3">
                INSTANT ALERTS
              </h3>
              <p className="body-sm text-neutral-500">
                Get notified immediately when data drift exceeds your defined
                thresholds.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-white p-8 group">
              <div className="w-12 h-12 border border-neutral-200 flex items-center justify-center mb-6 group-hover:border-revolt-red transition-colors sharp">
                <ShieldCheck
                  size={24}
                  className="text-neutral-400 group-hover:text-revolt-red transition-colors"
                />
              </div>
              <h3 className="heading-sm text-neutral-900 mb-3">
                BANK-GRADE SECURITY
              </h3>
              <p className="body-sm text-neutral-500">
                Your data is encrypted at rest and in transit. SOC2 compliant
                infrastructure.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-24 border-t border-neutral-200">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-px bg-neutral-200">
            <div className="bg-white p-8 text-center">
              <div className="text-4xl font-black text-neutral-900 tracking-tight mb-2">
                99.9%
              </div>
              <div className="label text-neutral-400">UPTIME</div>
            </div>
            <div className="bg-white p-8 text-center">
              <div className="text-4xl font-black text-revolt-red tracking-tight mb-2">
                24/7
              </div>
              <div className="label text-neutral-400">MONITORING</div>
            </div>
            <div className="bg-white p-8 text-center">
              <div className="text-4xl font-black text-neutral-900 tracking-tight mb-2">
                50M+
              </div>
              <div className="label text-neutral-400">TRANSACTIONS</div>
            </div>
            <div className="bg-white p-8 text-center">
              <div className="text-4xl font-black text-neutral-900 tracking-tight mb-2">
                &lt;1s
              </div>
              <div className="label text-neutral-400">DETECTION TIME</div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-neutral-900 py-12">
        <div className="max-w-7xl mx-auto px-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-revolt-red flex items-center justify-center text-white font-black text-sm">
              D
            </div>
            <span className="font-bold text-lg tracking-tight text-white">
              DRA PLATFORM
            </span>
          </div>
          <div className="flex gap-8">
            <span className="label-sm text-neutral-500 hover:text-white transition-colors cursor-pointer">
              PRIVACY
            </span>
            <span className="label-sm text-neutral-500 hover:text-white transition-colors cursor-pointer">
              TERMS
            </span>
            <span className="label-sm text-neutral-500 hover:text-white transition-colors cursor-pointer">
              SUPPORT
            </span>
          </div>
        </div>
        <div className="max-w-7xl mx-auto px-6 mt-8 pt-8 border-t border-neutral-800">
          <p className="label-sm text-neutral-600">
            © 2026 DRA Platform. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
