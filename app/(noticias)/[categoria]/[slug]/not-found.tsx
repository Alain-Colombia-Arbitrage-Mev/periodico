import Link from 'next/link';
import { FileQuestion } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center px-4">
        <FileQuestion className="w-24 h-24 mx-auto text-gray-400 mb-6" />
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          404 - Artículo no encontrado
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          El artículo que buscas no existe o ha sido eliminado.
        </p>
        <Link
          href="/"
          className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          Volver al inicio
        </Link>
      </div>
    </div>
  );
}
