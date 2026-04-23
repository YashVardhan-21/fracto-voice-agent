import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { getDashboardStats } from '../api/analytics';
import { Header } from '../components/layout/Header';
import { StatCard } from '../components/ui/Card';

export function Dashboard() {
  const { data: stats } = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboardStats,
  });

  return (
    <>
      <Header title="Dashboard" />
      <div className="p-8 space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard label="Total Companies" value={stats?.total_companies ?? '—'} />
          <StatCard label="Active Voice Agents" value={stats?.active_agents ?? '—'} />
          <StatCard label="Campaigns" value={stats?.total_campaigns ?? '—'} />
          <StatCard label="Total Calls" value={stats?.total_calls ?? '—'} />
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="flex gap-3 flex-wrap">
            <Link
              to="/pipeline"
              className="px-4 py-2 bg-brand-500 text-white rounded-lg text-sm font-medium hover:bg-brand-600 transition-colors"
            >
              ⚡ Run Pipeline
            </Link>
            <Link
              to="/companies"
              className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
            >
              View Companies
            </Link>
            <Link
              to="/campaigns"
              className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
            >
              New Campaign
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}
