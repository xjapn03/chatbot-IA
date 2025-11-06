# Frontend - Chatbot NICSP

Interfaz de usuario en Next.js 16 con React y Tailwind CSS para el chatbot NICSP.

## 🚀 Inicio Rápido

```bash
# Instalar dependencias
npm install

# Modo desarrollo
npm run dev

# Build para producción
npm run build

# Iniciar producción
npm start
```

El frontend estará disponible en: `http://localhost:3000`

## 📁 Estructura

```
frontend/
├── app/
│   ├── Chatbot.jsx      # Componente principal del chat
│   ├── page.tsx         # Página principal
│   ├── layout.tsx       # Layout raíz
│   └── globals.css      # Estilos globales
├── public/              # Archivos estáticos
└── package.json         # Dependencias
```

## 🎨 Componentes

### Chatbot.jsx

Componente principal que maneja:
- Estado de mensajes
- Comunicación con API backend
- UI del chat con Tailwind CSS
- Manejo de errores

```jsx
import Chatbot from "./Chatbot";

export default function MyPage() {
  return <Chatbot />;
}
```

## 🔌 Configuración de API

El frontend se conecta al backend en `http://localhost:5000`

Para cambiar la URL, edita `app/Chatbot.jsx`:
```jsx
const res = await fetch("http://localhost:5000/chat", {
  // ...
});
```

Para producción, usa variables de entorno:
```jsx
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";
```

## 🎨 Personalización

### Colores

Edita las clases de Tailwind en `Chatbot.jsx`:
```jsx
// Mensajes del usuario
className="bg-blue-500 text-white"

// Mensajes del bot
className="bg-white dark:bg-gray-700"
```

### Altura del chat

En `Chatbot.jsx`:
```jsx
<div className="flex flex-col h-[600px] max-h-[70vh]">
```

### Estilos globales

Edita `app/globals.css` para estilos globales.

## 🐛 Troubleshooting

### Error: CORS policy blocked

Asegúrate de que el backend tenga CORS habilitado:
```python
# backend/app.py
from flask_cors import CORS
CORS(app)
```

### Error: fetch failed

- Verifica que el backend esté corriendo en puerto 5000
- Revisa la URL de la API en `Chatbot.jsx`

### Estilos no se aplican

```bash
# Limpia caché de Next.js
rm -rf .next
npm run dev
```

## 📦 Dependencias

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| next | 16.0.1 | Framework React |
| react | 19.2.0 | Librería UI |
| react-dom | 19.2.0 | Renderizado React |
| tailwindcss | 4.x | Estilos CSS |
| typescript | 5.x | Tipado estático |

## 🚀 Deploy

### Vercel (Recomendado)

```bash
npm install -g vercel
vercel
```

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Variables de Entorno

Crea `.env.local`:
```env
NEXT_PUBLIC_API_URL=https://tu-backend.com
```

## 📝 Próximas Mejoras

- [ ] TypeScript para Chatbot.jsx
- [ ] Tests con Jest/React Testing Library
- [ ] Modo oscuro persistente
- [ ] Exportar conversaciones
- [ ] Compartir conversaciones
- [ ] PWA support
- [ ] Notificaciones

