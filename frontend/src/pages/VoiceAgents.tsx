import { useQuery } from '@tanstack/react-query';
import { getAgents } from '../api/agents';
import { Header } from '../components/layout/Header';
import { Badge } from '../components/ui/Badge';

export function VoiceAgents() {
  const { data: agents = [], isLoading } = useQuery({
    queryKey: ['agents'],
    queryFn: getAgents,
  });

  return (
    <>
      <Header title="Voice Agents" />
      <div className="p-8">
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                {['Name', 'Status', 'Total Calls', 'Successful', 'Created'].map((h) => (
                  <th
                    key={h}
                    className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {isLoading && (
                <tr>
                  <td colSpan={5} className="text-center py-8 text-gray-400">
                    Loading…
                  </td>
                </tr>
              )}
              {!isLoading && agents.length === 0 && (
                <tr>
                  <td colSpan={5} className="text-center py-8 text-gray-400">
                    No voice agents yet. Run the pipeline to create agents.
                  </td>
                </tr>
              )}
              {agents.map((a) => (
                <tr key={a.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{a.name}</td>
                  <td className="px-4 py-3">
                    <Badge label={a.status} status={a.status} />
                  </td>
                  <td className="px-4 py-3 text-gray-600">{a.total_calls}</td>
                  <td className="px-4 py-3 text-gray-600">{a.successful_calls}</td>
                  <td className="px-4 py-3 text-gray-500">
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
