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
      <div className="p-8 space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard label="Total Companies" value={stats?.total_companies ?? '—'} />
          <StatCard label="Active Voice Agents" value={stats?.active_agents ?? '—'} />
          <StatCard label="Total Campaigns" value={stats?.total_campaigns ?? '—'} />
          <StatCard label="Total Calls" value={stats?.total_calls ?? '—'} />
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <p className="text-sm text-gray-500">
            Detailed call analytics and conversion metrics will appear here as your voice agents make calls.
          </p>
        </div>
      </div>
    </>
  );
}
