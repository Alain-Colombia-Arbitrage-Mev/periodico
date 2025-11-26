const fs = require('fs');
const path = require('path');

// Mapeo de imágenes placeholder a URLs de Unsplash reales
const imageMap = {
  '/images/dolar-blue-1.jpg': 'https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=1200&h=800&fit=crop',
  '/images/economia-argentina-1.jpg': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&h=800&fit=crop',
  '/images/milei-1.jpg': 'https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=1200&h=800&fit=crop',
  '/images/milei-2.jpg': 'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=1200&h=800&fit=crop',
  '/images/milei-3.jpg': 'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=1200&h=800&fit=crop',
  '/images/casa-rosada-1.jpg': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1200&h=800&fit=crop',
  '/images/casa-rosada-2.jpg': 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200&h=800&fit=crop',
  '/images/argentina-celebracion-1.jpg': 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1200&h=800&fit=crop',
  '/images/argentina-celebracion-2.jpg': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=1200&h=800&fit=crop',
};

// Leer el archivo
const filePath = path.join(__dirname, '..', 'app', 'data', 'noticias.ts');
let content = fs.readFileSync(filePath, 'utf8');

// Reemplazar URLs
for (const [placeholder, realUrl] of Object.entries(imageMap)) {
  const regex = new RegExp(placeholder.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
  content = content.replace(regex, realUrl);
}

// Guardar el archivo
fs.writeFileSync(filePath, content, 'utf8');

console.log('✅ Se actualizaron las URLs de imágenes');
