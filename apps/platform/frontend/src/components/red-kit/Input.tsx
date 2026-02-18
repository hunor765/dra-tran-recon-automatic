"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function Input({ label, error, className, ...props }: InputProps) {
  return (
    <div className="w-full">
      {label && (
        <label className="block label mb-2 text-neutral-600">
          {label}
        </label>
      )}
      <input
        className={cn(
          `
            w-full
            px-0 py-3
            bg-transparent
            border-0 border-b-2 border-neutral-200
            text-neutral-900
            placeholder:text-neutral-400
            focus:outline-none focus:border-revolt-red
            transition-colors duration-150
            sharp
          `,
          error && "border-revolt-red focus:border-revolt-red",
          className
        )}
        {...props}
      />
      {error && (
        <p className="mt-2 text-xs font-semibold text-revolt-red uppercase tracking-wide">
          {error}
        </p>
      )}
    </div>
  );
}
