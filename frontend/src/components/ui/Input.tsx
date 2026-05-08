import clsx from 'clsx';
import { InputHTMLAttributes } from 'react';

interface Props extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function Input({ label, error, className, ...props }: Props) {
  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label className="text-[11px] uppercase tracking-[0.05em] text-digital-white font-sf-mono">
          {label}
        </label>
      )}
      <input
        className={clsx(
          'rounded-buttons border bg-transparent px-4 py-2 text-[13px] text-digital-white',
          'placeholder:text-slate-blue focus:outline-none focus:ring-2 focus:ring-active-blue focus:ring-offset-0',
          error ? 'border-urgency-red' : 'border-steel-grey/50',
          className
        )}
        {...props}
      />
      {error && <p className="text-[11px] text-urgency-red font-sf-mono">{error}</p>}
    </div>
  );
}
