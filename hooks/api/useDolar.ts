'use client';

import { useState, useEffect } from 'react';
import { dolarService, DolarData } from '@/lib/services/dolar.service';

export function useDolar() {
  const [data, setData] = useState<DolarData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function fetchDolar() {
      try {
        setLoading(true);
        const cotizaciones = await dolarService.getCotizaciones();

        if (isMounted) {
          setData(cotizaciones);
          setError(null);
        }
      } catch (err) {
        if (isMounted) {
          setError(err as Error);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    fetchDolar();

    // Actualizar cada 5 minutos
    const interval = setInterval(fetchDolar, 5 * 60 * 1000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return { data, loading, error };
}
