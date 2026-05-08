import clsx from 'clsx';
import { ButtonHTMLAttributes } from 'react';

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'liftoff';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
}

const variants = {
  primary:
    'bg-urgency-red text-digital-white rounded-buttons shadow-subtle-2 hover:opacity-95 focus:ring-urgency-red',
  secondary:
    'bg-display-black text-digital-white rounded-buttons border border-digital-white/20 hover:bg-display-black/90 focus:ring-active-blue',
  danger:
    'bg-urgency-red text-digital-white rounded-buttons shadow-subtle hover:opacity-90 focus:ring-urgency-red',
  ghost: 'bg-transparent text-obsidian-grey rounded-none px-0 py-0 hover:text-urgency-red focus:ring-graphite',
  liftoff:
    'bg-[var(--gradient-gradient-combustion)] text-digital-white rounded-full shadow-subtle-2 hover:brightness-105 focus:ring-urgency-red',
};

const sizes = {
  sm: 'px-2 py-0.5 text-[11px]',
  md: 'px-2 py-1 text-[12px]',
  lg: 'px-3 py-1.5 text-sm',
};

export function Button({
  variant = 'primary',
  size = 'md',
  loading,
  children,
  className,
  disabled,
  ...props
}: Props) {
  return (
    <button
      disabled={disabled || loading}
      className={clsx(
        'inline-flex items-center justify-center gap-2 font-semibold tracking-[0.02em] transition-all',
        'focus:outline-none focus:ring-2 focus:ring-offset-2',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        'font-proxima-nova',
        variants[variant],
        variant !== 'liftoff' && sizes[size],
        variant === 'liftoff' && 'h-28 w-28 text-lg',
        className
      )}
      {...props}
    >
      {loading && (
        <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      )}
      {children}
    </button>
  );
}
