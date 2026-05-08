import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';

export function Layout() {
  return (
    <div className="flex min-h-screen bg-control-panel-grey">
      <Sidebar />
      <main className="flex-1 flex flex-col overflow-auto min-w-0">
        <Outlet />
      </main>
    </div>
  );
}
