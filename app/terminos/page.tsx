'use client';

import NYTHeader from '@/components/nyt/Header';
import Link from 'next/link';

export default function TerminosPage() {
  return (
    <div className="min-h-screen bg-white">
      <NYTHeader />

      <main className="max-w-[1440px] mx-auto px-10 py-12">
        <h1 className="text-4xl font-bold mb-4 pb-4 border-b-2 border-black" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
          Términos y Condiciones
        </h1>
        <p className="text-sm mb-8" style={{ color: 'var(--nyt-text-gray)' }}>Última actualización: Noviembre 2025</p>

        <div className="prose prose-lg max-w-none">
          <h2>1. Aceptación de los Términos</h2>
          <p>
            Al acceder y utilizar Política Argentina ("el Sitio"), usted acepta estar sujeto a
            estos Términos y Condiciones. Si no está de acuerdo con alguna parte de estos términos,
            no debe utilizar nuestro sitio web.
          </p>

          <h2>2. Uso del Contenido</h2>
          <p>
            Todo el contenido publicado en Política Argentina, incluyendo textos, imágenes, videos
            y gráficos, está protegido por derechos de autor y es propiedad de Política Argentina
            o de terceros que nos han otorgado licencia para su uso.
          </p>
          <ul>
            <li>Puede compartir enlaces a nuestros artículos en redes sociales</li>
            <li>Puede citar fragmentos de nuestros artículos con atribución adecuada</li>
            <li>No puede reproducir contenido completo sin autorización previa</li>
            <li>No puede modificar o crear obras derivadas de nuestro contenido</li>
          </ul>

          <h2>3. Comentarios y Contribuciones de Usuarios</h2>
          <p>
            Al enviar comentarios, opiniones u otro contenido al Sitio, usted otorga a
            Política Argentina una licencia mundial, no exclusiva y libre de regalías para
            usar, reproducir, modificar y publicar dicho contenido.
          </p>
          <p>
            Usted acepta que no publicará contenido que:
          </p>
          <ul>
            <li>Sea ilegal, difamatorio, obsceno o abusivo</li>
            <li>Viole los derechos de terceros</li>
            <li>Contenga virus o código malicioso</li>
            <li>Promueva actividades ilegales</li>
            <li>Incite al odio o la violencia</li>
          </ul>

          <h2>4. Privacidad y Datos Personales</h2>
          <p>
            El uso de su información personal está regulado por nuestra{' '}
            <Link href="/privacidad" className="text-blue-600 hover:underline">
              Política de Privacidad
            </Link>
            , que forma parte integral de estos Términos y Condiciones.
          </p>

          <h2>5. Enlaces a Sitios de Terceros</h2>
          <p>
            Nuestro Sitio puede contener enlaces a sitios web de terceros. No somos responsables
            del contenido, políticas de privacidad o prácticas de estos sitios externos.
          </p>

          <h2>6. Limitación de Responsabilidad</h2>
          <p>
            Política Argentina se esfuerza por mantener la precisión de la información publicada,
            pero no garantiza la exactitud, integridad o actualidad del contenido. El uso del Sitio
            es bajo su propio riesgo.
          </p>
          <p>
            No seremos responsables por:
          </p>
          <ul>
            <li>Errores u omisiones en el contenido</li>
            <li>Daños derivados del uso o imposibilidad de uso del Sitio</li>
            <li>Interrupciones o problemas técnicos</li>
            <li>Acciones de terceros</li>
          </ul>

          <h2>7. Modificaciones de los Términos</h2>
          <p>
            Nos reservamos el derecho de modificar estos Términos y Condiciones en cualquier
            momento. Los cambios entrarán en vigor inmediatamente después de su publicación en
            el Sitio. Su uso continuado del Sitio después de dichos cambios constituye su
            aceptación de los nuevos términos.
          </p>

          <h2>8. Propiedad Intelectual</h2>
          <p>
            El nombre "Política Argentina", logotipo y todos los diseños, gráficos y marcas
            relacionadas son propiedad de Política Argentina y están protegidos por las leyes
            de propiedad intelectual argentinas e internacionales.
          </p>

          <h2>9. Jurisdicción y Ley Aplicable</h2>
          <p>
            Estos Términos y Condiciones se regirán e interpretarán de acuerdo con las leyes
            de la República Argentina. Cualquier disputa relacionada con estos términos será
            sometida a los tribunales competentes de Buenos Aires, Argentina.
          </p>

          <h2>10. Contacto</h2>
          <p>
            Si tiene preguntas sobre estos Términos y Condiciones, puede contactarnos en:
          </p>
          <ul>
            <li>Email: legal@politicaargentina.com</li>
            <li>
              Dirección: Av. Corrientes 1234, Piso 5, Buenos Aires, Argentina
            </li>
          </ul>

          <div className="bg-gray-100 border-l-4 border-gray-600 p-6 my-8">
            <p className="text-sm text-gray-700">
              <strong>Nota:</strong> Estos términos constituyen un acuerdo legal entre usted y
              Política Argentina. Al usar nuestro sitio, usted reconoce haber leído, entendido
              y aceptado estos términos en su totalidad.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
