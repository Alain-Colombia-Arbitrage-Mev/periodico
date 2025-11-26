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

  return (
    <header className="border-b border-black bg-white sticky top-0 z-50">
      {/* Ticker de Dólar */}
      <DolarTicker />

      {/* Top Bar */}
      <div className="max-w-[1440px] mx-auto px-4 sm:px-6 md:px-8 lg:px-10">
        {/* Languages Bar - Enlaces funcionales */}
        <div className="hidden sm:flex justify-center items-center gap-4 py-2 text-[10px] uppercase">
          <Link
            href="/"
            className={`hover:font-bold transition-all ${isArgentina ? 'font-bold' : 'text-gray-600'}`}
          >
            ARGENTINA
          </Link>
          <Link
            href="/internacional"
            className={`hover:font-bold transition-all ${isInternacional ? 'font-bold' : 'text-gray-600'}`}
          >
            INTERNACIONAL
          </Link>
          <span className="text-gray-400 cursor-not-allowed">ESPAÑOL</span>
        </div>

        {/* Logo and Date */}
        <div className="flex items-center justify-between py-3 md:py-4 border-b border-gray-300">
          {/* Left: Date - Oculto en móvil pequeño */}
          <div className="hidden md:flex flex-col gap-1 min-w-[120px]">
            <p className="text-[11px] md:text-[12px] font-bold whitespace-nowrap">{today}</p>
            <Link href="/" className="text-[12px] md:text-[14px] text-gray-700 hover:underline">
              Edición de Hoy
            </Link>
          </div>

          {/* Center: Logo */}
          <div className="flex-1 flex justify-center md:justify-center">
            <Link
              href="/"
              className="text-2xl sm:text-3xl md:text-4xl font-serif font-bold tracking-tight text-center"
              style={{ fontFamily: 'var(--font-georgia)' }}
            >
              Política Argentina
            </Link>
          </div>

          {/* Right: Buttons - Responsive */}
          <div className="flex items-center gap-2 md:gap-4 min-w-[120px] justify-end">
            {/* Botones desktop */}
            <button className="hidden md:block nyt-button text-[10px] uppercase px-3 md:px-4 py-2 rounded transition">
              Suscribirse
            </button>
            <button className="hidden md:block nyt-button text-[10px] uppercase px-3 md:px-4 py-2 rounded transition">
              Iniciar Sesión
            </button>

            {/* Menú hamburguesa móvil */}
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
        <nav className="hidden md:flex items-center justify-center py-3 border-b-2 border-black">
          <div className="flex items-center gap-4 lg:gap-8 text-[11px] uppercase font-bold tracking-wide">
            <Link href="/politica" className="hover:underline whitespace-nowrap transition-all">
              Política
            </Link>
            <Link href="/economia" className="hover:underline whitespace-nowrap transition-all">
              Economía
            </Link>
            <Link href="/judicial" className="hover:underline whitespace-nowrap transition-all">
              Judicial
            </Link>
            <Link href="/internacional" className="hover:underline whitespace-nowrap transition-all">
              Internacional
            </Link>
            <Link href="/sociedad" className="hover:underline whitespace-nowrap transition-all">
              Sociedad
            </Link>
          </div>
        </nav>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav className="md:hidden py-4 border-b-2 border-black">
            <div className="flex flex-col gap-3 text-sm uppercase font-semibold">
              <Link href="/politica" className="py-2 hover:bg-gray-50 px-2 rounded" onClick={() => setMobileMenuOpen(false)}>
                Política
              </Link>
              <Link href="/economia" className="py-2 hover:bg-gray-50 px-2 rounded" onClick={() => setMobileMenuOpen(false)}>
                Economía
              </Link>
              <Link href="/judicial" className="py-2 hover:bg-gray-50 px-2 rounded" onClick={() => setMobileMenuOpen(false)}>
                Judicial
              </Link>
              <Link href="/internacional" className="py-2 hover:bg-gray-50 px-2 rounded" onClick={() => setMobileMenuOpen(false)}>
                Internacional
              </Link>
              <Link href="/sociedad" className="py-2 hover:bg-gray-50 px-2 rounded" onClick={() => setMobileMenuOpen(false)}>
                Sociedad
              </Link>
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

