'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  ArrowLeft, 
  Save, 
  Eye,
  Image as ImageIcon,
  Upload,
  X
} from 'lucide-react';

export default function NuevaNoticiaPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    title: '',
    subtitle: '',
    category: 'economia',
    excerpt: '',
    content: '',
    imageUrl: '',
    author: 'Admin',
    tags: '',
    isBreaking: false,
    isFeatured: false,
  });

  const [isSaving, setIsSaving] = useState(false);

  const categories = [
    { value: 'economia', label: 'Economía' },
    { value: 'politica', label: 'Política' },
    { value: 'judicial', label: 'Judicial' },
    { value: 'internacional', label: 'Internacional' },
    { value: 'sociedad', label: 'Sociedad' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);

    try {
      const response = await fetch('/api/noticias', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          source_type: 1, // 0x01 (1) = manual, 0x00 (0) = scraper + LLM
          status: 'published',
          tags: formData.tags.split(',').map(t => t.trim()).filter(t => t),
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || 'Error al crear la noticia');
      }

      alert('Noticia creada exitosamente');
      router.push('/admin/noticias');
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Error al crear la noticia');
    } finally {
      setIsSaving(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            href="/admin/noticias"
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Nueva Noticia</h1>
            <p className="text-gray-600 mt-1">Crea una nueva noticia para el portal</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            type="button"
            className="flex items-center gap-2 px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Eye className="w-5 h-5" />
            <span className="font-medium">Vista Previa</span>
          </button>
          <button
            onClick={handleSubmit}
            disabled={isSaving}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Save className="w-5 h-5" />
            <span className="font-medium">{isSaving ? 'Guardando...' : 'Publicar'}</span>
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Title */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Título *
            </label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
              placeholder="Escribe un título llamativo..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg font-semibold"
            />
          </div>

          {/* Subtitle */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Subtítulo
            </label>
            <input
              type="text"
              name="subtitle"
              value={formData.subtitle}
              onChange={handleChange}
              placeholder="Subtítulo opcional..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Excerpt */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Extracto *
            </label>
            <textarea
              name="excerpt"
              value={formData.excerpt}
              onChange={handleChange}
              required
              rows={3}
              placeholder="Resumen breve de la noticia (aparecerá en las tarjetas)..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
            <p className="text-xs text-gray-500 mt-2">
              {formData.excerpt.length} / 200 caracteres recomendados
            </p>
          </div>

          {/* Content Editor */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Contenido *
            </label>
            <div className="border border-gray-300 rounded-lg overflow-hidden">
              {/* Toolbar */}
              <div className="bg-gray-50 border-b border-gray-300 p-2 flex items-center gap-2 flex-wrap">
                <button type="button" className="p-2 hover:bg-gray-200 rounded" title="Negrita">
                  <strong>B</strong>
                </button>
                <button type="button" className="p-2 hover:bg-gray-200 rounded" title="Cursiva">
                  <em>I</em>
                </button>
                <button type="button" className="p-2 hover:bg-gray-200 rounded" title="Subrayado">
                  <u>U</u>
                </button>
                <div className="w-px h-6 bg-gray-300"></div>
                <button type="button" className="p-2 hover:bg-gray-200 rounded" title="Lista">
                  ≡
                </button>
                <button type="button" className="p-2 hover:bg-gray-200 rounded" title="Enlace">
                  🔗
                </button>
                <button type="button" className="p-2 hover:bg-gray-200 rounded" title="Imagen">
                  <ImageIcon className="w-4 h-4" />
                </button>
              </div>
              {/* Editor */}
              <textarea
                name="content"
                value={formData.content}
                onChange={handleChange}
                required
                rows={15}
                placeholder="Escribe el contenido completo de la noticia aquí..."
                className="w-full px-4 py-3 focus:outline-none resize-none"
              />
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {formData.content.length} caracteres
            </p>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Category */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Categoría *
            </label>
            <select
              name="category"
              value={formData.category}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {categories.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          {/* Image */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Imagen Destacada
            </label>
            <div className="space-y-3">
              <input
                type="text"
                name="imageUrl"
                value={formData.imageUrl}
                onChange={handleChange}
                placeholder="/images/noticia.jpg"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                type="button"
                className="w-full flex items-center justify-center gap-2 px-4 py-2 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
              >
                <Upload className="w-5 h-5 text-gray-400" />
                <span className="text-sm text-gray-600">Subir Imagen</span>
              </button>
              {formData.imageUrl && (
                <div className="relative aspect-video bg-gray-100 rounded-lg overflow-hidden">
                  <img
                    src={formData.imageUrl}
                    alt="Preview"
                    className="w-full h-full object-cover"
                  />
                  <button
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, imageUrl: '' }))}
                    className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Author */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Autor
            </label>
            <input
              type="text"
              name="author"
              value={formData.author}
              onChange={handleChange}
              placeholder="Nombre del autor"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Tags */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tags
            </label>
            <input
              type="text"
              name="tags"
              value={formData.tags}
              onChange={handleChange}
              placeholder="economía, dólar, inflación"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-2">
              Separa los tags con comas
            </p>
          </div>

          {/* Options */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                name="isBreaking"
                checked={formData.isBreaking}
                onChange={handleChange}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <div>
                <span className="text-sm font-medium text-gray-900">Breaking News</span>
                <p className="text-xs text-gray-500">Marcar como noticia de última hora</p>
              </div>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                name="isFeatured"
                checked={formData.isFeatured}
                onChange={handleChange}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <div>
                <span className="text-sm font-medium text-gray-900">Noticia Destacada</span>
                <p className="text-xs text-gray-500">Aparecerá en la portada</p>
              </div>
            </label>
          </div>
        </div>
      </form>
    </div>
  );
}
