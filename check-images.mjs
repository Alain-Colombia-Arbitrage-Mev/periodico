import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  'https://dnacsmoubqrzpbvjhary.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRuYWNzbW91YnFyenBidmpoYXJ5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjgxNjcwNiwiZXhwIjoyMDc4MzkyNzA2fQ.DW5uBBOYv-2eGP830lCTnWM800_WYXmNwQWl2Bg8tpc'
);

const { data, error } = await supabase
  .from('noticias')
  .select('id, title, image_url, category_id')
  .eq('status', 'published');

if (error) {
  console.error('Error:', error);
  process.exit(1);
}

console.log('📊 Total artículos:', data.length);
console.log('\n🖼️  Análisis de imágenes:');
console.log('- Imágenes en Supabase Storage:', data.filter(n => n.image_url?.includes('supabase.co/storage')).length);
console.log('- Imágenes con data:image (placeholders):', data.filter(n => n.image_url?.includes('data:image')).length);
console.log('- Imágenes externas:', data.filter(n => !n.image_url?.includes('supabase.co') && !n.image_url?.includes('data:image')).length);

console.log('\n📋 Muestra de URLs en Supabase:');
const supabaseImages = data.filter(n => n.image_url?.includes('supabase.co/storage')).slice(0, 5);
supabaseImages.forEach((n, i) => {
  console.log(`${i+1}. ${n.title.substring(0, 50)}...`);
  console.log(`   ${n.image_url}`);
});

// Verificar si hay imágenes que referencian "data:image" en el path de Supabase
const badImages = data.filter(n => n.image_url?.includes('data:image'));
if (badImages.length > 0) {
  console.log('\n❌ Imágenes con problemas (data:image en URL):');
  badImages.slice(0, 5).forEach(n => {
    console.log(`- ${n.title.substring(0, 50)}...`);
    console.log(`  ${n.image_url.substring(0, 150)}...`);
  });
}
