import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import clsx from 'clsx';
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';
import { Sidebar } from './Sidebar';

export function Layout() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-control-panel-grey">
      <Sidebar className="hidden lg:flex" />

      <div className="flex-1 flex flex-col min-w-0">
        <header className="lg:hidden bg-display-black border-b border-digital-white/10 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-base text-urgency-red">●</span>
            <span className="text-digital-white text-sm font-semibold tracking-[0.06em] uppercase font-sf-mono">
              FRACTO
            </span>
          </div>
          <button
            type="button"
            onClick={() => setMobileMenuOpen((v) => !v)}
            aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
            className="text-digital-white p-1"
          >
            {mobileMenuOpen ? <XMarkIcon className="w-6 h-6" /> : <Bars3Icon className="w-6 h-6" />}
          </button>
        </header>

        <main className="flex-1 flex flex-col overflow-auto min-w-0">
          <Outlet />
        </main>
      </div>

      {mobileMenuOpen && (
        <button
          type="button"
          aria-label="Close navigation"
          className="fixed inset-0 bg-black/60 z-40 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      <Sidebar
        className={clsx(
          'fixed inset-y-0 left-0 z-50 transition-transform duration-200 lg:hidden',
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        )}
        onNavigate={() => setMobileMenuOpen(false)}
      />
    </div>
  );
}
