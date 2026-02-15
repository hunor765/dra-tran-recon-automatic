"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  variant?: "default" | "outlined" | "filled";
}

export function Card({
  children,
  variant = "outlined",
  className,
  ...props
}: CardProps) {
  const variants = {
    default: "bg-white shadow-sm border border-neutral-100",
    outlined: "bg-white border border-neutral-200", // "Swiss" standard
    filled: "bg-neutral-50 border border-transparent",
  };

  return (
    <div
      className={cn(
        "sharp p-6 relative transition-all duration-200",
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export function CardHeader({ children, className, ...props }: CardHeaderProps) {
  return (
    <div
      className={cn("mb-4 pb-4 border-b border-neutral-100", className)}
      {...props}
    >
      {children}
    </div>
  );
}

interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  children: React.ReactNode;
}

export function CardTitle({ children, className, ...props }: CardTitleProps) {
  return (
    <h3
      className={cn("heading-sm text-neutral-900", className)}
      {...props}
    >
      {children}
    </h3>
  );
}

interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export function CardContent({
  children,
  className,
  ...props
}: CardContentProps) {
  return (
    <div className={cn("body text-neutral-600", className)} {...props}>
      {children}
    </div>
  );
}
