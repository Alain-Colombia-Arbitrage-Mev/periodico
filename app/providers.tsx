'use client';

import { SWRConfig } from 'swr';

/**
 * SWR Provider con configuración global optimizada
 */
export function SWRProvider({ children }: { children: React.ReactNode }) {
  return (
    <SWRConfig
      value={{
        // Revalidar cada 60 segundos
        refreshInterval: 60000,
        // Revalidar cuando la ventana recupera el foco
        revalidateOnFocus: true,
        // Revalidar cuando se reconecta
        revalidateOnReconnect: true,
        // Mantener datos anteriores mientras se cargan nuevos
        keepPreviousData: true,
        // Tiempo de deduplicación (evitar múltiples requests simultáneos)
        dedupingInterval: 2000,
        // Error retry
        errorRetryCount: 3,
        errorRetryInterval: 5000,
        // Provider para compartir cache entre componentes
        provider: () => new Map(),
      }}
    >
      {children}
    </SWRConfig>
  );
}


