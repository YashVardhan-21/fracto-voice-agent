import clsx from 'clsx';

const variants: Record<string, string> = {
  pending:      'border-slate-blue/60   text-slate-blue',
  analyzing:    'border-active-blue/60  text-active-blue',
  prompt_ready: 'border-graphite/60     text-graphite',
  agent_created:'border-steel-grey/60   text-steel-grey',
  active:       'border-digital-white/40 text-digital-white',
  draft:        'border-steel-grey/40   text-steel-grey',
  running:      'border-active-blue/60  text-active-blue',
  completed:    'border-digital-white/40 text-digital-white',
  paused:       'border-slate-blue/60   text-slate-blue',
  vapi_failed:  'border-urgency-red/60  text-urgency-red',
  opted_out:    'border-urgency-red/60  text-urgency-red',
};

interface Props {
  label: string;
  status?: string;
}

export function Badge({ label, status }: Props) {
  return (
    <span
      className={clsx(
        'inline-flex items-center px-2 py-0.5 rounded-buttons border text-[11px] font-sf-mono uppercase tracking-[0.04em]',
        variants[status ?? ''] ?? 'border-steel-grey/40 text-steel-grey'
      )}
    >
      {label}
    </span>
  );
}
