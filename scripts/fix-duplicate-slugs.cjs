const fs = require('fs');
const path = require('path');

// Leer el archivo
const filePath = path.join(__dirname, '..', 'app', 'data', 'noticias.ts');
let content = fs.readFileSync(filePath, 'utf8');

// Eliminar slugs duplicados - mantener solo el primer slug después del title
const lines = content.split('\n');
const newLines = [];
let lastWasSlug = false;

for (const line of lines) {
  if (line.trim().startsWith('slug:')) {
    if (!lastWasSlug) {
      newLines.push(line);
      lastWasSlug = true;
    }
    // Si lastWasSlug es true, omitir esta línea (es un duplicado)
  } else {
    newLines.push(line);
    lastWasSlug = false;
  }
}

// Guardar el archivo
fs.writeFileSync(filePath, newLines.join('\n'), 'utf8');

console.log('✅ Se eliminaron los slugs duplicados');
