'use client';

import { useEffect, useRef } from 'react';

interface ViewTrackerProps {
  articleId: string;
}

/**
 * Componente que rastrea las vistas de un artículo
 * Se ejecuta solo una vez por sesión para evitar múltiples conteos
 */
export default function ViewTracker({ articleId }: ViewTrackerProps) {
  const tracked = useRef(false);

  useEffect(() => {
    // Evitar múltiples llamadas en desarrollo (StrictMode)
    if (tracked.current) return;
    
    // Verificar si ya se contó esta vista en esta sesión
    const viewedKey = `viewed_${articleId}`;
    const hasViewed = sessionStorage.getItem(viewedKey);
    
    if (hasViewed) return;

    tracked.current = true;

    // Incrementar vistas después de un pequeño delay
    // para asegurar que el usuario realmente está leyendo
    const timer = setTimeout(async () => {
      try {
        await fetch(`/api/noticias/${articleId}/views`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        
        // Marcar como vista en esta sesión
        sessionStorage.setItem(viewedKey, 'true');
      } catch (error) {
        // Silently fail - views are not critical
        console.debug('View tracking failed:', error);
      }
    }, 2000); // 2 segundos de delay

    return () => clearTimeout(timer);
  }, [articleId]);

  // Este componente no renderiza nada
  return null;
}
