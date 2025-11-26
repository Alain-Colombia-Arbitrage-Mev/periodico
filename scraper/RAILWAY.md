# 🚂 Deployment en Railway - News Scraper

Guía completa para deployar el scraper de noticias en Railway con Docker.

## 📋 Características del Scraper

- ✅ **Web Scraping Avanzado** con Playwright (anti-detección)
- ✅ **Reescritura LLM** con OpenRouter (Claude 3.5 Sonnet / DeepSeek)
- ✅ **Procesamiento de Imágenes** con validación de calidad
- ✅ **Storage en Supabase** con sincronización automática
- ✅ **Auto-limpieza** de noticias antiguas (últimos 3 días)
- ✅ **Pipeline completo**: Scrape → Rewrite → Upload → Cleanup

## 🚀 Deployment Rápido

### Opción 1: Deploy desde GitHub (Recomendado)

1. **Push del código a GitHub**
   ```bash
   git add scraper/
   git commit -m "Add scraper for Railway deployment"
   git push origin main
   ```

2. **Crear nuevo proyecto en Railway**
   - Ve a [railway.app](https://railway.app)
   - Click en "New Project"
   - Selecciona "Deploy from GitHub repo"
   - Selecciona tu repositorio
   - Railway detectará automáticamente el Dockerfile

3. **Configurar variables de entorno** (ver sección Variables)

4. **Deploy automático**
   - Railway construirá y desplegará automáticamente
   - El scraper comenzará a ejecutarse

### Opción 2: Deploy desde CLI de Railway

1. **Instalar Railway CLI**
   ```bash
   npm i -g @railway/cli
   ```

2. **Login y vincular proyecto**
   ```bash
   railway login
   cd scraper
   railway init
   ```

3. **Configurar variables de entorno**
   ```bash
   railway variables set SUPABASE_URL="https://..."
   railway variables set SUPABASE_KEY="eyJ..."
   railway variables set SUPABASE_SERVICE_KEY="eyJ..."
   railway variables set OPENROUTER_API_KEY="sk-or-v1-..."
   ```

4. **Deploy**
   ```bash
   railway up
   ```

## 🔐 Variables de Entorno Requeridas

### Variables Obligatorias

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key  # IMPORTANTE para Storage

# LLM (si LLM_REWRITE_ENABLED=true)
OPENROUTER_API_KEY=sk-or-v1-your-key
```

### Variables Opcionales (con valores por defecto)

```bash
# LLM Configuration
LLM_MODEL=deepseek/deepseek-v3.2-exp   # Recomendado (calidad/precio)
# Alternativas:
# - deepseek/deepseek-chat              # Más económico
# - anthropic/claude-3.5-sonnet         # Premium (mejor calidad, más caro)
LLM_REWRITE_ENABLED=true

# Scraper Configuration
RUN_MODE=continuous                     # O "once" para ejecución única
SCRAPE_INTERVAL=43200                   # 12 horas (en segundos)
MAX_ARTICLES_PER_CATEGORY=20
PAGE_TIMEOUT=30000

# Cleanup
DELETE_OLD_ARTICLES=true
OLD_ARTICLES_DAYS=3                     # Mantener noticias de últimos 3 días

# Images
DOWNLOAD_IMAGES=true
IMAGE_QUALITY=85
MAX_IMAGE_SIZE=2048

# Logging
LOG_LEVEL=INFO
```

## 📝 Configurar Variables en Railway Dashboard

1. Ve a tu proyecto en Railway
2. Click en tu servicio (aparecerá como "scraper" o nombre del repo)
3. Ve a la pestaña "Variables"
4. Click en "New Variable"
5. Agrega cada variable de la lista de arriba

**Tip:** Puedes usar "Raw Editor" para pegar todas las variables de una vez:
```
SUPABASE_URL=https://...
SUPABASE_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...
OPENROUTER_API_KEY=sk-or-v1-...
LLM_MODEL=deepseek/deepseek-v3.2-exp
SCRAPE_INTERVAL=43200
```

## 🔑 Obtener Credenciales

### Supabase
1. Ve a [supabase.com/dashboard](https://supabase.com/dashboard)
2. Selecciona tu proyecto
3. Ve a **Settings** → **API**
4. Copia:
   - **URL**: Project URL
   - **SUPABASE_KEY**: `anon` `public` key
   - **SUPABASE_SERVICE_KEY**: `service_role` key ⚠️ (Mantener secreta)

### OpenRouter
1. Ve a [openrouter.ai](https://openrouter.ai)
2. Regístrate/Login
3. Ve a [Keys](https://openrouter.ai/keys)
4. Crea una nueva API key
5. Copia la key (comienza con `sk-or-v1-`)

## 🐳 Build y Optimizaciones

El Dockerfile incluye:

- ✅ **Multi-stage build** para tamaño mínimo
- ✅ **Caché optimizado** de dependencias
- ✅ **Playwright Chromium** preinstalado
- ✅ **Healthcheck** automático
- ✅ **Entrypoint script** con validaciones
- ✅ **Logs estructurados** con loguru

### Tamaño de imagen esperado
- Build completo: ~1.2 GB (incluye Chromium)
- Build time: ~5-8 minutos (primera vez)
- Build time: ~1-2 minutos (con caché)

## 📊 Monitoreo y Logs

### Ver logs en tiempo real
```bash
railway logs
```

O en Railway Dashboard:
1. Ve a tu servicio
2. Click en "Deployments"
3. Click en el deployment activo
4. Ver logs en tiempo real

### Logs importantes a monitorear

```
✅ News Scraper - Starting
✅ Supabase configuration validated
✅ OpenRouter API key configured
✅ Playwright Chromium is ready
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  STARTING FULL PIPELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 🔄 Pipeline de Ejecución

1. **Scraping** (5-10 min)
   - Scraping de La Nación y Clarín
   - 4 categorías: Economía, Política, Sociedad, Internacional
   - ~20 artículos por categoría

2. **LLM Rewriting** (10-15 min)
   - Reescritura con modelo seleccionado
   - Costo estimado: ~$0.10-0.30 USD por ejecución (Claude)
   - Costo estimado: ~$0.01-0.05 USD por ejecución (DeepSeek)

3. **Upload a Supabase** (2-3 min)
   - Subida de imágenes a Supabase Storage
   - Inserción de artículos en DB
   - Validación de duplicados por source_url

4. **Cleanup** (1 min)
   - Eliminación de noticias > 3 días
   - Limpieza de imágenes huérfanas

**Total por ejecución:** ~20-30 minutos

## 🎯 Modos de Ejecución

### Modo Continuo (Producción)
```bash
RUN_MODE=continuous
SCRAPE_INTERVAL=43200  # 12 horas
```
- Se ejecuta cada 12 horas automáticamente
- Ideal para producción
- Railway mantiene el container siempre corriendo

### Modo Once (Testing)
```bash
RUN_MODE=once
```
- Se ejecuta una sola vez y termina
- Ideal para testing
- Railway detendrá el container al finalizar

## 💰 Costos Estimados

### Railway
- **Starter Plan**: $5 USD/mes
  - $5 de créditos incluidos
  - Suficiente para ~500 horas de ejecución

### OpenRouter (LLM)
- **DeepSeek V3.2 Exp** (RECOMENDADO - Mejor relación calidad/precio):
  - ~$0.03-0.05 USD por ejecución (80 artículos)
  - ~$1.50-2.50 USD/mes (2 ejecuciones/día)
  - Calidad comparable a Claude 3.5 Sonnet

- **DeepSeek Chat** (Más económico):
  - ~$0.02 USD por ejecución (80 artículos)
  - ~$1 USD/mes (2 ejecuciones/día)

- **Claude 3.5 Sonnet** (Premium):
  - ~$0.20 USD por ejecución (80 artículos)
  - ~$10 USD/mes (2 ejecuciones/día)

### Supabase
- **Free Tier**: $0/mes
  - 500 MB database
  - 1 GB Storage (imágenes)
  - 2 GB transferencia
  - Suficiente para ~500-1000 noticias

**Total mensual estimado:** $6.50-7.50 USD (usando DeepSeek V3.2 Exp)

## 🔧 Troubleshooting

### Error: "Playwright Chromium verification failed"
**Solución:** Railway está instalando Chromium automáticamente. Espera ~30 segundos.

### Error: "SUPABASE_SERVICE_KEY is not set"
**Solución:** Asegúrate de configurar la **service_role** key, no solo la anon key.

### Error: "Failed to upload image"
**Solución:**
1. Verifica que el bucket "noticias" existe en Supabase Storage
2. Verifica las políticas RLS del bucket
3. Verifica que SUPABASE_SERVICE_KEY tenga permisos

### Build muy lento
**Solución:**
1. Railway cachea builds. El segundo build será mucho más rápido.
2. Asegúrate de que `.dockerignore` esté configurado correctamente
3. No incluyas `data/` ni `logs/` en el build

### Container se reinicia constantemente
**Solución:**
1. Revisa los logs: `railway logs`
2. Verifica que todas las variables estén configuradas
3. Si es modo "once", es normal que termine

## 🚀 Comandos Útiles

```bash
# Ver logs en tiempo real
railway logs

# Ver estado del deployment
railway status

# Abrir dashboard web
railway open

# Re-deployar (force)
railway up --detach

# Ver variables configuradas
railway variables

# Shell interactivo en el container (debugging)
railway run bash
```

## 📈 Mejoras Futuras

- [ ] Webhook para notificaciones de nuevas noticias
- [ ] API REST para consultar estadísticas
- [ ] Dashboard web para monitoreo
- [ ] Soporte para más fuentes (Infobae, Página/12, etc.)
- [ ] Clasificación automática con ML
- [ ] Detección de trending topics

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs: `railway logs`
2. Verifica variables de entorno
3. Revisa la documentación de [Railway](https://docs.railway.app)
4. Abre un issue en el repositorio

---

**¡Happy scraping! 🎉**
