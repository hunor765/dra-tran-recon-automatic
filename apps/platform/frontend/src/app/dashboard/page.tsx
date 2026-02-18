"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BarChart3,
  Calendar,
  CheckCircle2,
  Clock,
  Database,
  History,
  RefreshCw,
  Server,
  XCircle,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

import { Button } from "@/components/red-kit/Button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/red-kit/Card";
import { Badge } from "@/components/red-kit/Badge";
import { PageSkeleton, Skeleton } from "@/components/ui/LoadingSkeleton";
import { api } from "@/lib/api/client";
import { cn } from "@/lib/utils";

// --- Types ---
interface SystemStatus {
  db: "connected" | "disconnected";
  api: "online" | "degraded";
  latency: number;
}

interface JobResult {
  match_rate: number;
  total_backend_value: number;
  total_ga4_value: number;
  missing_count: number;
  missing_ids: string[];
  ga4_records: number;
  backend_records: number;
}

interface Job {
  id: number;
  client_id: number;
  client_name?: string;
  status: "pending" | "running" | "completed" | "failed" | "retrying";
  last_run: string;
  result_summary: JobResult | null;
  logs: string | null;
  days: number;
  start_date: string | null;
  end_date: string | null;
  retry_count: number;
  max_retries: number;
}

interface ChartDataPoint {
  name: string;
  value: number;
  type: "match" | "missing" | "inflated";
}

export default function DashboardPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    db: "connected",
    api: "online",
    latency: 45,
  });

  // Fetch jobs on mount
  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  // Simulate System Heartbeat
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemStatus((prev) => ({
        ...prev,
        latency: Math.floor(Math.random() * (60 - 30) + 30),
      }));
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  async function fetchJobs() {
    try {
      const data = await api.getJobs({ limit: 10 });
      setJobs(data);
      
      // Auto-select the most recent completed job if none selected
      if (!selectedJob && data.length > 0) {
        const completedJob = data.find((j: Job) => j.status === "completed");
        if (completedJob) {
          setSelectedJob(completedJob);
        } else {
          setSelectedJob(data[0]);
        }
      } else if (selectedJob) {
        // Update selected job if it changed
        const updated = data.find((j: Job) => j.id === selectedJob.id);
        if (updated) {
          setSelectedJob(updated);
        }
      }
      
      setError(null);
    } catch (err) {
      console.error("Failed to fetch jobs:", err);
      setError("Failed to load jobs. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }

  function getChartData(job: Job): ChartDataPoint[] {
    if (!job.result_summary) return [];
    
    const { ga4_records, backend_records, missing_count } = job.result_summary;
    const matched = Math.max(0, backend_records - missing_count);
    
    return [
      { name: "Matched", value: matched, type: "match" },
      { name: "Missing (GA4)", value: missing_count, type: "missing" },
      { name: "Inflated", value: Math.max(0, ga4_records - matched), type: "inflated" },
    ];
  }

  function formatCurrency(val: number) {
    return new Intl.NumberFormat("ro-RO", {
      style: "currency",
      currency: "RON",
      maximumFractionDigits: 0,
    }).format(val);
  }

  function formatDate(dateStr: string) {
    return new Date(dateStr).toLocaleString("ro-RO", {
      dateStyle: "medium",
      timeStyle: "short",
    });
  }

  function getStatusBadge(status: string) {
    const variants: Record<string, "success" | "warning" | "error" | "info"> = {
      completed: "success",
      running: "info",
      pending: "info",
      retrying: "warning",
      failed: "error",
    };
    return <Badge variant={variants[status] || "info"}>{status.toUpperCase()}</Badge>;
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12" />
        <div className="grid lg:grid-cols-12 gap-6">
          <div className="lg:col-span-8">
            <Skeleton className="h-[400px]" />
          </div>
          <div className="lg:col-span-4">
            <Skeleton className="h-[400px]" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <XCircle size={48} className="text-red-500 mb-4" />
        <h2 className="heading-md mb-2">Error Loading Dashboard</h2>
        <p className="text-neutral-500 mb-6">{error}</p>
        <Button onClick={fetchJobs}>Retry</Button>
      </div>
    );
  }

  const hasJobs = jobs.length > 0;
  const latestCompleted = jobs.find((j) => j.status === "completed");
  const displayJob = selectedJob || latestCompleted;

  return (
    <div className="space-y-6">
      {/* --- System Status Bar --- */}
      <div className="flex items-center justify-between bg-white border border-neutral-200 p-3 sharp">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <div
              className={cn(
                "w-2 h-2 rounded-full",
                systemStatus.db === "connected"
                  ? "bg-emerald-500 animate-pulse"
                  : "bg-red-500"
              )}
            />
            <span className="text-xs font-bold uppercase tracking-wider text-neutral-500">
              Database
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div
              className={cn(
                "w-2 h-2 rounded-full",
                systemStatus.api === "online" ? "bg-emerald-500" : "bg-amber-500"
              )}
            />
            <span className="text-xs font-bold uppercase tracking-wider text-neutral-500">
              API Gateway
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Activity size={14} className="text-neutral-400" />
            <span className="text-xs font-mono text-neutral-500">
              {systemStatus.latency}ms
            </span>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => router.push("/dashboard/history")}
          >
            <History size={14} className="mr-2" /> View History
          </Button>
          <div className="text-xs font-mono text-neutral-400">v2.4.0-stable</div>
        </div>
      </div>

      {!hasJobs ? (
        // No jobs state
        <div className="flex flex-col items-center justify-center py-20">
          <Database size={48} className="text-neutral-300 mb-4" />
          <h2 className="heading-md mb-2">No Jobs Yet</h2>
          <p className="text-neutral-500 mb-6 text-center max-w-md">
            No reconciliation jobs have been run for your account yet. 
            Contact your administrator to schedule a job.
          </p>
        </div>
      ) : (
        <div className="grid lg:grid-cols-12 gap-6">
          {/* --- Main Panel (Left) --- */}
          <div className="lg:col-span-8 space-y-6">
            <Card variant="default" className="min-h-[400px]">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 size={18} className="text-revolt-red" />
                    RECONCILIATION RESULTS
                  </CardTitle>
                  <p className="body-sm text-neutral-500 mt-1">
                    {displayJob?.client_name || "Client"} -{" "}
                    {displayJob?.start_date
                      ? `${displayJob.start_date} to ${displayJob.end_date || "today"}`
                      : `Last ${displayJob?.days || 30} days`}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {displayJob && getStatusBadge(displayJob.status)}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() =>
                      displayJob && router.push(`/dashboard/results/${displayJob.id}`)
                    }
                    disabled={!displayJob}
                  >
                    View Details <ArrowRight size={14} className="ml-2" />
                  </Button>
                </div>
              </CardHeader>

              <CardContent>
                {displayJob?.status === "running" || displayJob?.status === "retrying" ? (
                  <div className="flex flex-col items-center justify-center py-20">
                    <div className="w-16 h-1 bg-neutral-100 overflow-hidden mb-6">
                      <div className="w-full h-full bg-revolt-red animate-progress-indeterminateOrigin" />
                    </div>
                    <h3 className="heading-sm mb-2">PROCESSING DATA</h3>
                    <div className="font-mono text-xs text-neutral-400 space-y-1 text-center">
                      <p>Job ID: {displayJob.id}</p>
                      <p>Attempt {displayJob.retry_count + 1} of {displayJob.max_retries + 1}</p>
                    </div>
                  </div>
                ) : displayJob?.status === "failed" ? (
                  <div className="flex flex-col items-center justify-center py-20">
                    <XCircle size={48} className="text-red-500 mb-4" />
                    <h3 className="heading-sm mb-2">JOB FAILED</h3>
                    <p className="text-sm text-neutral-500 mb-4 text-center max-w-md">
                      {displayJob.logs || "An error occurred during processing."}
                    </p>
                    {displayJob.can_retry && (
                      <Button
                        onClick={() => api.retryJob(displayJob.id).then(fetchJobs)}
                      >
                        <RefreshCw size={14} className="mr-2" /> Retry Job
                      </Button>
                    )}
                  </div>
                ) : displayJob?.result_summary ? (
                  <div className="grid md:grid-cols-2 gap-8 h-full">
                    <div className="space-y-6">
                      <div>
                        <span className="label text-neutral-400">Match Rate</span>
                        <div className="flex items-baseline gap-2">
                          <span className="text-5xl font-black tracking-tighter text-neutral-900">
                            {displayJob.result_summary.match_rate.toFixed(1)}%
                          </span>
                          <Badge
                            variant={
                              displayJob.result_summary.match_rate > 90
                                ? "success"
                                : "warning"
                            }
                          >
                            {displayJob.result_summary.match_rate < 90
                              ? "ATTENTION NEEDED"
                              : "OPTIMAL"}
                          </Badge>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 bg-neutral-50 border border-neutral-100 sharp">
                          <span className="label-sm text-neutral-500">Missing Rev</span>
                          <div className="text-xl font-bold text-revolt-red mt-1">
                            {formatCurrency(
                              Math.max(
                                0,
                                displayJob.result_summary.total_backend_value -
                                  displayJob.result_summary.total_ga4_value
                              )
                            )}
                          </div>
                        </div>
                        <div className="p-4 bg-neutral-50 border border-neutral-100 sharp">
                          <span className="label-sm text-neutral-500">Total Trans</span>
                          <div className="text-xl font-bold text-neutral-900 mt-1">
                            {displayJob.result_summary.backend_records.toLocaleString()}
                          </div>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-neutral-500">GA4 Records</span>
                          <span className="font-mono">
                            {displayJob.result_summary.ga4_records.toLocaleString()}
                          </span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-neutral-500">Backend Records</span>
                          <span className="font-mono">
                            {displayJob.result_summary.backend_records.toLocaleString()}
                          </span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-neutral-500">Missing IDs</span>
                          <span className="font-mono text-revolt-red">
                            {displayJob.result_summary.missing_count.toLocaleString()}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="h-[200px] w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={getChartData(displayJob)}>
                          <XAxis
                            dataKey="name"
                            fontSize={10}
                            tickLine={false}
                            axisLine={false}
                          />
                          <Tooltip
                            cursor={{ fill: "#f4f4f5" }}
                            contentStyle={{
                              borderRadius: 0,
                              border: "1px solid #e4e4e7",
                              boxShadow: "none",
                            }}
                          />
                          <Bar dataKey="value" radius={[2, 2, 0, 0]}>
                            {getChartData(displayJob).map((entry, index) => (
                              <Cell
                                key={`cell-${index}`}
                                fill={
                                  entry.type === "match"
                                    ? "#10b981"
                                    : entry.type === "missing"
                                    ? "#dd3333"
                                    : "#f59e0b"
                                }
                              />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-20">
                    <Clock size={48} className="text-neutral-300 mb-4" />
                    <h3 className="heading-sm mb-2">NO RESULTS YET</h3>
                    <p className="text-neutral-500">This job is still processing.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* --- Sidebar Panel (Right) --- */}
          <div className="lg:col-span-4 space-y-6">
            {/* Recent Jobs List */}
            <Card variant="outlined" className="h-[400px] flex flex-col">
              <CardHeader className="pb-2 border-b border-neutral-100">
                <CardTitle className="text-sm flex items-center gap-2">
                  <History size={14} />
                  RECENT JOBS
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-1 overflow-auto p-0">
                <div className="divide-y divide-neutral-100">
                  {jobs.map((job) => (
                    <button
                      key={job.id}
                      onClick={() => setSelectedJob(job)}
                      className={cn(
                        "w-full p-4 text-left hover:bg-neutral-50 transition-colors",
                        selectedJob?.id === job.id && "bg-neutral-50 border-l-2 border-l-revolt-red"
                      )}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-mono text-xs text-neutral-400">
                          #{job.id}
                        </span>
                        {getStatusBadge(job.status)}
                      </div>
                      <div className="text-sm font-medium text-neutral-900">
                        {job.start_date
                          ? `${job.start_date} to ${job.end_date || "today"}`
                          : `Last ${job.days} days`}
                      </div>
                      <div className="flex items-center gap-3 mt-2 text-xs text-neutral-500">
                        <span className="flex items-center gap-1">
                          <Calendar size={12} />
                          {formatDate(job.last_run)}
                        </span>
                        {job.result_summary && (
                          <span className="flex items-center gap-1">
                            <CheckCircle2 size={12} className="text-emerald-500" />
                            {job.result_summary.match_rate.toFixed(1)}%
                          </span>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Activity Log / Status */}
            <Card variant="outlined" className="bg-neutral-900 border-neutral-900 text-white">
              <CardHeader className="border-white/10 pb-2">
                <CardTitle className="text-white flex items-center gap-2 text-sm">
                  <Server size={14} className="text-revolt-red" />
                  JOB STATUS
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 pt-4">
                {displayJob?.logs ? (
                  <div className="font-mono text-xs text-neutral-400 whitespace-pre-wrap">
                    {displayJob.logs}
                  </div>
                ) : (
                  <>
                    <div className="flex items-start gap-3 p-3 bg-white/5 border border-white/10 sharp">
                      <CheckCircle2 size={16} className="text-emerald-500 mt-0.5" />
                      <div>
                        <div className="text-xs font-bold text-white uppercase">Latest Job</div>
                        <div className="text-[10px] text-neutral-400 mt-1">
                          {displayJob?.status === "completed"
                            ? `Job #${displayJob.id} completed successfully`
                            : displayJob?.status === "failed"
                            ? `Job #${displayJob.id} failed`
                            : `Job #${displayJob.id} is ${displayJob?.status}`}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-start gap-3 p-3 bg-white/5 border border-white/10 sharp">
                      <Database size={16} className="text-blue-400 mt-0.5" />
                      <div>
                        <div className="text-xs font-bold text-white uppercase">Data Sources</div>
                        <div className="text-[10px] text-neutral-400 mt-1">
                          GA4 + Backend sync active
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
