import Chatbot from "./Chatbot";

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <main className="w-full max-w-4xl mx-auto p-6">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8">
          <h1 className="text-4xl font-bold text-center mb-2 text-gray-800 dark:text-white">
            Chatbot NICSP
          </h1>
          <p className="text-center text-gray-600 dark:text-gray-300 mb-8">
            Asistente virtual para consultas sobre Normas Internacionales de Contabilidad del Sector Público
          </p>
          <Chatbot />
        </div>
      </main>
    </div>
  );
}
