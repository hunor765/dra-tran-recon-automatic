"use client";

import { useState, useEffect } from "react";
import {
  Upload,
  FileCheck,
  AlertTriangle,
  ArrowRight,
  Database,
  Activity,
  Server,
  RefreshCw,
  CheckCircle2,
  XCircle,
  FileText
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell
} from "recharts";

import { Button } from "@/components/red-kit/Button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/red-kit/Card";
import { Badge } from "@/components/red-kit/Badge";
import { cn } from "@/lib/utils";

// --- Types ---
interface SystemStatus {
  db: "connected" | "disconnected";
  api: "online" | "degraded";
  latency: number;
}

interface AnalysisResult {
  matchRate: number;
  totalBackend: number;
  totalGa4: number;
  discrepancyValue: number;
  chartData: Array<{ name: string; value: number; type: "match" | "missing" | "inflated" }>;
  logs: Array<{ time: string; level: "info" | "warn" | "error"; msg: string }>;
}

export default function DashboardPage() {
  const [step, setStep] = useState<"upload" | "processing" | "complete">("upload");
  const [ga4File, setGa4File] = useState<File | null>(null);
  const [backendFile, setBackendFile] = useState<File | null>(null);
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({ db: "connected", api: "online", latency: 45 });
  const [result, setResult] = useState<AnalysisResult | null>(null);

  // Simulate System Heartbeat
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemStatus(prev => ({
        ...prev,
        latency: Math.floor(Math.random() * (60 - 30) + 30)
      }));
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleAnalyze = () => {
    if (!ga4File || !backendFile) return;
    setStep("processing");

    // Simulate complex processing
    setTimeout(() => {
      setResult({
        matchRate: 86.4,
        totalBackend: 84979,
        totalGa4: 52127,
        discrepancyValue: 11483607,
        chartData: [
          { name: "Matched", value: 45333, type: "match" },
          { name: "Missing (GA4)", value: 6794, type: "missing" },
          { name: "Inflated", value: 5967, type: "inflated" },
        ],
        logs: [
          { time: "14:32:01", level: "info", msg: "Initiating reconciliation protocol..." },
          { time: "14:32:02", level: "info", msg: "Parsed backend_orders.csv (84,979 rows)" },
          { time: "14:32:02", level: "warn", msg: "Detected 43 duplicate transaction IDs" },
          { time: "14:32:03", level: "info", msg: "Parsed ga4_export.csv (52,127 rows)" },
          { time: "14:32:05", level: "error", msg: "Gateway 'LeanPay' shows 100% failure rate" },
          { time: "14:32:06", level: "info", msg: "Reconciliation complete. Generating report." },
        ]
      });
      setStep("complete");
    }, 2800);
  };

  const formatCurrency = (val: number) =>
    new Intl.NumberFormat('ro-RO', { style: 'currency', currency: 'RON', maximumFractionDigits: 0 }).format(val);

  return (
    <div className="space-y-6">
      {/* --- System Status Bar --- */}
      <div className="flex items-center justify-between bg-white border border-neutral-200 p-3 sharp">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <div className={cn("w-2 h-2 rounded-full", systemStatus.db === "connected" ? "bg-emerald-500 animate-pulse" : "bg-red-500")} />
            <span className="text-xs font-bold uppercase tracking-wider text-neutral-500">Database</span>
          </div>
          <div className="flex items-center gap-2">
            <div className={cn("w-2 h-2 rounded-full", systemStatus.api === "online" ? "bg-emerald-500" : "bg-amber-500")} />
            <span className="text-xs font-bold uppercase tracking-wider text-neutral-500">API Gateway</span>
          </div>
          <div className="flex items-center gap-2">
            <Activity size={14} className="text-neutral-400" />
            <span className="text-xs font-mono text-neutral-500">{systemStatus.latency}ms</span>
          </div>
        </div>
        <div className="text-xs font-mono text-neutral-400">v2.4.0-stable</div>
      </div>

      <div className="grid lg:grid-cols-12 gap-6">

        {/* --- Main Control Panel (Left/Top) --- */}
        <div className="lg:col-span-8 space-y-6">
          <Card variant="default" className="min-h-[400px]">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Database size={18} className="text-revolt-red" />
                  DATA INGESTION
                </CardTitle>
                <p className="body-sm text-neutral-500 mt-1">Upload raw transaction logs for analysis</p>
              </div>
              {step === "complete" && (
                <Button variant="outline" size="sm" onClick={() => setStep("upload")}>
                  <RefreshCw size={14} className="mr-2" /> New Audit
                </Button>
              )}
            </CardHeader>

            <CardContent>
              {step === "upload" && (
                <div className="grid md:grid-cols-2 gap-4">
                  {/* GA4 Zone */}
                  <label className={cn(
                    "group relative flex flex-col items-center justify-center p-8 border-2 border-dashed border-neutral-200 transition-all cursor-pointer hover:border-revolt-red hover:bg-neutral-50 sharp",
                    ga4File ? "border-solid border-neutral-900 bg-neutral-50" : ""
                  )}>
                    <input type="file" className="hidden" onChange={(e) => setGa4File(e.target.files?.[0] || null)} />
                    <div className="mb-4 p-3 bg-white border border-neutral-100 group-hover:border-revolt-red transition-colors sharp">
                      <FileText size={24} className={ga4File ? "text-neutral-900" : "text-neutral-400 group-hover:text-revolt-red"} />
                    </div>
                    <span className="text-sm font-bold uppercase tracking-wide text-neutral-900">
                      {ga4File ? ga4File.name : "GA4 Export"}
                    </span>
                    <span className="text-xs text-neutral-400 mt-1">.csv, .json</span>
                    {ga4File && <CheckCircle2 size={16} className="absolute top-2 right-2 text-emerald-500" />}
                  </label>

                  {/* Backend Zone */}
                  <label className={cn(
                    "group relative flex flex-col items-center justify-center p-8 border-2 border-dashed border-neutral-200 transition-all cursor-pointer hover:border-revolt-red hover:bg-neutral-50 sharp",
                    backendFile ? "border-solid border-neutral-900 bg-neutral-50" : ""
                  )}>
                    <input type="file" className="hidden" onChange={(e) => setBackendFile(e.target.files?.[0] || null)} />
                    <div className="mb-4 p-3 bg-white border border-neutral-100 group-hover:border-revolt-red transition-colors sharp">
                      <Server size={24} className={backendFile ? "text-neutral-900" : "text-neutral-400 group-hover:text-revolt-red"} />
                    </div>
                    <span className="text-sm font-bold uppercase tracking-wide text-neutral-900">
                      {backendFile ? backendFile.name : "Backend Logs"}
                    </span>
                    <span className="text-xs text-neutral-400 mt-1">.csv, .xlsx</span>
                    {backendFile && <CheckCircle2 size={16} className="absolute top-2 right-2 text-emerald-500" />}
                  </label>

                  <div className="md:col-span-2 mt-4 flex justify-end">
                    <Button onClick={handleAnalyze} disabled={!ga4File || !backendFile}>
                      INITIALIZE RECONCILIATION <ArrowRight size={16} className="ml-2" />
                    </Button>
                  </div>
                </div>
              )}

              {step === "processing" && (
                <div className="flex flex-col items-center justify-center py-20">
                  <div className="w-16 h-1 bg-neutral-100 overflow-hidden mb-6">
                    <div className="w-full h-full bg-revolt-red animate-progress-indeterminateOrigin" />
                  </div>
                  <h3 className="heading-sm mb-2">PROCESSING DATA STREAM</h3>
                  <div className="font-mono text-xs text-neutral-400 space-y-1 text-center">
                    <p>Hash: 8a9f...e21d</p>
                    <p>Indexing {Math.floor(Math.random() * 10000)} records...</p>
                  </div>
                </div>
              )}

              {step === "complete" && result && (
                <div className="grid md:grid-cols-2 gap-8 h-full">
                  <div className="space-y-6">
                    <div>
                      <span className="label text-neutral-400">Match Rate</span>
                      <div className="flex items-baseline gap-2">
                        <span className="text-5xl font-black tracking-tighter text-neutral-900">{result.matchRate}%</span>
                        <Badge variant={result.matchRate > 90 ? "success" : "warning"}>
                          {result.matchRate < 90 ? "ATTENTION NEEDED" : "OPTIMAL"}
                        </Badge>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 bg-neutral-50 border border-neutral-100 sharp">
                        <span className="label-sm text-neutral-500">Missing Rev</span>
                        <div className="text-xl font-bold text-revolt-red mt-1">{formatCurrency(result.discrepancyValue)}</div>
                      </div>
                      <div className="p-4 bg-neutral-50 border border-neutral-100 sharp">
                        <span className="label-sm text-neutral-500">Total Trans</span>
                        <div className="text-xl font-bold text-neutral-900 mt-1">{result.totalBackend.toLocaleString()}</div>
                      </div>
                    </div>
                  </div>

                  <div className="h-[200px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={result.chartData}>
                        <XAxis dataKey="name" fontSize={10} tickLine={false} axisLine={false} />
                        <Tooltip
                          cursor={{ fill: '#f4f4f5' }}
                          contentStyle={{ borderRadius: 0, border: '1px solid #e4e4e7', boxShadow: 'none' }}
                        />
                        <Bar dataKey="value" radius={[2, 2, 0, 0]}>
                          {result.chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.type === 'match' ? '#10b981' : entry.type === 'missing' ? '#dd3333' : '#f59e0b'} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* --- Sidebar Panel (Right) --- */}
        <div className="lg:col-span-4 space-y-6">
          {/* Critical Alerts */}
          <Card variant="outlined" className="bg-neutral-900 border-neutral-900 text-white">
            <CardHeader className="border-white/10 pb-2">
              <CardTitle className="text-white flex items-center gap-2 text-sm">
                <AlertTriangle size={16} className="text-revolt-red" />
                SYSTEM ALERTS
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 pt-4">
              <div className="flex items-start gap-3 p-3 bg-white/5 border border-white/10 sharp">
                <XCircle size={16} className="text-revolt-red mt-0.5" />
                <div>
                  <div className="text-xs font-bold text-white uppercase">Gateway Timeout</div>
                  <div className="text-[10px] text-neutral-400 mt-1">LeanPay provider failed to respond in 450 transactions.</div>
                </div>
              </div>
              <div className="flex items-start gap-3 p-3 bg-white/5 border border-white/10 sharp">
                <AlertTriangle size={16} className="text-amber-500 mt-0.5" />
                <div>
                  <div className="text-xs font-bold text-white uppercase">High Refund Rate</div>
                  <div className="text-[10px] text-neutral-400 mt-1">BTDirect showing 15% refund anomalies.</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Activity Log */}
          <Card variant="outlined" className="h-[300px] flex flex-col">
            <CardHeader className="pb-2 border-b border-neutral-100">
              <CardTitle className="text-sm">PROCESS TERMINAL</CardTitle>
            </CardHeader>
            <CardContent className="flex-1 overflow-auto bg-neutral-50 p-4 font-mono text-xs">
              {step === "upload" ? (
                <div className="text-neutral-400 italic">Waiting for input stream...</div>
              ) : step === "processing" ? (
                <div className="space-y-1">
                  <div className="text-neutral-500">{">"} System ready</div>
                  <div className="text-neutral-500">{">"} Upload received</div>
                  <div className="text-revolt-red animate-pulse">{">"} Processing batch...</div>
                </div>
              ) : (
                <div className="space-y-2">
                  {result?.logs.map((log, i) => (
                    <div key={i} className="flex gap-2">
                      <span className="text-neutral-400">[{log.time}]</span>
                      <span className={cn(
                        log.level === "error" ? "text-revolt-red font-bold" :
                          log.level === "warn" ? "text-amber-600" : "text-emerald-600"
                      )}>
                        {log.msg}
                      </span>
                    </div>
                  ))}
                  <div className="text-neutral-500 mt-2 border-t border-neutral-200 pt-2">{">"} Process finished.</div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

      </div>
    </div>
  );
}
