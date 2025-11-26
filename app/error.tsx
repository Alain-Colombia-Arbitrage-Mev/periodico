'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { AlertTriangle, Home, RefreshCw } from 'lucide-react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Error:', error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--ln-neutral-0)' }}>
      <div className="text-center px-4 max-w-2xl">
        <AlertTriangle className="w-24 h-24 mx-auto text-red-500 mb-6" />
        <h1 className="text-6xl font-bold text-gray-900 mb-4">500</h1>
        <h2 className="text-2xl font-serif font-bold text-gray-800 mb-4">
          Error del servidor
        </h2>
        <p className="text-lg text-gray-600 mb-4">
          Algo salió mal. Por favor, intenta nuevamente.
        </p>
        {error.message && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 text-left">
            <p className="text-sm text-red-800 font-mono">
              {error.message}
            </p>
          </div>
        )}
        <div className="flex gap-4 justify-center">
          <button
            onClick={reset}
            className="inline-flex items-center gap-2 bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            <RefreshCw className="w-5 h-5" />
            Intentar de nuevo
          </button>
          <Link
            href="/"
            className="inline-flex items-center gap-2 border-2 border-blue-600 text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
          >
            <Home className="w-5 h-5" />
            Volver al inicio
          </Link>
        </div>
      </div>
    </div>
  );
}
