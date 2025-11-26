'use client';

import { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, DollarSign } from 'lucide-react';
import type { DolarData, DolarQuote } from '@/lib/services/dolar.service';

export default function DolarWidget() {
  const [dolarData, setDolarData] = useState<DolarData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    async function fetchDolar() {
      try {
        const response = await fetch('/api/dolar');
        if (!response.ok) throw new Error('Error fetching dolar');
        
        const result = await response.json();
        if (result.success && result.data) {
          setDolarData(result.data);
          setError(false);
        } else {
          setError(true);
        }
      } catch (err) {
        console.error('Error fetching dolar:', err);
        setError(true);
      } finally {
        setLoading(false);
      }
    }

    fetchDolar();
    
    // Actualizar cada 5 minutos
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

  const renderQuote = (label: string, quote: DolarQuote, color: string) => {
    const avg = (quote.compra + quote.venta) / 2;
    const isPositive = quote.variacion >= 0;

    return (
      <div className="flex items-center justify-between py-2 border-b border-gray-200 last:border-0">
        <div className="flex items-center gap-2">
          <div 
            className="w-2 h-2 rounded-full" 
            style={{ backgroundColor: color }}
          />
          <span className="text-[11px] font-semibold uppercase tracking-wide" style={{ color: 'var(--nyt-text-primary)' }}>
            {label}
          </span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm font-bold" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
            {formatPrice(avg)}
          </span>
          {quote.variacion !== 0 && (
            <div className={`flex items-center gap-1 ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {isPositive ? (
                <TrendingUp className="w-3 h-3" />
              ) : (
                <TrendingDown className="w-3 h-3" />
              )}
              <span className="text-[10px] font-semibold">
                {Math.abs(quote.variacion).toFixed(2)}%
              </span>
            </div>
          )}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="bg-white border border-black p-4">
        <div className="flex items-center gap-2 mb-4 pb-3 border-b-2 border-black">
          <DollarSign className="w-5 h-5" style={{ color: '#00A86B' }} />
          <h3 className="text-sm font-bold uppercase tracking-wide" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
            Cotizaciones del Dólar
          </h3>
        </div>
        <div className="text-center py-6">
          <p className="text-xs" style={{ color: 'var(--nyt-text-secondary)' }}>Cargando cotizaciones...</p>
        </div>
      </div>
    );
  }

  if (error || !dolarData) {
    return (
      <div className="bg-white border border-black p-4">
        <div className="flex items-center gap-2 mb-4 pb-3 border-b-2 border-black">
          <DollarSign className="w-5 h-5" style={{ color: '#00A86B' }} />
          <h3 className="text-sm font-bold uppercase tracking-wide" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
            Cotizaciones del Dólar
          </h3>
        </div>
        <div className="text-center py-6">
          <p className="text-xs" style={{ color: 'var(--nyt-text-secondary)' }}>
            No se pudieron cargar las cotizaciones
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-black">
      <div className="p-4 pb-3 border-b-2 border-black">
        <div className="flex items-center gap-2 mb-1">
          <DollarSign className="w-5 h-5" style={{ color: '#00A86B' }} />
          <h3 className="text-sm font-bold uppercase tracking-wide" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
            Cotizaciones del Dólar
          </h3>
        </div>
        <p className="text-[10px]" style={{ color: 'var(--nyt-text-secondary)' }}>
          Actualizado:{' '}
          {new Date(dolarData.timestamp).toLocaleTimeString('es-AR', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </p>
      </div>

      <div className="p-4">
        {renderQuote('Blue', dolarData.blue, '#1E40AF')}
        {renderQuote('Oficial', dolarData.oficial, '#059669')}
        {renderQuote('Tarjeta', dolarData.tarjeta, '#DC2626')}
        {renderQuote('MEP', dolarData.mep, '#7C3AED')}
        {renderQuote('CCL', dolarData.ccl, '#EA580C')}
        {renderQuote('Mayorista', dolarData.mayorista, '#0891B2')}
        {renderQuote('Cripto', dolarData.cripto, '#F59E0B')}
      </div>

      <div className="px-4 pb-4 pt-2 border-t border-gray-200">
        <p className="text-[9px] text-center" style={{ color: 'var(--nyt-text-secondary)' }}>
          Fuente: DolarAPI • CriptoYa
        </p>
      </div>
    </div>
  );
}
