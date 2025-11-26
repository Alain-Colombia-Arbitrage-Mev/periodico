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
      const response = await fetch('https://dolarapi.com/v1/dolares', {
        next: { revalidate: 300 }, // Revalidar cada 5 minutos
        headers: {
          'Accept': 'application/json',
        },
      });

      if (!response.ok) throw new Error('Error fetching DolarAPI');

      const data = await response.json();

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
        next: { revalidate: 300 },
        headers: {
          'Accept': 'application/json',
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

    if (apiData) {
      // Enriquecer con datos de CriptoYa (MEP y CCL)
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

    // Si falla, retornar datos por defecto
    return this.getDefaultData();
  }

  /**
   * Parsea respuesta de DolarAPI
   */
  private parseDolarAPIResponse(data: any[]): DolarData {
    const findQuote = (nombre: string) => {
      const item = data.find(d => d.nombre?.toLowerCase().includes(nombre.toLowerCase()));
      return {
        compra: item?.compra || 0,
        venta: item?.venta || 0,
        variacion: this.calculateVariation(item?.compra, item?.venta),
        fecha: item?.fechaActualizacion || new Date().toISOString(),
      };
    };

    return {
      oficial: findQuote('oficial'),
      blue: findQuote('blue'),
      mep: findQuote('mep'),
      ccl: findQuote('ccl'),
      solidario: findQuote('solidario'),
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
   * Datos por defecto (fallback)
   */
  private getDefaultData(): DolarData {
    const defaultQuote: DolarQuote = {
      compra: 1000,
      venta: 1020,
      variacion: 0,
      fecha: new Date().toISOString(),
    };

    return {
      oficial: { ...defaultQuote, compra: 1025, venta: 1075 },
      blue: { ...defaultQuote, compra: 1415, venta: 1445 },
      mep: { ...defaultQuote, compra: 1454, venta: 1464 },
      ccl: { ...defaultQuote, compra: 1466, venta: 1476 },
      solidario: { ...defaultQuote, compra: 1333, venta: 1398 },
      mayorista: { ...defaultQuote, compra: 1018, venta: 1038 },
      cripto: { ...defaultQuote, compra: 1450, venta: 1470 },
      tarjeta: { ...defaultQuote, compra: 1640, venta: 1720 },
      timestamp: new Date(),
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
