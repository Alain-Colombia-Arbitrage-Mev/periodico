'use client';

import { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import type { DolarData } from '@/lib/services/dolar.service';

export default function DolarTicker() {
  const [dolarData, setDolarData] = useState<DolarData | null>(null);

  useEffect(() => {
    async function fetchDolar() {
      try {
        const response = await fetch('/api/dolar');
        if (!response.ok) return;
        
        const result = await response.json();
        if (result.success && result.data) {
          setDolarData(result.data);
        }
      } catch (err) {
        console.error('Error fetching dolar:', err);
      }
    }

    fetchDolar();
    const interval = setInterval(fetchDolar, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(price);
  };

  if (!dolarData) return null;

  const quotes = [
    { label: 'BLUE', data: dolarData.blue, color: '#1E40AF' },
    { label: 'OFICIAL', data: dolarData.oficial, color: '#059669' },
    { label: 'MEP', data: dolarData.mep, color: '#7C3AED' },
    { label: 'CCL', data: dolarData.ccl, color: '#EA580C' },
    { label: 'CRIPTO', data: dolarData.cripto, color: '#F59E0B' },
  ];

  return (
    <div className="bg-black text-white overflow-hidden border-b border-gray-700">
      <div className="ticker-wrapper">
        <div className="ticker-content">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex items-center gap-6 px-6">
              {quotes.map((quote, idx) => {
                const avg = (quote.data.compra + quote.data.venta) / 2;
                const isPositive = quote.data.variacion >= 0;
                
                return (
                  <div key={`${i}-${idx}`} className="flex items-center gap-2 whitespace-nowrap">
                    <span 
                      className="text-xs font-bold uppercase tracking-wide"
                      style={{ color: quote.color }}
                    >
                      {quote.label}
                    </span>
                    <span className="text-sm font-semibold">
                      {formatPrice(avg)}
                    </span>
                    {quote.data.variacion !== 0 && (
                      <span className={`flex items-center gap-0.5 text-xs ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                        {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                        {Math.abs(quote.data.variacion).toFixed(1)}%
                      </span>
                    )}
                    <span className="text-gray-500 mx-1">|</span>
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      <style jsx>{`
        .ticker-wrapper {
          width: 100%;
          overflow: hidden;
        }

        .ticker-content {
          display: flex;
          animation: scroll 30s linear infinite;
        }

        @keyframes scroll {
          0% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(-33.333%);
          }
        }

        .ticker-content:hover {
          animation-play-state: paused;
        }
      `}</style>
    </div>
  );
}
