import clsx from 'clsx';

const variants: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  analyzing: 'bg-blue-100 text-blue-800',
  prompt_ready: 'bg-purple-100 text-purple-800',
  agent_created: 'bg-green-100 text-green-800',
  active: 'bg-green-100 text-green-800',
  draft: 'bg-gray-100 text-gray-800',
  running: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  paused: 'bg-yellow-100 text-yellow-800',
  vapi_failed: 'bg-red-100 text-red-800',
  opted_out: 'bg-red-100 text-red-800',
};

interface Props {
  label: string;
  status?: string;
}

export function Badge({ label, status }: Props) {
  return (
    <span
      className={clsx(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        variants[status ?? ''] ?? 'bg-gray-100 text-gray-800'
      )}
    >
      {label}
    </span>
  );
}
