'use client';

import { useDolar } from '@/hooks/api/useDolar';
import { TrendingUp, TrendingDown, DollarSign } from 'lucide-react';

export default function DolarWidget() {
  const { data, loading, error } = useDolar();

  if (loading) {
    return (
      <div className="bg-white border border-gray-200 p-4">
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-8 bg-gray-200 rounded"></div>
          <div className="h-8 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return null;
  }

  const quotes = [
    { name: 'Blue', data: data.blue, color: 'text-blue-600', bg: 'bg-blue-50' },
    { name: 'Oficial', data: data.oficial, color: 'text-gray-700', bg: 'bg-gray-50' },
    { name: 'MEP', data: data.mep, color: 'text-purple-600', bg: 'bg-purple-50' },
    { name: 'CCL', data: data.ccl, color: 'text-indigo-600', bg: 'bg-indigo-50' },
  ];

  return (
    <div className="bg-white border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-3">
        <div className="flex items-center gap-2 text-white">
          <DollarSign className="w-5 h-5" />
          <h3 className="font-bold text-sm uppercase tracking-wide">
            Cotización del Dólar
          </h3>
        </div>
      </div>

      {/* Quotes */}
      <div className="divide-y divide-gray-100">
        {quotes.map((quote) => (
          <div
            key={quote.name}
            className={`p-3 hover:${quote.bg} transition-colors duration-200`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className={`font-bold text-sm ${quote.color}`}>
                Dólar {quote.name}
              </span>
              {quote.data.variacion !== 0 && (
                <div className="flex items-center gap-1">
                  {quote.data.variacion > 0 ? (
                    <TrendingUp className="w-3 h-3 text-green-600" />
                  ) : (
                    <TrendingDown className="w-3 h-3 text-red-600" />
                  )}
                  <span className={`text-xs font-medium ${
                    quote.data.variacion > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {Math.abs(quote.data.variacion).toFixed(2)}%
                  </span>
                </div>
              )}
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <div className="text-xs text-gray-500 mb-0.5">Compra</div>
                <div className="text-lg font-bold text-gray-900">
                  ${quote.data.compra.toFixed(2)}
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500 mb-0.5">Venta</div>
                <div className={`text-lg font-bold ${quote.color}`}>
                  ${quote.data.venta.toFixed(2)}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="bg-gray-50 px-3 py-2 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          Actualizado: {new Date(data.timestamp).toLocaleTimeString('es-AR', {
            hour: '2-digit',
            minute: '2-digit'
          })}
        </p>
      </div>
    </div>
  );
}
