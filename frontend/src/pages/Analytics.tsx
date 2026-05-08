import { useQuery } from '@tanstack/react-query';
import { getDashboardStats } from '../api/analytics';
import { Header } from '../components/layout/Header';
import { StatCard } from '../components/ui/Card';

export function Analytics() {
  const { data: stats } = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboardStats,
  });

  return (
    <>
      <Header title="Analytics" />
      <div className="p-4 sm:p-6 space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-2">
          <StatCard label="Total Companies" value={stats?.total_companies ?? '—'} />
          <StatCard label="Active Voice Agents" value={stats?.active_agents ?? '—'} />
          <StatCard label="Total Campaigns" value={stats?.total_campaigns ?? '—'} />
          <StatCard label="Total Calls" value={stats?.total_calls ?? '—'} />
        </div>
        <div className="bg-display-black border border-digital-white/10 rounded-lg p-5">
          <p className="text-[12px] font-sf-mono uppercase tracking-[0.05em] text-steel-grey mb-2">
            Call Analytics
          </p>
          <p className="text-[13px] text-slate-blue">
            Detailed call analytics and conversion metrics will appear here as your voice agents make calls.
          </p>
        </div>
      </div>
    </>
  );
}
