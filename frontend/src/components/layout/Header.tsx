import { useAuthStore } from '../../store/authStore';
import { Button } from '../ui/Button';

export function Header({ title }: { title: string }) {
  const { user, logout } = useAuthStore();
  return (
    <header className="bg-white border-b border-gray-200 px-8 py-4 flex items-center justify-between flex-shrink-0">
      <h1 className="text-xl font-semibold text-gray-900">{title}</h1>
      <div className="flex items-center gap-4">
        <span className="text-sm text-gray-500">{user?.full_name}</span>
        <Button variant="ghost" size="sm" onClick={logout}>
          Sign out
        </Button>
      </div>
    </header>
  );
}
