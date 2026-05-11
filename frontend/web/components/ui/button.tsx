import type { ButtonHTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/utils";

type ButtonVariant = "primary" | "secondary" | "ghost";

const variantClass: Record<ButtonVariant, string> = {
  primary: "bg-gradient-to-r from-brand to-brand-accent text-white shadow-soft hover:opacity-90",
  secondary: "border border-white/60 bg-white/70 text-ink hover:bg-white/90",
  ghost: "text-ink-soft hover:text-ink hover:bg-white/40",
};

export function Button({
  className,
  children,
  variant = "primary",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  children: ReactNode;
}) {
  return (
    <button
      className={cn(
        "inline-flex h-11 items-center justify-center rounded-2xl px-5 text-sm font-semibold transition-all",
        variantClass[variant],
        className,
      )}
      {...props}
    >
      {children}
    </button>
  );
}

