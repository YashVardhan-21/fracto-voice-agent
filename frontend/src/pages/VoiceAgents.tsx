import { useQuery } from '@tanstack/react-query';
import { getAgents } from '../api/agents';
import { Header } from '../components/layout/Header';
import { Badge } from '../components/ui/Badge';

const TH_CLS =
  'text-left px-4 py-3 text-[11px] font-sf-mono uppercase tracking-[0.05em] text-steel-grey';
const TD_CLS = 'px-4 py-3';

export function VoiceAgents() {
  const { data: agents = [], isLoading } = useQuery({
    queryKey: ['agents'],
    queryFn: getAgents,
  });

  return (
    <>
      <Header title="Voice Agents" />
      <div className="p-4 sm:p-6">
        <div className="bg-display-black border border-digital-white/10 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="border-b border-digital-white/10">
              <tr>
                {['Name', 'Status', 'Total Calls', 'Successful', 'Created'].map((h) => (
                  <th key={h} className={TH_CLS}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {isLoading && (
                <tr>
                  <td colSpan={5} className="text-center py-10 text-slate-blue text-[12px] font-sf-mono">
                    Loading…
                  </td>
                </tr>
              )}
              {!isLoading && agents.length === 0 && (
                <tr>
                  <td colSpan={5} className="text-center py-10 text-slate-blue text-[12px] font-sf-mono">
                    No voice agents yet. Run the pipeline to create agents.
                  </td>
                </tr>
              )}
              {agents.map((a) => (
                <tr
                  key={a.id}
                  className="border-b border-digital-white/[0.06] hover:bg-digital-white/[0.03] transition-colors"
                >
                  <td className={`${TD_CLS} font-medium text-digital-white text-[13px]`}>{a.name}</td>
                  <td className={TD_CLS}>
                    <Badge label={a.status} status={a.status} />
                  </td>
                  <td className={`${TD_CLS} text-slate-blue text-[12px] font-sf-mono`}>{a.total_calls}</td>
                  <td className={`${TD_CLS} text-slate-blue text-[12px] font-sf-mono`}>{a.successful_calls}</td>
                  <td className={`${TD_CLS} text-slate-blue text-[12px] font-sf-mono`}>
                    {new Date(a.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
