"use client";

import React, { useState, useEffect } from "react";


function Chatbot() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dots, setDots] = useState(0);
  const [typingMessage, setTypingMessage] = useState(null); // Para animación de escritura
  const [connectionWarning, setConnectionWarning] = useState(false); // Banner de conexión lenta
  const [loadingStartTime, setLoadingStartTime] = useState(null); // Tiempo de inicio de carga

  useEffect(() => {
    let interval;
    if (loading) {
      interval = setInterval(() => {
        setDots((prev) => (prev < 2 ? prev + 1 : 0));
      }, 500);
    } else {
      setDots(0);
    }
    return () => clearInterval(interval);
  }, [loading]);

  // Detectar conexión lenta (después de 10 segundos)
  useEffect(() => {
    let timer;
    if (loading && loadingStartTime) {
      timer = setTimeout(() => {
        setConnectionWarning(true);
      }, 10000); // 10 segundos
    } else {
      setConnectionWarning(false);
    }
    return () => clearTimeout(timer);
  }, [loading, loadingStartTime]);

  // Función auxiliar para actualizar el texto del mensaje animado
  function updateTypingMessage(id, fullText, i) {
    setMessages((prev) => prev.map((msg) =>
      msg.id === id
        ? { ...msg, text: fullText.slice(0, i) }
        : msg
    ));
  }

  // Animación de escritura para el mensaje del bot (menos anidación)
  useEffect(() => {
    if (typingMessage && typingMessage.fullText) {
      let i = 0;
      setMessages((prev) => [...prev, { sender: "bot", text: "", id: typingMessage.id }]);
      function handleTyping() {
        i++;
        updateTypingMessage(typingMessage.id, typingMessage.fullText, i);
        if (i >= typingMessage.fullText.length) {
          setTypingMessage(null);
          clearInterval(interval);
        }
      }
      const interval = setInterval(handleTyping, 18); // velocidad de escritura
      return () => clearInterval(interval);
    }
  }, [typingMessage]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const newMessage = { sender: "user", text: input, id: Date.now() };
    setMessages([...messages, newMessage]);
    setInput("");
    setLoading(true);
    setLoadingStartTime(Date.now());
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000); // Timeout de 120 segundos
      
      const res = await fetch("http://3.220.179.134:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      
      if (!res.ok) {
        throw new Error(`Error del servidor: ${res.status}`);
      }
      
      const data = await res.json();
      
      if (!data.response || data.response.trim() === "") {
        throw new Error("Sin respuesta del servidor");
      }
      
      // Animación de escritura para el bot
      setTypingMessage({
        id: Date.now() + 1,
        fullText: data.response,
      });
      
    } catch (error) {
      let errorMessage = "Error al conectar con el servidor";
      
      if (error.name === 'AbortError') {
        errorMessage = "❌ Tiempo de espera agotado. La conexión al servidor tardó demasiado. Por favor, verifica tu conexión a internet e intenta nuevamente.";
      } else if (error.message.includes("Failed to fetch")) {
        errorMessage = "❌ No se pudo establecer conexión con el servidor. Verifica que el backend esté ejecutándose y tu conexión a internet esté activa.";
      } else if (error.message.includes("Error del servidor: 500")) {
        errorMessage = "⚠️ El servidor está experimentando problemas técnicos. Por favor, intenta nuevamente en unos momentos.";
      } else if (error.message.includes("Sin respuesta del servidor")) {
        errorMessage = "Lo siento, no pude generar una respuesta. Por favor, reformula tu pregunta.";
      }
      
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: errorMessage, id: Date.now() },
      ]);
      console.error("Error:", error);
    }
    
    setLoading(false);
    setLoadingStartTime(null);
  };

  return (
    <div className="flex flex-col h-[600px] max-h-[70vh]">
      {/* Banner de advertencia de conexión lenta */}
      {connectionWarning && (
        <div className="mb-3 px-4 py-3 bg-yellow-100 dark:bg-yellow-900/30 border border-yellow-400 dark:border-yellow-600 rounded-lg">
          <p className="text-sm text-yellow-800 dark:text-yellow-200 flex items-center gap-2">
            <span className="text-lg">⚠️</span>
            <span>La conexión está tardando más de lo normal. Por favor, espera un momento...</span>
          </p>
        </div>
      )}
      
  <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900 rounded-lg no-scrollbar">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 dark:text-gray-400 mt-8">
            <p>¡Hola! Pregúntame sobre las NICSP</p>
          </div>
        )}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                msg.sender === "user"
                  ? "bg-blue-500 text-white"
                  : "bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-600"
              }`}
            >
              <p className="text-sm font-semibold mb-1">
                {msg.sender === "user" ? "Tú" : "Bot"}
              </p>
              <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="max-w-[80%] rounded-lg px-4 py-2 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-600">
              <p className="text-sm font-semibold mb-1">Bot</p>
              <p className="text-sm whitespace-pre-wrap">.{'.'.repeat(dots)}</p>
            </div>
          </div>
        )}
      </div>
      <div className="flex gap-2 mt-4">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Haz una pregunta sobre las NICSP..."
          className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
        />
        <button 
          onClick={sendMessage}
          className="px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={!input.trim()}
        >
          Enviar
        </button>
      </div>
    </div>
  );
}

export default Chatbot;