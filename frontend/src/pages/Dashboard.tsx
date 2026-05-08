import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { getDashboardStats } from '../api/analytics';
import { Header } from '../components/layout/Header';
import { StatCard } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

export function Dashboard() {
  const { data: stats } = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboardStats,
  });

  return (
    <>
      <Header title="Dashboard" />
      <div className="p-4 sm:p-6 space-y-2">
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-2">
          <StatCard label="Total Companies" value={stats?.total_companies ?? '—'} />
          <StatCard label="Active Voice Agents" value={stats?.active_agents ?? '—'} />
          <StatCard label="Campaigns" value={stats?.total_campaigns ?? '—'} />
          <StatCard label="Total Calls" value={stats?.total_calls ?? '—'} />
        </div>
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-2">
          <div className="bg-display-black rounded-[40px] border border-digital-white/10 px-6 py-5">
            <h2 className="text-[11px] uppercase tracking-[0.08em] text-steel-grey font-sf-mono mb-4">
              Quick Actions
            </h2>
            <div className="flex gap-2 flex-wrap">
              <Link to="/pipeline">
                <Button size="md">Run Pipeline</Button>
              </Link>
              <Link to="/companies">
                <Button variant="secondary" size="md">
                  View Companies
                </Button>
              </Link>
              <Link to="/campaigns">
                <Button variant="secondary" size="md">
                  New Campaign
                </Button>
              </Link>
            </div>
          </div>

          <div className="bg-display-black rounded-[40px] border border-digital-white/10 px-6 py-5">
            <h2 className="text-[11px] uppercase tracking-[0.08em] text-steel-grey font-sf-mono mb-4">
              Launch Status
            </h2>
            <div className="space-y-2 text-[11px] font-sf-mono">
              <p className="text-steel-grey">FINDING COMPANIES FOR OUTREACH</p>
              <p className="text-urgency-red">LAUNCHING VOICE AGENT SETUP</p>
              <p className="text-steel-grey">READY FOR OUTBOUND CALLING</p>
            </div>
          </div>

          <div className="bg-display-black rounded-cards border border-digital-white/10 p-3 flex flex-col items-center justify-center gap-3 min-h-36">
            <p className="text-[10px] uppercase tracking-[0.1em] text-steel-grey font-sf-mono">Coming Soon</p>
            <button
              disabled
              aria-label="Lift-off — coming soon"
              className="btn-liftoff w-32 h-32 rounded-full cursor-not-allowed flex items-center justify-center select-none"
            >
              <span className="text-digital-white font-sf-mono text-[13px] uppercase tracking-[0.06em] drop-shadow-sm">
                Lift-off
              </span>
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
