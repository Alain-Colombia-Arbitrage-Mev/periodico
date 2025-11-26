'use client';

import { useState, useEffect } from 'react';
import { Clock, TrendingUp } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

interface LiveUpdate {
  id: string;
  minutesAgo: number;
  title: string;
  category: string;
  categorySlug: string;
}

const liveUpdates: LiveUpdate[] = [
  {
    id: '1',
    minutesAgo: 2,
    title: 'Milei anuncia nuevas medidas económicas en conferencia de prensa',
    category: 'Economía',
    categorySlug: 'economia'
  },
  {
    id: '2',
    minutesAgo: 8,
    title: 'Actualización: Dólar blue cotiza a nuevo récord histórico',
    category: 'Economía',
    categorySlug: 'economia'
  },
  {
    id: '3',
    minutesAgo: 15,
    title: 'Congreso debate proyecto de reforma judicial',
    category: 'Política',
    categorySlug: 'politica'
  },
  {
    id: '4',
    minutesAgo: 23,
    title: 'Inflación: INDEC publicará datos del mes en las próximas horas',
    category: 'Economía',
    categorySlug: 'economia'
  },
];

function getCategoryClass(slug: string) {
  const classes: Record<string, string> = {
    politica: 'category-politica',
    economia: 'category-economia',
    judicial: 'category-judicial',
    internacional: 'category-internacional',
    sociedad: 'category-sociedad',
  };
  return classes[slug] || 'bg-gray-600 text-white';
}

export default function LiveTicker() {
  const [mounted, setMounted] = useState(false);
  const [currentTime, setCurrentTime] = useState<Date | null>(null);

  useEffect(() => {
    setMounted(true);
    setCurrentTime(new Date());

    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 30000); // Actualizar cada 30 segundos

    return () => clearInterval(timer);
  }, []);

  if (!mounted) {
    return (
      <div className="sidebar-widget bg-gradient-to-br from-red-50 to-orange-50 border-red-200">
        <h3 className="sidebar-title flex items-center gap-2 text-red-700 border-red-700">
          <div className="relative flex items-center">
            <span className="animate-pulse absolute h-2 w-2 rounded-full bg-red-600"></span>
            <span className="relative h-2 w-2 rounded-full bg-red-600"></span>
          </div>
          <span className="flex items-center gap-2">
            EN VIVO
            <Clock className="w-4 h-4" />
          </span>
        </h3>
        <div className="space-y-4">
          {liveUpdates.map((update) => (
            <div
              key={update.id}
              className="group cursor-pointer pb-3 border-b border-red-100 last:border-0 last:pb-0 transition-all hover:bg-white hover:bg-opacity-60 p-2 rounded"
            >
              <div className="flex items-start gap-2 mb-2">
                <span className={`category-badge text-xs px-2 py-0.5 ${getCategoryClass(update.categorySlug)}`}>
                  {update.category}
                </span>
                <time className="text-xs text-red-600 font-semibold flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  hace {update.minutesAgo} min
                </time>
              </div>
              <h4 className="font-serif font-bold text-sm leading-tight text-gray-900 group-hover:text-red-700 transition-colors">
                {update.title}
              </h4>
            </div>
          ))}
        </div>
        <div className="mt-4 pt-3 border-t border-red-200 text-center">
          <button className="text-xs font-semibold text-red-700 hover:text-red-900 transition-colors uppercase tracking-wide">
            Ver todas las actualizaciones →
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="sidebar-widget bg-gradient-to-br from-red-50 to-orange-50 border-red-200">
      <h3 className="sidebar-title flex items-center gap-2 text-red-700 border-red-700">
        <div className="relative flex items-center">
          <span className="animate-pulse absolute h-2 w-2 rounded-full bg-red-600"></span>
          <span className="relative h-2 w-2 rounded-full bg-red-600"></span>
        </div>
        <span className="flex items-center gap-2">
          EN VIVO
          <Clock className="w-4 h-4" />
        </span>
      </h3>

      <div className="space-y-4">
        {liveUpdates.map((update) => {
          const updateTime = new Date(currentTime!.getTime() - update.minutesAgo * 60000);
          return (
            <div
              key={update.id}
              className="group cursor-pointer pb-3 border-b border-red-100 last:border-0 last:pb-0 transition-all hover:bg-white hover:bg-opacity-60 p-2 rounded"
            >
              <div className="flex items-start gap-2 mb-2">
                <span className={`category-badge text-xs px-2 py-0.5 ${getCategoryClass(update.categorySlug)}`}>
                  {update.category}
                </span>
                <time className="text-xs text-red-600 font-semibold flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {formatDistanceToNow(updateTime, {
                    addSuffix: true,
                    locale: es
                  })}
                </time>
              </div>
              <h4 className="font-serif font-bold text-sm leading-tight text-gray-900 group-hover:text-red-700 transition-colors">
                {update.title}
              </h4>
            </div>
          );
        })}
      </div>

      <div className="mt-4 pt-3 border-t border-red-200 text-center">
        <button className="text-xs font-semibold text-red-700 hover:text-red-900 transition-colors uppercase tracking-wide">
          Ver todas las actualizaciones →
        </button>
      </div>
    </div>
  );
}
