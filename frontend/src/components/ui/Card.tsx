import clsx from 'clsx';

/** General content panel — flat rectangular card for forms, tables, sections. */
export function Card({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={clsx(
        'bg-display-black text-digital-white rounded-lg border border-digital-white/10 p-4',
        className
      )}
    >
      {children}
    </div>
  );
}

/** Stat display panel — rounded dark card with Doto pixel numbers. */
export function StatCard({
  label,
  value,
  sub,
}: {
  label: string;
  value: string | number;
  sub?: string;
}) {
  return (
    <div className="bg-display-black text-digital-white rounded-[40px] border border-digital-white/10 shadow-subtle-2 px-8 py-6 flex flex-col justify-between gap-3 min-h-40">
      <p className="text-[13px] uppercase tracking-[0.06em] text-slate-blue font-sf-mono leading-tight">{label}</p>
      <p className="text-[40px] sm:text-[52px] leading-none font-doto text-digital-white">{value}</p>
      {sub && <p className="text-[12px] text-steel-grey font-proxima-nova">{sub}</p>}
    </div>
  );
}
