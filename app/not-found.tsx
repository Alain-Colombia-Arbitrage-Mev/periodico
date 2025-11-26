import Link from 'next/link';
import { FileQuestion, Home } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--ln-neutral-0)' }}>
      <div className="text-center px-4 max-w-2xl">
        <FileQuestion className="w-24 h-24 mx-auto text-blue-500 mb-6" />
        <h1 className="text-6xl font-bold text-gray-900 mb-4">404</h1>
        <h2 className="text-2xl font-serif font-bold text-gray-800 mb-4">
          Página no encontrada
        </h2>
        <p className="text-lg text-gray-600 mb-8">
          Lo sentimos, la página que buscas no existe o ha sido movida.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/"
            className="inline-flex items-center gap-2 bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            <Home className="w-5 h-5" />
            Volver al inicio
          </Link>
          <Link
            href="/politica"
            className="inline-flex items-center gap-2 border-2 border-blue-600 text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
          >
            Ver noticias
          </Link>
        </div>
      </div>
    </div>
  );
}
