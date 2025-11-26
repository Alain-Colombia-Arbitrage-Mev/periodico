# 🚀 Deploy Inmediato - Railway

Proyecto vinculado: `6f2c8ac4-3a71-4878-b6f8-504e3b0ebf79`

## Paso 1: Configurar Variables de Entorno

```bash
# Supabase (OBLIGATORIAS)
railway variables set SUPABASE_URL="https://tu-proyecto.supabase.co"
railway variables set SUPABASE_KEY="tu-anon-key"
railway variables set SUPABASE_SERVICE_KEY="tu-service-role-key"

# OpenRouter (OBLIGATORIA)
railway variables set OPENROUTER_API_KEY="sk-or-v1-tu-key"

# LLM Model (OPCIONAL - ya tiene default)
railway variables set LLM_MODEL="deepseek/deepseek-v3.2-exp"

# Configuración (OPCIONAL)
railway variables set SCRAPE_INTERVAL="43200"
railway variables set MAX_ARTICLES_PER_CATEGORY="20"
railway variables set DELETE_OLD_ARTICLES="true"
railway variables set OLD_ARTICLES_DAYS="3"
railway variables set LOG_LEVEL="INFO"
```

## Paso 2: Deploy

```bash
# Desde /scraper
railway up
```

O si prefieres deployar detached (en background):
```bash
railway up --detach
```

## Paso 3: Monitorear Deployment

```bash
# Ver logs en tiempo real
railway logs -f
```

Deberías ver:
```
✅ News Scraper - Starting
✅ Supabase configuration validated
✅ OpenRouter API key configured
✅ LLM model: deepseek/deepseek-v3.2-exp
✅ Playwright Chromium is ready
Starting application...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  STARTING FULL PIPELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Paso 4: Verificar en Dashboard

```bash
# Abrir Railway Dashboard
railway open
```

En el Dashboard verás:
- Build progress
- Deployment status
- Logs en tiempo real
- Métricas de CPU/Memory

## ⚠️ Antes de Deploy - Checklist

- [ ] Tienes las credenciales de Supabase listas
- [ ] Tienes la API key de OpenRouter
- [ ] El bucket "noticias" existe en Supabase Storage
- [ ] Tienes créditos en OpenRouter ($5 mínimo recomendado)

## 🔑 Dónde Obtener Credenciales

### Supabase
1. Ve a https://supabase.com/dashboard
2. Selecciona tu proyecto
3. Settings > API
4. Copia:
   - URL: `https://xxxxx.supabase.co`
   - anon public key
   - service_role key (⚠️ secreta!)

### OpenRouter
1. Ve a https://openrouter.ai/keys
2. Crea una nueva key
3. Copia la key (comienza con `sk-or-v1-`)
4. Recarga créditos en https://openrouter.ai/credits

## 📊 Después del Deploy

### Verificar que funciona

```bash
# Ver logs
railway logs

# Ver estado
railway status

# Ver variables configuradas
railway variables
```

### Primera ejecución

El pipeline completo toma ~20-30 minutos:
- Scraping: 5-10 min
- LLM Rewriting: 10-15 min
- Upload: 2-3 min
- Cleanup: 1 min

### Verificar datos en Supabase

1. Ve a tu proyecto Supabase
2. Table Editor > noticias
3. Deberías ver las noticias reescritas
4. Storage > noticias - Deberías ver las imágenes

## 🎯 Comandos Útiles

```bash
# Ver logs continuos
railway logs -f

# Restart del servicio
railway restart

# Ver variables
railway variables

# Abrir dashboard
railway open

# Ver info del proyecto
railway status

# Shell en el container (debugging)
railway run bash
```

## 🔧 Troubleshooting Rápido

### Build falla
```bash
# Ver logs del build
railway logs --build

# Re-deployar forzando rebuild
railway up --detach
```

### Container se reinicia
```bash
# Ver por qué crashea
railway logs | grep ERROR

# Verificar variables
railway variables
```

### No hay noticias en Supabase
```bash
# Verificar que el scraper terminó
railway logs | grep "PIPELINE COMPLETE"

# Verificar errores de Supabase
railway logs | grep "Supabase"
```

## 💰 Monitorear Costos

### Railway
- Dashboard > Usage
- Verás horas de ejecución y costo acumulado

### OpenRouter
- https://openrouter.ai/activity
- Verás requests, tokens y costo por modelo

---

**¡Listo para deployar!** 🚀
