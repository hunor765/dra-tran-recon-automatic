"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "success" | "warning" | "error" | "outline";
  children: React.ReactNode;
}

export function Badge({
  variant = "default",
  className,
  children,
  ...props
}: BadgeProps) {
  const variants = {
    default: "bg-neutral-900 text-white",
    success: "bg-neutral-900 text-white border-neutral-900",
    warning: "bg-white text-neutral-900 border-neutral-900",
    error: "bg-revolt-red text-white border-revolt-red",
    outline: "bg-transparent text-neutral-900 border-neutral-900",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center px-3 py-1 label-sm sharp border",
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}
