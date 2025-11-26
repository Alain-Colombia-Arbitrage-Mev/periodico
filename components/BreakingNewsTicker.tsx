'use client';

import { useState, useEffect } from 'react';
import { TrendingUp } from 'lucide-react';

interface BreakingNews {
  id: number;
  text: string;
}

const breakingNewsItems: BreakingNews[] = [
  { id: 1, text: "🔴 ÚLTIMA HORA: Milei anuncia nuevas medidas económicas en conferencia de prensa" },
  { id: 2, text: "💰 Dólar blue alcanza nuevo máximo histórico - Cotización actualizada" },
  { id: 3, text: "⚖️ Congreso debate reforma judicial con sesión extraordinaria" },
  { id: 4, text: "📊 INDEC publicará datos de inflación en las próximas horas" },
  { id: 5, text: "🌍 Mercosur: Argentina y Brasil firman nuevo acuerdo comercial" },
];

export default function BreakingNewsTicker() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setIsAnimating(true);
      setTimeout(() => {
        setCurrentIndex((prev) => (prev + 1) % breakingNewsItems.length);
        setIsAnimating(false);
      }, 500);
    }, 5000); // Cambiar cada 5 segundos

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-gradient-to-r from-red-600 via-red-700 to-red-600 text-white py-2.5 shadow-lg relative overflow-hidden">
      {/* Animated background pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent animate-shimmer"></div>
      </div>

      <div className="container mx-auto px-4 relative z-10">
        <div className="flex items-center gap-3">
          {/* Badge */}
          <div className="flex items-center gap-2 bg-white text-red-700 px-3 py-1 font-bold text-xs uppercase tracking-wider shadow-md flex-shrink-0">
            <span className="animate-pulse">●</span>
            <span>Último Momento</span>
            <TrendingUp className="w-3 h-3" />
          </div>

          {/* News Ticker */}
          <div className="flex-1 overflow-hidden">
            <div
              className={`transition-all duration-500 ${
                isAnimating ? 'opacity-0 transform translate-y-2' : 'opacity-100 transform translate-y-0'
              }`}
            >
              <p className="text-sm md:text-base font-medium truncate">
                {breakingNewsItems[currentIndex].text}
              </p>
            </div>
          </div>

          {/* Indicators */}
          <div className="hidden md:flex items-center gap-1.5 flex-shrink-0">
            {breakingNewsItems.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentIndex(index)}
                className={`w-2 h-2 rounded-full transition-all ${
                  index === currentIndex
                    ? 'bg-white w-6'
                    : 'bg-white bg-opacity-50 hover:bg-opacity-75'
                }`}
                aria-label={`Ir a noticia ${index + 1}`}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
