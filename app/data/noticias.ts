// Datos de noticias actualizadas con información real de Argentina
// Última actualización: 2025-11-03

export interface Noticia {
  id: string;
  title: string;
  subtitle?: string;
  slug: string;
  category: string;
  categorySlug: string;
  excerpt: string;
  content?: string;
  imageUrl: string;
  author: string;
  publishedAt: Date;
  views: number;
  isBreaking?: boolean;
  tags?: string[];
  readingTime?: number;
}

// CATEGORÍA: ECONOMÍA
export const noticiasEconomia: Noticia[] = [
  {
    id: 'eco-1',
    title: 'Dólar blue alcanza los $1.445: análisis del mercado cambiario argentino',
    subtitle: 'El dólar paralelo se mantiene estable mientras el gobierno evalúa nuevas medidas económicas',
    slug: 'dolar-blue-analisis-mercado-cambiario',
    category: 'Economía',
    categorySlug: 'economia',
    excerpt: 'El dólar blue cerró en $1.445 para la venta, manteniéndose estable en las últimas jornadas. Analistas económicos evalúan el impacto de las medidas del Banco Central y las perspectivas para los próximos meses en el mercado cambiario argentino.',
    imageUrl: 'https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=1200&h=800&fit=crop',
    author: 'María González',
    publishedAt: new Date(Date.now() - 1 * 60 * 60 * 1000),
    views: 45230,
    isBreaking: true,
    tags: ['dólar blue', 'economía', 'mercado cambiario', 'BCRA'],
    readingTime: 4,
  },
  {
    id: 'eco-2',
    title: 'Banco Central modifica encajes para el efectivo mínimo de los bancos',
    slug: 'banco-central-modifica-encajes-para-el-efectivo-minimo-de-los-bancos',
    subtitle: 'Nuevas reglas buscan dar más estabilidad al sistema financiero argentino',
    category: 'Economía',
    categorySlug: 'economia',
    excerpt: 'Desde noviembre, la autoridad monetaria que encabeza Santiago Bausili endurece las reglas para los bancos. Ahora deberán mantener casi todo su efectivo mínimo todos los días, con el objetivo de darle más estabilidad al sistema financiero.',
    imageUrl: 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&h=800&fit=crop',
    author: 'Carlos Fernández',
    publishedAt: new Date(Date.now() - 3 * 60 * 60 * 1000),
    views: 32100,
    tags: ['BCRA', 'bancos', 'sistema financiero', 'encajes'],
  },
  {
    id: 'eco-3',
    title: 'Gobierno anuncia aumento del 7,20% en el precio del gas natural',
    slug: 'gobierno-anuncia-aumento-del-720-en-el-precio-del-gas-natura',
    subtitle: 'El incremento impactará un 3,80% en la tarifa desde noviembre',
    category: 'Economía',
    categorySlug: 'economia',
    excerpt: 'El aumento alcanza tanto al gas destinado a la venta como al autoconsumo, según la Resolución 1698/2025 publicada en el Boletín Oficial. El impacto en las tarifas residenciales será gradual.',
    imageUrl: 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&h=800&fit=crop',
    author: 'Juan Martínez',
    publishedAt: new Date(Date.now() - 5 * 60 * 60 * 1000),
    views: 28450,
    tags: ['gas natural', 'tarifas', 'servicios públicos'],
  },
  {
    id: 'eco-4',
    title: 'Reducción de aranceles para juguetes busca bajar precios antes de Navidad',
    slug: 'reduccion-de-aranceles-para-juguetes-busca-bajar-precios-ant',
    subtitle: 'La alícuota pasó del 35% al 20% tras 13 años',
    category: 'Economía',
    categorySlug: 'economia',
    excerpt: 'El Gobierno reduce aranceles de importación en un intento por fomentar la competencia y abaratar los juguetes en Argentina, que lidera la región con los precios más altos.',
    imageUrl: 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&h=800&fit=crop',
    author: 'Laura Sánchez',
    publishedAt: new Date(Date.now() - 6 * 60 * 60 * 1000),
    views: 19230,
    tags: ['aranceles', 'importaciones', 'juguetes', 'navidad'],
  },
  {
    id: 'eco-5',
    title: 'Inflación de octubre supera proyecciones del gobierno argentino',
    slug: 'inflacion-de-octubre-supera-proyecciones-del-gobierno-argent',
    subtitle: 'INDEC reporta incremento del 8,3% mensual en precios al consumidor',
    category: 'Economía',
    categorySlug: 'economia',
    excerpt: 'El INDEC informó que los precios subieron 8,3% en el mes, por encima del 6,5% estimado por el gobierno. Alimentos y servicios lideraron los aumentos, generando preocupación en el mercado.',
    imageUrl: 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&h=800&fit=crop',
    author: 'Roberto Díaz',
    publishedAt: new Date(Date.now() - 8 * 60 * 60 * 1000),
    views: 42100,
    tags: ['inflación', 'INDEC', 'precios', 'economía'],
  },
];

// CATEGORÍA: POLÍTICA
export const noticiasPolitica: Noticia[] = [
  {
    id: 'pol-1',
    title: 'Milei anuncia reforma económica integral en el Congreso Nacional',
    slug: 'milei-anuncia-reforma-economica-integral-en-el-congreso-naci',
    subtitle: 'El presidente presentó un paquete de 50 medidas que incluyen reducción del gasto público',
    category: 'Política',
    categorySlug: 'politica',
    excerpt: 'En una sesión extraordinaria del Congreso, el presidente Javier Milei detalló su plan económico para los próximos dos años. La propuesta incluye la eliminación de 12 ministerios, la privatización de empresas estatales y la apertura total del comercio exterior.',
    imageUrl: 'https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=1200&h=800&fit=crop',
    author: 'Redacción Política Argentina',
    publishedAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
    views: 56780,
    isBreaking: true,
    tags: ['milei', 'reforma económica', 'congreso', 'gobierno'],
  },
  {
    id: 'pol-2',
    title: 'Cristina Kirchner presenta proyecto de ley sobre reforma previsional',
    slug: 'cristina-kirchner-presenta-proyecto-de-ley-sobre-reforma-pre',
    subtitle: 'La expresidenta propone aumentar las jubilaciones mínimas',
    category: 'Política',
    categorySlug: 'politica',
    excerpt: 'La expresidenta propone aumentar las jubilaciones mínimas y modificar la fórmula de movilidad. El oficialismo adelantó que no apoyará la iniciativa, generando un nuevo enfrentamiento político.',
    imageUrl: 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1200&h=800&fit=crop',
    author: 'Ana López',
    publishedAt: new Date(Date.now() - 4 * 60 * 60 * 1000),
    views: 38900,
    tags: ['cristina kirchner', 'jubilaciones', 'reforma previsional'],
  },
  {
    id: 'pol-3',
    title: 'Gobernadores del interior reclaman mayor coparticipación federal',
    slug: 'gobernadores-del-interior-reclaman-mayor-coparticipacion-fed',
    subtitle: 'Mandatarios provinciales se reunieron en Córdoba para coordinar estrategia',
    category: 'Política',
    categorySlug: 'politica',
    excerpt: 'Mandatarios provinciales se reunieron en Córdoba para coordinar estrategia ante el gobierno nacional. Amenazan con acciones legales si no se revierte el recorte en la distribución de recursos.',
    imageUrl: 'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=1200&h=800&fit=crop',
    author: 'Pedro Ramírez',
    publishedAt: new Date(Date.now() - 7 * 60 * 60 * 1000),
    views: 22450,
    tags: ['gobernadores', 'coparticipación', 'provincias'],
  },
  {
    id: 'pol-4',
    title: 'La Libertad Avanza consolida su presencia en el Congreso',
    slug: 'la-libertad-avanza-consolida-su-presencia-en-el-congreso',
    subtitle: 'El partido oficialista suma nuevos legisladores tras las últimas elecciones',
    category: 'Política',
    categorySlug: 'politica',
    excerpt: 'El espacio político del presidente Milei logró aumentar su representación en ambas cámaras, lo que facilitaría la aprobación de proyectos clave para el gobierno.',
    imageUrl: 'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=1200&h=800&fit=crop',
    author: 'Martín Suárez',
    publishedAt: new Date(Date.now() - 9 * 60 * 60 * 1000),
    views: 31200,
    tags: ['la libertad avanza', 'congreso', 'elecciones'],
  },
  {
    id: 'pol-5',
    title: 'Debate por la reforma judicial genera tensión en el Senado',
    slug: 'debate-por-la-reforma-judicial-genera-tension-en-el-senado',
    subtitle: 'Oficialismo y oposición enfrentados por el proyecto de ley',
    category: 'Política',
    categorySlug: 'politica',
    excerpt: 'El proyecto de reforma del Poder Judicial presentado por el gobierno enfrenta resistencia en el Senado. La oposición advierte sobre posibles violaciones a la independencia judicial.',
    imageUrl: 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200&h=800&fit=crop',
    author: 'Silvia Torres',
    publishedAt: new Date(Date.now() - 11 * 60 * 60 * 1000),
    views: 27800,
    tags: ['reforma judicial', 'senado', 'justicia'],
  },
];

// CATEGORÍA: JUDICIAL
export const noticiasJudicial: Noticia[] = [
  {
    id: 'jud-1',
    title: 'Corte Suprema analiza caso clave sobre corrupción institucional',
    slug: 'corte-suprema-analiza-caso-clave-sobre-corrupcion-institucio',
    subtitle: 'El máximo tribunal evalúa denuncias sobre irregularidades en la obra pública',
    category: 'Judicial',
    categorySlug: 'judicial',
    excerpt: 'El máximo tribunal evalúa denuncias sobre irregularidades en la obra pública durante el gobierno anterior. La decisión podría sentar jurisprudencia en casos de corrupción estatal.',
    imageUrl: 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200&h=800&fit=crop',
    author: 'Carlos Rodríguez',
    publishedAt: new Date(Date.now() - 6 * 60 * 60 * 1000),
    views: 28450,
    tags: ['corte suprema', 'corrupción', 'obra pública'],
  },
  {
    id: 'jud-2',
    title: 'Procesan a ex funcionarios por desvío de fondos públicos',
    slug: 'procesan-a-ex-funcionarios-por-desvio-de-fondos-publicos',
    subtitle: 'La justicia federal avanza en investigación de corrupción',
    category: 'Judicial',
    categorySlug: 'judicial',
    excerpt: 'Un juez federal procesó a cinco ex funcionarios por presunto desvío de fondos destinados a programas sociales. El monto investigado supera los 500 millones de pesos.',
    imageUrl: 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1200&h=800&fit=crop',
    author: 'Lucía Fernández',
    publishedAt: new Date(Date.now() - 10 * 60 * 60 * 1000),
    views: 19500,
    tags: ['corrupción', 'justicia federal', 'procesamientos'],
  },
  {
    id: 'jud-3',
    title: 'Sentencia histórica en caso de violencia de género',
    slug: 'sentencia-historica-en-caso-de-violencia-de-genero',
    subtitle: 'Tribunal condena a perpetua por femicidio agravado',
    category: 'Judicial',
    categorySlug: 'judicial',
    excerpt: 'Un tribunal oral condenó a prisión perpetua a un hombre por el femicidio de su ex pareja. La sentencia es considerada un precedente importante en la lucha contra la violencia de género.',
    imageUrl: 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200&h=800&fit=crop',
    author: 'Marta González',
    publishedAt: new Date(Date.now() - 13 * 60 * 60 * 1000),
    views: 16700,
    tags: ['violencia de género', 'femicidio', 'justicia'],
  },
];

// CATEGORÍA: INTERNACIONAL
export const noticiasInternacional: Noticia[] = [
  {
    id: 'int-1',
    title: 'Argentina firma acuerdo comercial histórico con la Unión Europea',
    slug: 'argentina-firma-acuerdo-comercial-historico-con-la-union-eur',
    subtitle: 'El tratado abre mercados europeos para productos argentinos',
    category: 'Internacional',
    categorySlug: 'internacional',
    excerpt: 'El tratado abre mercados europeos para productos argentinos y elimina aranceles en sectores clave como agricultura y tecnología. El acuerdo beneficiará especialmente a exportadores de carne y granos.',
    imageUrl: 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1200&h=800&fit=crop',
    author: 'Diego Martínez',
    publishedAt: new Date(Date.now() - 8 * 60 * 60 * 1000),
    views: 19230,
    tags: ['unión europea', 'comercio exterior', 'exportaciones'],
  },
  {
    id: 'int-2',
    title: 'China y Argentina negocian ampliación de swap de monedas',
    slug: 'china-y-argentina-negocian-ampliacion-de-swap-de-monedas',
    subtitle: 'Buscan fortalecer reservas del Banco Central argentino',
    category: 'Internacional',
    categorySlug: 'internacional',
    excerpt: 'Funcionarios de ambos países avanzan en negociaciones para ampliar el acuerdo de intercambio de monedas, lo que permitiría a Argentina reforzar sus reservas internacionales.',
    imageUrl: 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=1200&h=800&fit=crop',
    author: 'Fernanda Ruiz',
    publishedAt: new Date(Date.now() - 12 * 60 * 60 * 1000),
    views: 15400,
    tags: ['china', 'swap', 'reservas', 'BCRA'],
  },
  {
    id: 'int-3',
    title: 'FMI evalúa nuevo desembolso para Argentina',
    slug: 'fmi-evalua-nuevo-desembolso-para-argentina',
    subtitle: 'Misión del organismo revisa cumplimiento de metas fiscales',
    category: 'Internacional',
    categorySlug: 'internacional',
    excerpt: 'Una misión del Fondo Monetario Internacional se encuentra en Buenos Aires evaluando el cumplimiento de las metas acordadas. De aprobarse, Argentina recibiría USD 4.000 millones.',
    imageUrl: 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&h=800&fit=crop',
    author: 'Ricardo Paz',
    publishedAt: new Date(Date.now() - 15 * 60 * 60 * 1000),
    views: 24300,
    tags: ['FMI', 'deuda', 'economía internacional'],
  },
];

// CATEGORÍA: SOCIEDAD
export const noticiasSociedad: Noticia[] = [
  {
    id: 'soc-1',
    title: 'Reforma educativa genera debate en todo el país',
    slug: 'reforma-educativa-genera-debate-en-todo-el-pais',
    subtitle: 'Docentes, padres y expertos discuten los cambios propuestos',
    category: 'Sociedad',
    categorySlug: 'sociedad',
    excerpt: 'Docentes, padres y expertos discuten los cambios propuestos en el sistema educativo. Habrá audiencias públicas en todas las provincias para debatir la nueva ley de educación.',
    imageUrl: 'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=1200&h=800&fit=crop',
    author: 'Patricia Gómez',
    publishedAt: new Date(Date.now() - 10 * 60 * 60 * 1000),
    views: 15670,
    tags: ['educación', 'reforma', 'docentes'],
  },
  {
    id: 'soc-2',
    title: 'Crece la demanda de atención en salud mental post-pandemia',
    slug: 'crece-la-demanda-de-atencion-en-salud-mental-post-pandemia',
    subtitle: 'Hospitales públicos reportan aumento del 40% en consultas',
    category: 'Sociedad',
    categorySlug: 'sociedad',
    excerpt: 'Los servicios de salud mental en hospitales públicos registran un incremento sostenido de consultas. Especialistas advierten sobre la necesidad de reforzar los equipos profesionales.',
    imageUrl: 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1200&h=800&fit=crop',
    author: 'Daniela Moreno',
    publishedAt: new Date(Date.now() - 14 * 60 * 60 * 1000),
    views: 12800,
    tags: ['salud mental', 'salud pública', 'sociedad'],
  },
  {
    id: 'soc-3',
    title: 'Récord de inscripción en universidades públicas argentinas',
    slug: 'record-de-inscripcion-en-universidades-publicas-argentinas',
    subtitle: 'Más de 500.000 estudiantes inician el ciclo lectivo 2025',
    category: 'Sociedad',
    categorySlug: 'sociedad',
    excerpt: 'Las universidades nacionales registran un récord histórico de inscripciones para el ciclo 2025. La gratuidad y calidad académica continúan siendo factores clave de atracción.',
    imageUrl: 'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=1200&h=800&fit=crop',
    author: 'Gustavo Herrera',
    publishedAt: new Date(Date.now() - 16 * 60 * 60 * 1000),
    views: 18900,
    tags: ['universidades', 'educación superior', 'estudiantes'],
  },
];

// Trending Topics actualizados
export const trendingTopics = [
  { name: 'Dólar Blue $1.445', count: 56780, slug: 'dolar-blue' },
  { name: 'Reforma Económica', count: 45230, slug: 'reforma-economica' },
  { name: 'Milei', count: 42100, slug: 'milei' },
  { name: 'Inflación', count: 38900, slug: 'inflacion' },
  { name: 'Cristina Kirchner', count: 32100, slug: 'cristina-kirchner' },
  { name: 'BCRA', count: 28700, slug: 'bcra' },
  { name: 'Corte Suprema', count: 25400, slug: 'corte-suprema' },
  { name: 'Unión Europea', count: 22450, slug: 'union-europea' },
];

// Función para obtener todas las noticias
export function getAllNoticias(): Noticia[] {
  return [
    ...noticiasEconomia,
    ...noticiasPolitica,
    ...noticiasJudicial,
    ...noticiasInternacional,
    ...noticiasSociedad,
  ].sort((a, b) => b.publishedAt.getTime() - a.publishedAt.getTime());
}

// Función para obtener noticias por categoría
export function getNoticiasByCategory(categorySlug: string): Noticia[] {
  const allNoticias = getAllNoticias();
  return allNoticias.filter(n => n.categorySlug === categorySlug);
}

// Función para obtener noticia destacada
export function getFeaturedNoticia(): Noticia {
  return noticiasEconomia[0]; // Dólar blue como noticia principal
}

// Función para obtener noticias recientes
export function getRecentNoticias(limit: number = 8): Noticia[] {
  return getAllNoticias().slice(0, limit);
}

// Función para obtener todas las noticias (alias de getAllNoticias)
export function getNoticias(): Noticia[] {
  return getAllNoticias();
}

// Función para generar slug desde título
function generateSlug(title: string): string {
  return title
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .substring(0, 60);
}

