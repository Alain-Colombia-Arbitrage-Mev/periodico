'use client';

import NYTHeader from '@/components/nyt/Header';
import Link from 'next/link';
import { Shield, Eye, Lock, Database, UserCheck } from 'lucide-react';

export default function PrivacidadPage() {
  return (
    <div className="min-h-screen bg-white">
      <NYTHeader />

      <main className="max-w-[1440px] mx-auto px-10 py-12">
        <h1 className="text-4xl font-bold mb-4 pb-4 border-b-2 border-black" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
          Política de Privacidad
        </h1>
        <p className="text-sm mb-8" style={{ color: 'var(--nyt-text-gray)' }}>Última actualización: Noviembre 2025</p>

        <div className="grid md:grid-cols-3 gap-4 mb-12">
          <div className="bg-blue-50 p-4 rounded-lg text-center">
            <Shield className="w-8 h-8 text-blue-600 mx-auto mb-2" />
            <h3 className="font-bold text-sm">Protección Total</h3>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg text-center">
            <Lock className="w-8 h-8 text-blue-600 mx-auto mb-2" />
            <h3 className="font-bold text-sm">Datos Encriptados</h3>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg text-center">
            <UserCheck className="w-8 h-8 text-blue-600 mx-auto mb-2" />
            <h3 className="font-bold text-sm">Control del Usuario</h3>
          </div>
        </div>

        <div className="prose prose-lg max-w-none">
          <h2>1. Información que Recopilamos</h2>

          <h3>1.1. Información que nos proporciona directamente:</h3>
          <ul>
            <li>Nombre y dirección de correo electrónico (al suscribirse al newsletter)</li>
            <li>Comentarios y opiniones que publique en el sitio</li>
            <li>Información de contacto cuando nos envía mensajes</li>
          </ul>

          <h3>1.2. Información recopilada automáticamente:</h3>
          <ul>
            <li>Dirección IP y datos de navegación</li>
            <li>Tipo de navegador y dispositivo</li>
            <li>Páginas visitadas y tiempo de permanencia</li>
            <li>Cookies y tecnologías similares</li>
          </ul>

          <h2>2. Cómo Utilizamos su Información</h2>
          <p>
            Utilizamos la información recopilada para:
          </p>
          <ul>
            <li>Proporcionar, operar y mantener nuestro sitio web</li>
            <li>Mejorar y personalizar su experiencia de usuario</li>
            <li>Enviar nuestro newsletter (solo si se suscribió)</li>
            <li>Responder a sus comentarios y preguntas</li>
            <li>Analizar el uso del sitio y generar estadísticas</li>
            <li>Detectar y prevenir fraudes o usos indebidos</li>
            <li>Cumplir con obligaciones legales</li>
          </ul>

          <h2>3. Cookies y Tecnologías de Seguimiento</h2>
          <p>
            Utilizamos cookies y tecnologías similares para:
          </p>
          <ul>
            <li><strong>Cookies esenciales:</strong> Necesarias para el funcionamiento del sitio</li>
            <li><strong>Cookies analíticas:</strong> Para entender cómo los usuarios usan nuestro sitio</li>
            <li><strong>Cookies de preferencias:</strong> Para recordar sus configuraciones</li>
          </ul>
          <p>
            Puede configurar su navegador para rechazar cookies, pero esto puede afectar
            la funcionalidad del sitio.
          </p>

          <h2>4. Compartir Información con Terceros</h2>
          <p>
            No vendemos ni alquilamos su información personal a terceros. Podemos compartir
            información en los siguientes casos:
          </p>
          <ul>
            <li><strong>Proveedores de servicios:</strong> Empresas que nos ayudan a operar el sitio (hosting, analytics)</li>
            <li><strong>Cumplimiento legal:</strong> Cuando sea requerido por ley o autoridades competentes</li>
            <li><strong>Protección de derechos:</strong> Para proteger nuestros derechos legales o los de terceros</li>
          </ul>

          <h2>5. Seguridad de los Datos</h2>
          <p>
            Implementamos medidas de seguridad técnicas y organizativas para proteger su
            información personal, incluyendo:
          </p>
          <ul>
            <li>Encriptación SSL/TLS para transmisión de datos</li>
            <li>Servidores seguros con acceso restringido</li>
            <li>Copias de seguridad regulares</li>
            <li>Auditorías de seguridad periódicas</li>
          </ul>

          <h2>6. Sus Derechos</h2>
          <p>
            Conforme a la Ley de Protección de Datos Personales argentina (Ley 25.326),
            usted tiene derecho a:
          </p>
          <ul>
            <li><strong>Acceder</strong> a sus datos personales que conservamos</li>
            <li><strong>Rectificar</strong> información incorrecta o desactualizada</li>
            <li><strong>Eliminar</strong> sus datos personales (derecho al olvido)</li>
            <li><strong>Oponerse</strong> al procesamiento de sus datos</li>
            <li><strong>Portabilidad</strong> de sus datos a otro servicio</li>
            <li><strong>Revocar</strong> el consentimiento en cualquier momento</li>
          </ul>
          <p>
            Para ejercer estos derechos, contáctenos en: privacidad@politicaargentina.com
          </p>

          <h2>7. Retención de Datos</h2>
          <p>
            Conservamos su información personal solo durante el tiempo necesario para
            cumplir con los propósitos descritos en esta política, o según lo requiera
            la ley argentina.
          </p>

          <h2>8. Enlaces a Sitios de Terceros</h2>
          <p>
            Nuestro sitio puede contener enlaces a sitios web de terceros. No somos
            responsables de las prácticas de privacidad de estos sitios externos.
            Le recomendamos leer sus políticas de privacidad.
          </p>

          <h2>9. Privacidad de Menores</h2>
          <p>
            Nuestro sitio no está dirigido a menores de 13 años. No recopilamos
            intencionalmente información personal de menores. Si descubrimos que hemos
            recopilado datos de un menor, los eliminaremos de inmediato.
          </p>

          <h2>10. Cambios a esta Política</h2>
          <p>
            Podemos actualizar esta Política de Privacidad ocasionalmente. Le notificaremos
            sobre cambios significativos publicando la nueva política en esta página con
            una nueva fecha de "última actualización".
          </p>

          <h2>11. Contacto</h2>
          <p>
            Si tiene preguntas sobre esta Política de Privacidad o sobre cómo manejamos
            sus datos personales, contáctenos:
          </p>
          <ul>
            <li>Email: privacidad@politicaargentina.com</li>
            <li>Teléfono: +54 11 5555-0123</li>
            <li>Dirección: Av. Corrientes 1234, Piso 5, Buenos Aires, Argentina</li>
          </ul>

          <div className="bg-blue-50 border-l-4 border-blue-600 p-6 my-8">
            <h3 className="text-lg font-bold text-blue-900 mb-2">
              Responsable del Tratamiento de Datos
            </h3>
            <p className="text-sm text-gray-700">
              Política Argentina es el responsable del tratamiento de sus datos personales.
              Estamos registrados ante la Agencia de Acceso a la Información Pública (AAIP)
              conforme a la normativa argentina vigente.
            </p>
          </div>

          <p className="text-center text-gray-600 mt-8">
            Para más información sobre sus derechos, visite{' '}
            <a
              href="https://www.argentina.gob.ar/aaip"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              el sitio de la AAIP
            </a>
          </p>
        </div>
      </main>
    </div>
  );
}
