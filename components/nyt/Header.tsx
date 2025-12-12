'use client';

import Link from 'next/link';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { Menu, X } from 'lucide-react';
import { useState } from 'react';
import { usePathname } from 'next/navigation';
import DolarTicker from '@/components/DolarTicker';

export default function NYTHeader() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const pathname = usePathname();
  const today = format(new Date(), "EEEE, d 'de' MMMM, yyyy", { locale: es });

  // Determinar la región activa basada en la ruta
  const isArgentina = pathname === '/' || pathname.startsWith('/politica') || pathname.startsWith('/economia') || pathname.startsWith('/judicial') || pathname.startsWith('/sociedad');
  const isInternacional = pathname.startsWith('/internacional');

  const navItems = [
    { href: '/politica', label: 'Política', active: pathname.startsWith('/politica') },
    { href: '/economia', label: 'Economía', active: pathname.startsWith('/economia') },
    { href: '/judicial', label: 'Judicial', active: pathname.startsWith('/judicial') },
    { href: '/internacional', label: 'Internacional', active: pathname.startsWith('/internacional') },
    { href: '/sociedad', label: 'Sociedad', active: pathname.startsWith('/sociedad') },
  ];

  return (
    <header className="bg-[var(--paper-surface)] sticky top-0 z-50 border-b border-[var(--rule-strong)]">
      {/* Ticker de Dólar */}
      <DolarTicker />

      {/* Top Bar */}
      <div className="site-container">
        {/* Languages Bar - Enlaces funcionales */}
        <div className="hidden sm:flex justify-between items-center py-2">
          <div className="flex items-center gap-3 text-[10px] uppercase tracking-widest" style={{ fontFamily: 'var(--font-ui)' }}>
            <span className="text-[var(--ink-3)]">Edición</span>
            <div className="inline-flex gap-3">
              <Link
                href="/"
                className={`px-3 py-1 transition ${
                  isArgentina ? 'text-[var(--ink)] font-bold underline underline-offset-4 decoration-[var(--rule-strong)]' : 'text-[var(--ink-3)] hover:text-[var(--ink)]'
                }`}
              >
                Argentina
              </Link>
              <Link
                href="/internacional"
                className={`px-3 py-1 transition ${
                  isInternacional ? 'text-[var(--ink)] font-bold underline underline-offset-4 decoration-[var(--rule-strong)]' : 'text-[var(--ink-3)] hover:text-[var(--ink)]'
                }`}
              >
                Internacional
              </Link>
            </div>
          </div>

          <div className="text-[11px] text-[var(--ink-3)]" style={{ fontFamily: 'var(--font-ui)' }}>
            {today}
          </div>
        </div>

        {/* Logo and Date */}
        <div className="flex items-center justify-between py-3 md:py-4 border-b border-[var(--border-soft)]">
          {/* Left: microcopy */}
          <div className="hidden md:flex flex-col gap-0.5 min-w-[180px]" style={{ fontFamily: 'var(--font-ui)' }}>
            <p className="text-[11px] text-[var(--ink-3)]">Periódico internacional</p>
            <Link href="/" className="text-[12px] text-[var(--ink-2)] hover:underline">
              Portada
            </Link>
          </div>

          {/* Center: Logo */}
          <div className="flex-1 flex justify-center">
            <Link
              href="/"
              className="text-2xl sm:text-3xl md:text-[44px] font-serif font-bold tracking-tight text-center"
              style={{ fontFamily: 'var(--font-georgia)' }}
            >
              Política Argentina
            </Link>
          </div>

          {/* Right: Mobile menu */}
          <div className="flex items-center min-w-[180px] justify-end">
            <button
              className="md:hidden p-2 hover:bg-gray-100 rounded"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Navigation Desktop */}
        <nav className="hidden md:flex items-center justify-center py-3 border-b-2 border-[var(--rule-strong)]">
          <div className="flex items-center gap-5 lg:gap-9 text-[11px] uppercase tracking-wider" style={{ fontFamily: 'var(--font-ui)', fontWeight: 700 }}>
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`whitespace-nowrap transition ${
                  item.active
                    ? 'text-[var(--ink)] underline underline-offset-[10px] decoration-[var(--rule-strong)] decoration-2'
                    : 'text-[var(--ink-2)] hover:text-[var(--ink)]'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </div>
        </nav>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav className="md:hidden py-4 border-b border-[var(--border-soft)]">
            <div className="flex flex-col gap-2" style={{ fontFamily: 'var(--font-ui)' }}>
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`py-2 px-3 rounded text-sm uppercase tracking-wider font-semibold ${
                    item.active ? 'bg-[var(--paper-bg)] text-[var(--ink)]' : 'hover:bg-[var(--paper-bg)] text-[var(--ink-2)]'
                  }`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {item.label}
                </Link>
              ))}
              {/* (sin botones de suscripción / login) */}
            </div>
          </nav>
        )}
      </div>

      <style jsx>{`
        .nyt-button {
          background-color: var(--nyt-button-bg);
          color: white;
        }
        .nyt-button:hover {
          background-color: var(--nyt-button-hover);
        }
      `}</style>
    </header>
  );
}

