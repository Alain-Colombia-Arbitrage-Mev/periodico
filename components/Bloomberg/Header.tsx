'use client';

import Link from 'next/link';
import { Search, Menu, User, TrendingUp, TrendingDown } from 'lucide-react';
import { useState, useEffect } from 'react';

interface MarketData {
  symbol: string;
  value: string;
  change: number;
  changePercent: number;
}

export default function BloombergHeader() {
  const [markets, setMarkets] = useState<MarketData[]>([
    { symbol: 'MERVAL', value: '1.234.567', change: 28543, changePercent: 2.36 },
    { symbol: 'DÓLAR BLUE', value: '1.050', change: -5, changePercent: -0.47 },
    { symbol: 'DÓLAR MEP', value: '1.025', change: 12, changePercent: 1.18 },
  ]);

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <>
      {/* Market Banner - Datos en vivo */}
      <div className="market-banner no-print">
        <div className="bloomberg-container">
          <div className="flex items-center justify-between overflow-x-auto scrollbar-hide">
            <div className="flex items-center gap-6 py-1">
              {markets.map((market) => (
                <div key={market.symbol} className="market-item flex-shrink-0">
                  <span className="text-gray-400 mr-2">{market.symbol}</span>
                  <span className={market.change >= 0 ? 'market-value-up' : 'market-value-down'}>
                    {market.value}
                    {market.change >= 0 ? (
                      <TrendingUp className="inline w-3 h-3 ml-1" />
                    ) : (
                      <TrendingDown className="inline w-3 h-3 ml-1" />
                    )}
                    <span className="ml-1">{market.changePercent > 0 ? '+' : ''}{market.changePercent}%</span>
                  </span>
                </div>
              ))}
            </div>
            <time className="text-gray-500 text-xs hidden md:block">
              {new Date().toLocaleString('es-AR', {
                hour: '2-digit',
                minute: '2-digit',
                day: '2-digit',
                month: 'short'
              })}
            </time>
          </div>
        </div>
      </div>

      {/* Main Header */}
      <header className="bloomberg-header sticky top-0 z-50">
        <div className="bloomberg-container">
          <div className="flex items-center justify-between py-4">
            {/* Logo */}
            <Link href="/" className="bloomberg-logo flex items-center gap-2">
              <div className="w-2 h-8 bg-yellow-500"></div>
              POLÍTICA AR
            </Link>

            {/* Navigation Desktop */}
            <nav className="hidden lg:flex items-center">
              <Link href="/economia" className="bloomberg-nav-link">
                Economía
              </Link>
              <Link href="/politica" className="bloomberg-nav-link">
                Política
              </Link>
              <Link href="/judicial" className="bloomberg-nav-link">
                Judicial
              </Link>
              <Link href="/internacional" className="bloomberg-nav-link">
                Internacional
              </Link>
              <Link href="/sociedad" className="bloomberg-nav-link">
                Sociedad
              </Link>
              <Link href="/opinion" className="bloomberg-nav-link">
                Opinión
              </Link>
            </nav>

            {/* Actions */}
            <div className="flex items-center gap-4">
              <button
                className="text-white hover:text-yellow-500 transition-colors"
                aria-label="Buscar"
              >
                <Search className="w-5 h-5" />
              </button>
              <button
                className="text-white hover:text-yellow-500 transition-colors hidden md:block"
                aria-label="Usuario"
              >
                <User className="w-5 h-5" />
              </button>
              <button
                className="lg:hidden text-white hover:text-yellow-500 transition-colors"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                aria-label="Menú"
              >
                <Menu className="w-6 h-6" />
              </button>
            </div>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <nav className="lg:hidden pb-4 border-t border-gray-800 mt-2 pt-4 animate-fadeIn">
              <div className="flex flex-col gap-2">
                <Link
                  href="/economia"
                  className="text-white hover:text-yellow-500 py-2 px-4 text-sm font-semibold uppercase"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Economía
                </Link>
                <Link
                  href="/politica"
                  className="text-white hover:text-yellow-500 py-2 px-4 text-sm font-semibold uppercase"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Política
                </Link>
                <Link
                  href="/judicial"
                  className="text-white hover:text-yellow-500 py-2 px-4 text-sm font-semibold uppercase"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Judicial
                </Link>
                <Link
                  href="/internacional"
                  className="text-white hover:text-yellow-500 py-2 px-4 text-sm font-semibold uppercase"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Internacional
                </Link>
                <Link
                  href="/sociedad"
                  className="text-white hover:text-yellow-500 py-2 px-4 text-sm font-semibold uppercase"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Sociedad
                </Link>
                <Link
                  href="/opinion"
                  className="text-white hover:text-yellow-500 py-2 px-4 text-sm font-semibold uppercase"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Opinión
                </Link>
              </div>
            </nav>
          )}
        </div>
      </header>
    </>
  );
}
