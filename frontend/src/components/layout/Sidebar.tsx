import { NavLink } from 'react-router-dom';
import clsx from 'clsx';
import { useBranding } from '../../hooks/useBranding';
import { useAuthStore } from '../../store/authStore';
import {
  HomeIcon,
  BuildingOffice2Icon,
  MicrophoneIcon,
  MegaphoneIcon,
  ChartBarIcon,
  BoltIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline';

const nav = [
  { to: '/', label: 'Dashboard', icon: HomeIcon },
  { to: '/pipeline', label: 'Pipeline', icon: BoltIcon },
  { to: '/companies', label: 'Companies', icon: BuildingOffice2Icon },
  { to: '/agents', label: 'Voice Agents', icon: MicrophoneIcon },
  { to: '/campaigns', label: 'Campaigns', icon: MegaphoneIcon },
  { to: '/analytics', label: 'Analytics', icon: ChartBarIcon },
];

export function Sidebar() {
  const { data: branding } = useBranding();
  const user = useAuthStore((s) => s.user);
  const isAdmin = Boolean(user?.is_admin) || user?.role === 'admin';
  const menu = isAdmin
    ? [...nav, { to: '/settings', label: 'Settings', icon: Cog6ToothIcon }]
    : nav;
  return (
    <aside className="w-64 bg-display-black min-h-screen flex flex-col py-6 flex-shrink-0 border-r border-digital-white/10">
      <div className="px-6 mb-8">
        <div className="flex items-center gap-2">
          <span className="text-xl text-urgency-red">●</span>
          <span className="text-digital-white text-lg font-semibold tracking-[0.08em] uppercase font-sf-mono">
            {branding?.company_name ?? 'FRACTO'}
          </span>
        </div>
        <p className="text-steel-grey text-[11px] mt-1 font-sf-mono uppercase tracking-[0.05em]">
          Voice Agent Platform
        </p>
      </div>
      <nav className="flex-1 px-3 space-y-1">
        {menu.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2 rounded-pills text-xs font-semibold uppercase tracking-[0.03em] transition-colors font-proxima-nova',
                isActive
                  ? 'bg-white/10 text-white'
                  : 'text-steel-grey hover:bg-white/5 hover:text-white'
              )
            }
          >
            <Icon className="w-5 h-5 flex-shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
