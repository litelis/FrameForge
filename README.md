# 🎬 FrameForge - AI Cinematic Video Editor (Pro Version)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-5%2F5%20passing-brightgreen.svg)](TEST_REPORT.md)

**FrameForge** es un editor de video cinematográfico impulsado por IA con interfaz web local. Transforma videos raw en ediciones cinematográficas de alta calidad mediante un pipeline de 4 fases con razonamiento narrativo profundo.

🌐 **Repositorio:** https://github.com/litelis/FrameForge.git

---

## ✨ Características Principales

### 🎯 Sistema de 4 Fases

| Fase | Nombre | Descripción |
|------|--------|-------------|
| **1** | **Prompt Refinement** | Refina prompts del usuario sin cambiar su intención |
| **2** | **Intelligent Questioning** | Preguntas inteligentes para obtener información faltante |
| **3** | **Narrative Reasoning** | Análisis interno de arco narrativo y progresión emocional |
| **4** | **Scene Planning** | Director LLM genera plan de escenas cinematográficas |

### 🔗 Integración Discord Webhook

- 15+ eventos notificables configurables
- Notificaciones async no bloqueantes
- Rich embeds con project ID, fase y estado
- Sistema de retry con exponential backoff
- Completamente opcional

### 🖥️ Interfaz Web

- Tema cinematográfico oscuro moderno
- Indicadores de progreso de 6 fases
- Upload drag-and-drop de videos
- Panel de chat conversacional
- Configuración de webhooks
- Diseño responsive

---

## 🚀 Instalación Rápida

### Opción 1: Setup Automático (Recomendado)

```bash
# Clonar repositorio
git clone https://github.com/litelis/FrameForge.git
cd FrameForge

# Ejecutar script de setup
python setup.py
```

El script `setup.py` verificará e instalará automáticamente:
- ✅ Python 3.8+
- ✅ Todas las dependencias de requirements.txt
- ✅ Directorios necesarios (uploads, outputs, logs, temp)
- ✅ Repositorio Git con remote configurado

### Opción 2: Instalación Manual

```bash
# Clonar repositorio
git clone https://github.com/litelis/FrameForge.git
cd FrameForge

# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear directorios necesarios
mkdir uploads outputs logs temp
```

---

## 🎮 Uso

### Iniciar el Servidor

```bash
python app.py
```

El servidor iniciará en:
- 🌐 **Local:** http://localhost:5000
- 🌐 **Red:** http://TU_IP_LOCAL:5000 (accesible en tu red - ver tu IP con `ipconfig` o `ifconfig`)

### Flujo de Trabajo

1. **Abre** http://localhost:5000 en tu navegador
2. **Sube** tu video en el área de drag-and-drop
3. **Fase 1:** Escribe tu prompt y aprueba la versión mejorada
4. **Fase 2:** Responde las preguntas inteligentes sobre formato, plataforma, etc.
5. **Fase 3:** El sistema analiza la narrativa internamente
6. **Fase 4:** Revisa el plan de escenas cinematográficas generado
7. **Opcional:** Configura webhook de Discord para notificaciones

---

## 🧪 Pruebas

Ejecutar suite de pruebas completa:

```bash
python test_api.py
```

**Resultados esperados:** 5/5 pruebas pasando ✅

Ver informe detallado: [TEST_REPORT.md](TEST_REPORT.md)

---

## 📁 Estructura del Proyecto

```
FrameForge/
├── app.py                          # Servidor Flask principal
├── setup.py                        # Script de instalación automática
├── update.py                       # Verificador de actualizaciones
├── test_api.py                     # Suite de pruebas API
├── requirements.txt                # Dependencias Python
├── .gitignore                      # Archivos ignorados por Git
├── README.md                       # Este archivo
├── SETUP_GUIDE.md                  # Guía de instalación detallada
├── TEST_REPORT.md                  # Informe de pruebas
├── COMPLETION_SUMMARY.md           # Resumen de implementación
├── phases/                         # Handlers de las 4 fases
│   ├── __init__.py
│   ├── prompt_refiner.py          # Phase 1
│   ├── intelligent_questioning.py # Phase 2
│   ├── narrative_reasoning.py      # Phase 3
│   └── scene_planning.py          # Phase 4
├── models/                         # Modelos de datos
│   ├── __init__.py
│   └── schemas.py                  # Schemas Pydantic
├── utils/                          # Utilidades
│   ├── __init__.py
│   ├── webhook.py                  # Notificaciones Discord
│   └── validators.py               # Validación JSON
├── templates/                      # Templates HTML
│   └── index.html                  # Interfaz web principal
├── static/                         # Assets estáticos
│   ├── css/style.css               # Estilos cinematográficos
│   └── js/app.js                   # Lógica frontend
├── uploads/                        # Videos subidos (gitignored)
├── outputs/                        # Videos procesados (gitignored)
├── logs/                           # Logs del sistema (gitignored)
└── temp/                           # Archivos temporales (gitignored)
```

---

## 🔌 API Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Interfaz web principal |
| `/api/upload` | POST | Subir video |
| `/api/phase1/refine` | POST | Refinar prompt |
| `/api/phase1/approve` | POST | Aprobar/rechazar prompt |
| `/api/phase2/questions` | POST | Obtener preguntas |
| `/api/phase2/answer` | POST | Enviar respuesta |
| `/api/phase3/analyze` | POST | Análisis narrativo |
| `/api/phase4/plan` | POST | Planificación de escenas |
| `/api/webhook/config` | POST | Configurar webhook |
| `/api/transcription` | POST | Transcripción de audio |
| `/api/visual-analysis` | POST | Análisis visual |

---

## ⚙️ Configuración

### Variables de Entorno (Opcional)

Crea un archivo `.env` en la raíz:

```env
# Flask
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=tu-clave-secreta-aqui

# Discord Webhook (opcional)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### Configuración Webhook Discord

1. Ve a tu servidor Discord → Configuración del servidor → Integraciones → Webhooks
2. Crea un nuevo webhook y copia la URL
3. En la interfaz web de FrameForge, pega la URL en la sección de configuración
4. Selecciona los eventos que quieres recibir (upload, transcripción, fases, etc.)

---

## 🛠️ Stack Tecnológico

- **Backend:** Python 3.11, Flask 2.3.3, Flask-SocketIO 5.3.6
- **Validación:** Pydantic 1.10.12
- **Async:** aiohttp 3.8.5
- **Frontend:** HTML5, CSS3, JavaScript ES6+
- **Tiempo Real:** Socket.IO
- **Webhooks:** Discord API

---

## 📝 Requisitos del Sistema

- **Python:** 3.8 o superior
- **RAM:** 4GB mínimo (8GB recomendado)
- **Disco:** 2GB espacio libre mínimo
- **Navegador:** Chrome, Firefox, Safari, Edge (últimas versiones)
- **OS:** Windows 10/11, macOS 10.15+, Linux

---

## 🤝 Contribuir

1. Fork el repositorio: https://github.com/litelis/FrameForge.git
2. Crea una rama: `git checkout -b feature/nueva-feature`
3. Commit tus cambios: `git commit -am 'Añade nueva feature'`
4. Push a la rama: `git push origin feature/nueva-feature`
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está licenciado bajo MIT License - ver archivo [LICENSE](LICENSE) para detalles.

---

## 🙏 Agradecimientos

- Flask y su ecosistema
- Pydantic por la validación robusta
- La comunidad de código abierto

---

## 📞 Soporte

- **Issues:** https://github.com/litelis/FrameForge/issues
- **Documentación:** Este README, SETUP_GUIDE.md y TEST_REPORT.md

---

<p align="center">
  <b>🎬 FrameForge - Transformando videos en arte cinematográfico</b><br>
  <a href="https://github.com/litelis/FrameForge">https://github.com/litelis/FrameForge.git</a>
</p>
