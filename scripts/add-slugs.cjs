const fs = require('fs');
const path = require('path');

function generateSlug(title) {
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

// Leer el archivo de noticias
const filePath = path.join(__dirname, '..', 'app', 'data', 'noticias.ts');
let content = fs.readFileSync(filePath, 'utf8');

// Regex para encontrar títulos y agregar slugs
const titleRegex = /title: '([^']+)',/g;
let match;
const replacements = [];

while ((match = titleRegex.exec(content)) !== null) {
  const title = match[1];
  const slug = generateSlug(title);

  // Buscar si ya tiene slug después del título
  const afterTitle = content.substring(match.index + match[0].length, match.index + match[0].length + 200);

  if (!afterTitle.includes('slug:')) {
    replacements.push({
      original: match[0],
      replacement: match[0] + `\n    slug: '${slug}',`
    });
  }
}

// Aplicar reemplazos
for (const rep of replacements) {
  content = content.replace(rep.original, rep.replacement);
}

// Guardar el archivo
fs.writeFileSync(filePath, content, 'utf8');

console.log(`✅ Se agregaron ${replacements.length} slugs al archivo de noticias`);
