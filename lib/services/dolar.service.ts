/**
 * Servicio de Cotización del Dólar
 * Obtiene cotizaciones en tiempo real de múltiples fuentes
 */

export interface DolarQuote {
  compra: number;
  venta: number;
  variacion: number;
  fecha: string;
}

export interface DolarData {
  oficial: DolarQuote;
  blue: DolarQuote;
  mep: DolarQuote;
  ccl: DolarQuote;
  solidario: DolarQuote;
  mayorista: DolarQuote;
  cripto: DolarQuote;
  tarjeta: DolarQuote;
  timestamp: Date;
}

class DolarService {
  private cache: DolarData | null = null;
  private cacheTime: number = 0;
  private readonly CACHE_DURATION = 5 * 60 * 1000; // 5 minutos

  /**
   * Obtiene cotizaciones de DolarAPI (https://dolarapi.com)
   */
  async getDolarAPI(): Promise<DolarData | null> {
    try {
      // No usar next: { revalidate } porque no funciona en Cloudflare edge
      const response = await fetch('https://dolarapi.com/v1/dolares', {
        cache: 'no-store', // Siempre obtener datos frescos
        headers: {
          'Accept': 'application/json',
          'User-Agent': 'Mozilla/5.0 (compatible; NewsBot/1.0)',
        },
      });

      if (!response.ok) {
        console.error('DolarAPI response not ok:', response.status);
        throw new Error('Error fetching DolarAPI');
      }

      const data = await response.json();
      console.log('DolarAPI data received:', data?.length, 'items');

      return this.parseDolarAPIResponse(data);
    } catch (error) {
      console.error('Error en DolarAPI:', error);
      return null;
    }
  }

  /**
   * Obtiene cotizaciones MEP y CCL de CriptoYa
   */
  async getCriptoYaData(): Promise<Partial<DolarData> | null> {
    try {
      const response = await fetch('https://criptoya.com/api/dolar', {
        cache: 'no-store',
        headers: {
          'Accept': 'application/json',
          'User-Agent': 'Mozilla/5.0 (compatible; NewsBot/1.0)',
        },
      });

      if (!response.ok) throw new Error('Error fetching CriptoYa');

      const data = await response.json();

      return this.parseCriptoYaResponse(data);
    } catch (error) {
      console.error('Error en CriptoYa:', error);
      return null;
    }
  }

  /**
   * Obtiene cotizaciones desde nuestra API interna
   */
  async getFromAPI(): Promise<DolarData | null> {
    try {
      const response = await fetch('/api/dolar', {
        cache: 'no-store',
      });

      if (!response.ok) throw new Error('Error fetching internal API');

      const result = await response.json();

      return result.data;
    } catch (error) {
      console.error('Error en API interna:', error);
      return null;
    }
  }

  /**
   * Obtiene cotizaciones de Ámbito (scraping fallback)
   */
  async getAmbitoData(): Promise<Partial<DolarData> | null> {
    try {
      // Esta sería una implementación de fallback
      // Por ahora retornamos null
      return null;
    } catch (error) {
      console.error('Error en Ámbito:', error);
      return null;
    }
  }

  /**
   * Obtiene las cotizaciones con cache
   */
  async getCotizaciones(): Promise<DolarData> {
    // Verificar cache
    const now = Date.now();
    if (this.cache && (now - this.cacheTime) < this.CACHE_DURATION) {
      return this.cache;
    }

    // Intentar obtener de DolarAPI
    const apiData = await this.getDolarAPI();

    if (!apiData) {
      // Si no hay datos, lanzar error para que el componente lo maneje
      throw new Error('No se pudieron obtener cotizaciones de ninguna fuente');
    }

    // Enriquecer con datos de CriptoYa (MEP y CCL más precisos)
    const criptoYaData = await this.getCriptoYaData();

    if (criptoYaData) {
      // Combinar datos: DolarAPI + CriptoYa
      const combinedData = {
        ...apiData,
        mep: criptoYaData.mep || apiData.mep,
        ccl: criptoYaData.ccl || apiData.ccl,
      };

      this.cache = combinedData;
      this.cacheTime = now;
      return combinedData;
    }

    this.cache = apiData;
    this.cacheTime = now;
    return apiData;
  }

  /**
   * Parsea respuesta de DolarAPI
   */
  private parseDolarAPIResponse(data: any[]): DolarData {
    const findQuote = (casa: string) => {
      const item = data.find(d => d.casa === casa);
      return {
        compra: item?.compra || 0,
        venta: item?.venta || item?.compra || 0,
        variacion: this.calculateVariation(item?.compra, item?.venta || item?.compra),
        fecha: item?.fechaActualizacion || new Date().toISOString(),
      };
    };

    // Dolar oficial para calcular solidario (oficial + 30% impuesto PAIS + 30% percepción)
    const oficialItem = data.find(d => d.casa === 'oficial');
    const oficialVenta = oficialItem?.venta || 0;
    // Solidario ya no tiene impuesto PAIS (eliminado dic 2024), solo 30% percepción ganancias
    const solidarioVenta = Math.round(oficialVenta * 1.30);

    return {
      oficial: findQuote('oficial'),
      blue: findQuote('blue'),
      mep: findQuote('bolsa'), // DolarAPI llama "bolsa" al MEP
      ccl: findQuote('contadoconliqui'), // DolarAPI llama "contadoconliqui" al CCL
      solidario: {
        compra: Math.round(oficialVenta * 1.25),
        venta: solidarioVenta,
        variacion: 0,
        fecha: oficialItem?.fechaActualizacion || new Date().toISOString(),
      },
      mayorista: findQuote('mayorista'),
      cripto: findQuote('cripto'),
      tarjeta: findQuote('tarjeta'),
      timestamp: new Date(),
    };
  }

  /**
   * Calcula variación porcentual
   */
  private calculateVariation(compra: number, venta: number): number {
    if (!compra || !venta) return 0;
    return ((venta - compra) / compra) * 100;
  }

  /**
   * Parsea respuesta de CriptoYa
   */
  private parseCriptoYaResponse(data: any): Partial<DolarData> {
    // MEP: usar promedio de AL30 24hs
    const mepPrice = data.mep?.al30?.['24hs']?.price || 0;
    const mepBid = mepPrice * 0.995; // Aproximar spread
    const mepAsk = mepPrice * 1.005;
    const mepVariation = data.mep?.al30?.['24hs']?.variation || 0;

    // CCL: usar promedio de AL30 24hs
    const cclPrice = data.ccl?.al30?.['24hs']?.price || 0;
    const cclBid = cclPrice * 0.995;
    const cclAsk = cclPrice * 1.005;
    const cclVariation = data.ccl?.al30?.['24hs']?.variation || 0;

    return {
      mep: {
        compra: Math.round(mepBid),
        venta: Math.round(mepAsk),
        variacion: mepVariation,
        fecha: new Date().toISOString(),
      },
      ccl: {
        compra: Math.round(cclBid),
        venta: Math.round(cclAsk),
        variacion: cclVariation,
        fecha: new Date().toISOString(),
      },
    };
  }

  /**
   * Formatea número como moneda argentina
   */
  formatCurrency(value: number): string {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
      minimumFractionDigits: 2,
    }).format(value);
  }

  /**
   * Formatea variación con símbolo
   */
  formatVariation(value: number): string {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  }
}

export const dolarService = new DolarService();
