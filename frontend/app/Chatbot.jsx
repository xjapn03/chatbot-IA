"use client";

import React, { useState, useEffect } from "react";

// URL del backend desde variable de entorno
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

function Chatbot() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dots, setDots] = useState(0);
  const [typingMessage, setTypingMessage] = useState(null); // Para animación de escritura
  const [connectionWarning, setConnectionWarning] = useState(false); // Banner de conexión lenta
  const [loadingStartTime, setLoadingStartTime] = useState(null); // Tiempo de inicio de carga
  const [selectedFile, setSelectedFile] = useState(null); // Archivo PDF seleccionado

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

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === "application/pdf") {
      setSelectedFile(file);
    } else if (file) {
      alert("Por favor selecciona solo archivos PDF");
      e.target.value = null;
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const newMessage = { 
      sender: "user", 
      text: selectedFile ? `📄 ${selectedFile.name}: ${input}` : input, 
      id: Date.now() 
    };
    setMessages([...messages, newMessage]);
    
    const currentInput = input;
    const currentFile = selectedFile;
    
    setInput("");
    setSelectedFile(null);
    setLoading(true);
    setLoadingStartTime(Date.now());
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000);
      
      let res;
      
      if (currentFile) {
        // Enviar con archivo
        const formData = new FormData();
        formData.append('file', currentFile);
        formData.append('question', currentInput);
        
        res = await fetch(`${API_URL}/upload`, {
          method: "POST",
          body: formData,
          signal: controller.signal,
        });
      } else {
        // Enviar solo texto
        res = await fetch(`${API_URL}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: currentInput }),
          signal: controller.signal,
        });
      }
      
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
      <div className="mt-4 space-y-3">
        {/* Mostrar archivo seleccionado */}
        {selectedFile && (
          <div className="flex items-center gap-2 p-3 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-700 rounded-lg">
            <span className="text-2xl">📄</span>
            <span className="text-sm text-blue-800 dark:text-blue-200 flex-1">{selectedFile.name}</span>
            <button
              onClick={() => setSelectedFile(null)}
              className="text-red-500 hover:text-red-700 font-bold"
            >
              ✕
            </button>
          </div>
        )}
        
        <div className="flex gap-2">
          {/* Botón para adjuntar PDF */}
          <label className="px-4 py-3 bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500 text-gray-800 dark:text-white font-semibold rounded-lg transition-colors cursor-pointer flex items-center gap-2">
            <span>📎</span>
            <span className="hidden sm:inline">PDF</span>
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="hidden"
            />
          </label>
          
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
            placeholder={selectedFile ? "Pregunta sobre el PDF..." : "Haz una pregunta sobre las NICSP..."}
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
    </div>
  );
}

export default Chatbot;