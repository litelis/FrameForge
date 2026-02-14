# 🚀 Guía de Instalación y Setup - FrameForge

## 📋 Requisitos Previos

- **Python 3.8 o superior** (descargar desde https://www.python.org/downloads/)
- **Git** (descargar desde https://git-scm.com/downloads/)
- **FFmpeg** (Procesamiento de video/audio - descargar desde https://ffmpeg.org/)
- **Ollama** (Motor de IA local - descargar desde https://ollama.com/)
- **10GB+ de espacio libre** en disco (para modelos de IA)
- **GPU (Recomendado)**: NVIDIA con CUDA para mejor rendimiento
- **Conexión a internet** (para descargar dependencias y modelos)

---

## 🎯 Opción 1: Instalación Automática (RECOMENDADA)

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/litelis/FrameForge.git
cd FrameForge
```

### Paso 2: Ejecutar Script de Setup

```bash
python setup.py
```

El script `setup.py` hará automáticamente:

✅ **Verificar Python 3.8+** instalado  
✅ **Verificar e instalar** todas las dependencias de `requirements.txt`  
✅ **Crear directorios** necesarios (`uploads`, `outputs`, `logs`, `temp`)  
✅ **Inicializar Git** y configurar remote  
✅ **Mostrar instrucciones** finales de uso  

### Paso 3: Iniciar el Servidor

```bash
python app.py
```

### Paso 7: IA Local Standalone (Opcional)

Si quieres usar el motor de edición directo:

```bash
python ai_editor.py video.mp4 "Request"
```

Abre tu navegador en: **http://localhost:5000**

---

## 🛠️ Opción 2: Instalación Manual

Si prefieres control total o el script automático falla:

### Paso 1: Clonar Repositorio

```bash
git clone https://github.com/litelis/FrameForge.git
cd FrameForge
```

### Paso 2: Crear Entorno Virtual (Recomendado)

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Dependencias instaladas:**
- Flask 2.3.3 - Framework web
- Flask-SocketIO 5.3.6 - Comunicación en tiempo real
- Flask-CORS 4.0.0 - Cross-origin requests
- Pydantic 1.10.12 - Validación de datos
- aiohttp 3.8.5 - Cliente HTTP async
- python-socketio 5.8.0 - Socket.IO server
- requests 2.32.5 - HTTP requests
- Werkzeug 2.3.7 - WSGI utilities
- python-dotenv 1.0.0 - Variables de entorno

### Paso 4: Crear Directorios

```bash
mkdir uploads outputs logs temp
```

### Paso 5: Inicializar Git (Opcional)

```bash
git init
git remote add origin https://github.com/litelis/FrameForge.git
```

### Paso 6: Iniciar Servidor

```bash
python app.py
```

---

## 🔧 Solución de Problemas

### Error: "No module named 'flask'"

**Causa:** Dependencias no instaladas  
**Solución:**
```bash
pip install -r requirements.txt
```

### Error: "Python no reconocido"

**Causa:** Python no está en el PATH  
**Solución Windows:**
1. Reinstalar Python marcando "Add Python to PATH"
2. O usar: `C:\Users\TU_USUARIO\AppData\Local\Programs\Python\Python311\python.exe`

### Error: "Puerto 5000 en uso"

**Causa:** Otro programa usa el puerto 5000  
**Solución:** Modificar `app.py` y cambiar `port=5000` a `port=5001`

### Error: "Permission denied" en Git

**Causa:** Problemas de permisos  
**Solución:**
```bash
# Configurar usuario de Git
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
```

---

## 🧪 Verificar Instalación

Ejecuta las pruebas para verificar que todo funciona:

```bash
python test_api.py
```

**Resultado esperado:** ✅ 5/5 pruebas pasando

---

## 📝 Configuración Post-Instalación

### Variables de Entorno (Opcional)

Crea archivo `.env` en la raíz del proyecto:

```env
# Configuración Flask
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=tu-clave-secreta-aqui

# Webhook Discord (opcional)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### Configurar Webhook Discord

1. Ve a tu servidor Discord
2. Configuración del servidor → Integraciones → Webhooks
3. Crea webhook y copia la URL
4. En la interfaz web de FrameForge, pega la URL
5. Selecciona eventos a notificar

---

## 🎮 Uso Básico

### 1. Iniciar Servidor
```bash
python app.py
```

### 2. Abrir Navegador
```
http://localhost:5000
```

### 3. Flujo de Trabajo
1. **Sube** tu video (drag & drop)
2. **Escribe** tu prompt en Fase 1
3. **Aprueba** el prompt mejorado
4. **Responde** preguntas en Fase 2
5. **Revisa** el plan de escenas en Fase 4
6. **Descarga** tu video editado

---

## 📁 Estructura de Archivos Después del Setup

```
FrameForge/
├── app.py                 # Servidor principal
├── setup.py              # Script de instalación
├── test_api.py           # Pruebas
├── requirements.txt      # Dependencias
├── .gitignore           # Git ignore
├── .env                 # Variables de entorno (tú lo creas)
├── README.md            # Documentación
├── SETUP_GUIDE.md       # Esta guía
├── uploads/             # Videos subidos
│   └── .gitkeep
├── outputs/             # Videos procesados
│   └── .gitkeep
├── logs/                # Logs del sistema
│   └── .gitkeep
├── temp/                # Archivos temporales
│   └── .gitkeep
├── phases/              # Lógica de fases
├── models/              # Modelos de datos
├── utils/               # Utilidades
├── templates/           # HTML
└── static/              # CSS/JS
```

---

## 🆘 Soporte

Si encuentras problemas:

1. **Revisa** TEST_REPORT.md para verificar funcionamiento
2. **Ejecuta** `python test_api.py` para diagnosticar
3. **Consulta** el repositorio: https://github.com/litelis/FrameForge.git
4. **Abre un issue** en GitHub si persiste el problema

---

## ✅ Checklist de Instalación

- [ ] Python 3.8+ instalado
- [ ] Git instalado
- [ ] Repositorio clonado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Directorios creados (`uploads`, `outputs`, `logs`, `temp`)
- [ ] Servidor inicia sin errores (`python app.py`)
- [ ] Pruebas pasan (`python test_api.py`)
- [ ] Interfaz web accesible en `http://localhost:5000`

---

**¡Listo para crear arte cinematográfico! 🎬✨**
