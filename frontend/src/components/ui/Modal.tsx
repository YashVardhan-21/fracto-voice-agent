import { XMarkIcon } from '@heroicons/react/24/outline';

interface Props {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export function Modal({ open, onClose, title, children }: Props) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-display-black/80 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-display-black border border-digital-white/20 rounded-lg shadow-subtle-2 p-6 w-full max-w-lg mx-4 z-10">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-[12px] uppercase tracking-[0.08em] font-sf-mono text-digital-white">
            {title}
          </h2>
          <button
            onClick={onClose}
            className="text-steel-grey hover:text-urgency-red transition-colors p-1"
          >
            <XMarkIcon className="w-4 h-4" />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
