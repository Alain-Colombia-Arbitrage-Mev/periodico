#!/usr/bin/env node

/**
 * Script para verificar que solo se use .env como archivo de variables de entorno
 */

import { existsSync } from 'fs';
import { join } from 'path';

const rootDir = process.cwd();
const envFiles = [
  '.env.local',
  '.env.development',
  '.env.production',
  '.env.test',
  '.env.development.local',
  '.env.test.local',
  '.env.production.local',
];

console.log('🔍 Verificando archivos de variables de entorno...\n');

const foundFiles = [];
envFiles.forEach(file => {
  const filePath = join(rootDir, file);
  if (existsSync(filePath)) {
    foundFiles.push(file);
    console.log(`⚠️  Encontrado: ${file}`);
  }
});

if (foundFiles.length > 0) {
  console.log('\n❌ Se encontraron archivos de entorno adicionales.');
  console.log('📝 Este proyecto solo usa .env como archivo de variables de entorno.');
  console.log('\n💡 Solución:');
  console.log('   1. Mueve las variables de estos archivos a .env');
  console.log('   2. Elimina los archivos adicionales');
  console.log('\n📋 Archivos encontrados:');
  foundFiles.forEach(file => console.log(`   - ${file}`));
  process.exit(1);
} else {
  console.log('✅ Solo se está usando .env (correcto)');
  
  const envPath = join(rootDir, '.env');
  if (existsSync(envPath)) {
    console.log('✅ Archivo .env existe');
  } else {
    console.log('⚠️  Archivo .env no existe. Crea uno con tus variables de entorno.');
  }
  
  process.exit(0);
}

