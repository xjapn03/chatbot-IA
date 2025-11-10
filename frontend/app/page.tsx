import Chatbot from "./Chatbot";
import Image from "next/image";

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <main className="w-full max-w-4xl mx-auto p-6">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8">
          {/* Header con título y logos en la misma línea */}
          <div className="flex items-center justify-between gap-4 mb-2">
            {/* Logo izquierdo - NICSP */}
            <div className="flex-shrink-0">
              <Image
                src="/logos/nicsplogo.png"
                alt="NICSP Logo"
                width={90}
                height={90}
                className="object-contain hover:scale-105 transition-transform"
              />
            </div>

            {/* Título central */}
            <h1 className="text-4xl font-bold text-center text-gray-800 dark:text-white">
              Chatbot NICSP
            </h1>

            {/* Logo derecho - Areandina */}
            <div className="flex-shrink-0">
              <Image
                src="/logos/areandinalogo.png"
                alt="Areandina Logo"
                width={60}
                height={60}
                className="object-contain hover:scale-105 transition-transform"
              />
            </div>
          </div>

          <p className="text-center text-gray-600 dark:text-gray-300 mb-8">
            Asistente virtual para consultas sobre Normas Internacionales de Contabilidad del Sector Público
          </p>
          <Chatbot />
        </div>
      </main>
    </div>
  );
}