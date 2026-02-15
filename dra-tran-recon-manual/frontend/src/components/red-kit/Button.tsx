"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "outline" | "ghost" | "destructive";
  size?: "sm" | "md" | "lg";
  children: React.ReactNode;
}

export function Button({
  variant = "primary",
  size = "md",
  className,
  children,
  ...props
}: ButtonProps) {
  const baseStyles = cn(
    "inline-flex items-center justify-center",
    "font-bold uppercase tracking-widest text-xs", // More premium typography
    "transition-all duration-200 ease-out",
    "focus:outline-none focus:ring-1 focus:ring-revolt-red focus:ring-offset-1",
    "disabled:opacity-50 disabled:cursor-not-allowed",
    "active:scale-95", // Micro-interaction
    "sharp" // Global utility
  );

  const variants = {
    primary: cn(
      "bg-revolt-red text-white border border-revolt-red",
      "hover:bg-revolt-red-dark hover:border-revolt-red-dark",
      "shadow-sm hover:shadow-md" // Subtle lift
    ),
    outline: cn(
      "bg-transparent text-neutral-900 border border-neutral-200",
      "hover:border-revolt-red hover:text-revolt-red",
      "hover:bg-neutral-50"
    ),
    ghost: cn(
      "bg-transparent text-neutral-600 border border-transparent",
      "hover:text-neutral-900 hover:bg-neutral-100"
    ),
    destructive: cn(
      "bg-white text-revolt-red border border-revolt-red",
      "hover:bg-revolt-red hover:text-white"
    ),
  };

  const sizes = {
    sm: "px-4 py-2 text-xs",
    md: "px-6 py-3 text-sm",
    lg: "px-8 py-4 text-base",
  };

  return (
    <button
      className={cn(baseStyles, variants[variant], sizes[size], className)}
      {...props}
    >
      {children}
    </button>
  );
}
