import { NavLink } from 'react-router-dom';
import clsx from 'clsx';
import {
  HomeIcon,
  BuildingOffice2Icon,
  MicrophoneIcon,
  MegaphoneIcon,
  ChartBarIcon,
  BoltIcon,
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
  return (
    <aside className="w-64 bg-brand-900 min-h-screen flex flex-col py-6 flex-shrink-0">
      <div className="px-6 mb-8">
        <div className="flex items-center gap-2">
          <span className="text-2xl">⚡</span>
          <span className="text-white text-xl font-bold tracking-tight">FRACTO</span>
        </div>
        <p className="text-brand-100/60 text-xs mt-1">Voice Agent Platform</p>
      </div>
      <nav className="flex-1 px-3 space-y-1">
        {nav.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-white/10 text-white'
                  : 'text-white/70 hover:bg-white/5 hover:text-white'
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
