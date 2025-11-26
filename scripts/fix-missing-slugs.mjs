#!/usr/bin/env node
import { createClient } from '@supabase/supabase-js';

// Función simple para crear slugs sin dependencias externas
function slugify(text) {
  return text
    .toString()
    .toLowerCase()
    .trim()
    .normalize('NFD') // Normalizar caracteres Unicode
    .replace(/[\u0300-\u036f]/g, '') // Eliminar diacríticos
    .replace(/[^a-z0-9\s-]/g, '') // Eliminar caracteres especiales
    .replace(/\s+/g, '-') // Reemplazar espacios con guiones
    .replace(/-+/g, '-') // Eliminar guiones duplicados
    .replace(/^-+/, '') // Eliminar guiones al inicio
    .replace(/-+$/, ''); // Eliminar guiones al final
}

// Configuración de Supabase
const supabaseUrl = 'https://dnacsmoubqrzpbvjhary.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRuYWNzbW91YnFyenBidmpoYXJ5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI4MTY3MDYsImV4cCI6MjA3ODM5MjcwNn0.xIZw6wsO-YHzTNQXpLCvrI5hWLFefjyz2wLA1lNMX6Y';

const supabase = createClient(supabaseUrl, supabaseAnonKey);

console.log('🔍 Buscando noticias con slugs faltantes o inválidos...\n');

// Buscar todas las noticias con slug NULL, undefined o vacío
const { data: noticias, error } = await supabase
  .from('noticias')
  .select('id, title, slug')
  .or('slug.is.null,slug.eq.undefined,slug.eq.');

if (error) {
  console.error('❌ Error al consultar noticias:', error.message);
  process.exit(1);
}

if (!noticias || noticias.length === 0) {
  console.log('✅ No se encontraron noticias con slugs faltantes');
  process.exit(0);
}

console.log(`📝 Encontradas ${noticias.length} noticias sin slug:\n`);

let fixed = 0;
let failed = 0;

for (const noticia of noticias) {
  console.log(`   ID: ${noticia.id}`);
  console.log(`   Título: ${noticia.title?.substring(0, 60)}...`);
  console.log(`   Slug actual: ${noticia.slug || '(vacío)'}`);

  if (!noticia.title) {
    console.log('   ❌ No se puede generar slug: título vacío\n');
    failed++;
    continue;
  }

  // Generar nuevo slug
  const newSlug = slugify(noticia.title);

  console.log(`   Nuevo slug: ${newSlug}`);

  // Actualizar en la base de datos
  const { error: updateError } = await supabase
    .from('noticias')
    .update({ slug: newSlug })
    .eq('id', noticia.id);

  if (updateError) {
    console.log(`   ❌ Error al actualizar: ${updateError.message}\n`);
    failed++;
  } else {
    console.log('   ✅ Slug actualizado correctamente\n');
    fixed++;
  }
}

console.log('─────────────────────────────────────────────────────');
console.log(`\n📊 Resumen:`);
console.log(`   ✅ Corregidos: ${fixed}`);
console.log(`   ❌ Fallidos: ${failed}`);
console.log(`   📝 Total procesados: ${noticias.length}\n`);
