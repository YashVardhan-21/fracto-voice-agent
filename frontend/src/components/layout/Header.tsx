import { useAuthStore } from '../../store/authStore';
import { Button } from '../ui/Button';

export function Header({ title }: { title: string }) {
  const { user, logout } = useAuthStore();
  return (
    <header className="bg-control-panel-grey border-b border-graphite px-8 py-4 flex items-center justify-between flex-shrink-0">
      <h1 className="text-xl font-bold text-obsidian-grey uppercase tracking-[0.08em] font-proxima-nova">
        {title}
      </h1>
      <div className="flex items-center gap-4">
        <span className="text-xs text-slate-blue uppercase tracking-[0.05em] font-sf-mono">
          {user?.full_name}
        </span>
        <Button variant="ghost" size="sm" onClick={logout}>
          Sign out
        </Button>
      </div>
    </header>
  );
}
