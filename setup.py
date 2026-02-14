#!/usr/bin/env python3
"""
FrameForge - AI Cinematic Video Editor
Setup Script - Verifica e instala dependencias automáticamente
"""

import sys
import subprocess
import importlib
from pathlib import Path
import secrets
import string

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def print_config(text):
    print(f"{Colors.CYAN}⚙️  {text}{Colors.END}")

# Dependencias requeridas
REQUIRED_PACKAGES = {
    'flask': 'Flask>=2.3.0',
    'flask_socketio': 'flask-socketio>=5.3.0',
    'flask_cors': 'flask-cors>=4.0.0',
    'pydantic': 'pydantic>=1.10.0,<2.0.0',
    'aiohttp': 'aiohttp>=3.8.0',
    'socketio': 'python-socketio>=5.8.0',
    'requests': 'requests>=2.28.0',
    'werkzeug': 'werkzeug>=2.3.0',
    'dotenv': 'python-dotenv>=1.0.0',
}

OPTIONAL_PACKAGES = {
    'eventlet': 'eventlet>=0.33.0',
    'moviepy': 'moviepy>=1.0.3',
    'opencv_python': 'opencv-python>=4.8.0',
    'numpy': 'numpy>=1.24.0',
    'pillow': 'pillow>=10.0.0',
}

def check_python_version():
    """Verifica la versión de Python"""
    print_info("Verificando versión de Python...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python {version.major}.{version.minor} detectado")
        print_error("Se requiere Python 3.8 o superior")
        print_info("Descarga Python desde: https://www.python.org/downloads/")
        return False
    
    print_success(f"Python {version.major}.{version.minor}.{version.micro} ✅")
    return True

def check_package(package_name):
    """Verifica si un paquete está instalado"""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False


def install_package(package_spec):
    """Instala un paquete usando pip"""
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 
            '--quiet', package_spec
        ])
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_install_packages():
    """Verifica e instala todas las dependencias"""
    print_header("VERIFICANDO DEPENDENCIAS")
    
    missing_required = []
    missing_optional = []
    
    # Verificar paquetes requeridos
    print_info("Verificando paquetes REQUERIDOS...")
    for module, package in REQUIRED_PACKAGES.items():
        if check_package(module):
            print_success(f"{package.split('>=')[0]} instalado")
        else:
            print_warning(f"{package.split('>=')[0]} NO instalado")
            missing_required.append(package)
    
    # Verificar paquetes opcionales
    print_info("\nVerificando paquetes OPCIONALES...")
    for module, package in OPTIONAL_PACKAGES.items():
        if check_package(module):
            print_success(f"{package.split('>=')[0]} instalado")
        else:
            print_warning(f"{package.split('>=')[0]} NO instalado (opcional)")
            missing_optional.append(package)
    
    # Instalar paquetes faltantes
    if missing_required:
        print_header("INSTALANDO PAQUETES REQUERIDOS")
        print_info("Instalando dependencias necesarias...")
        
        for package in missing_required:
            print_info(f"Instalando {package}...")
            if install_package(package):
                print_success(f"{package} instalado correctamente")
            else:
                print_error(f"Falló la instalación de {package}")
                print_info(f"Intenta instalar manualmente: pip install {package}")
        
        # Verificar nuevamente
        still_missing = []
        for module, package in REQUIRED_PACKAGES.items():
            if not check_package(module):
                still_missing.append(package)
        
        if still_missing:
            print_error("\nAlgunos paquetes no se pudieron instalar:")
            for pkg in still_missing:
                print(f"  - {pkg}")
            print_info("\nPara instalar manualmente todos:")
            print(f"  pip install {' '.join(still_missing)}")
            return False
    else:
        print_success("\nTodos los paquetes requeridos están instalados!")
    
    # Instalar paquetes opcionales
    if missing_optional:
        print_header("INSTALANDO PAQUETES OPCIONALES")
        print_info("Instalando características adicionales...")
        
        for package in missing_optional:
            print_info(f"Instalando {package}...")
            if install_package(package):
                print_success(f"{package} instalado")
            else:
                print_warning(f"No se pudo instalar {package} (opcional)")
    
    return True

def create_directories():
    """Crea directorios necesarios"""
    print_header("CONFIGURANDO DIRECTORIOS")
    
    dirs = ['uploads', 'outputs', 'logs', 'temp']
    
    for dir_name in dirs:
        path = Path(dir_name)
        if not path.exists():
            path.mkdir(exist_ok=True)
            print_success(f"Directorio '{dir_name}' creado")
        else:
            print_info(f"Directorio '{dir_name}' ya existe")
    
    return True

def generate_secret_key():
    """Genera una clave secreta segura para Flask"""
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
    return ''.join(secrets.choice(alphabet) for _ in range(32))

def create_env_file():
    """Crea el archivo .env con explicaciones detalladas"""
    print_header("CONFIGURACIÓN DE VARIABLES DE ENTORNO (.env)")
    
    env_path = Path('.env')
    
    if env_path.exists():
        print_info("Archivo .env ya existe")
        response = input(f"\n{Colors.YELLOW}¿Quieres sobrescribirlo? [y/N]: {Colors.END}").strip().lower()
        if response not in ['y', 'yes', 's', 'si']:
            print_info("Manteniendo archivo .env existente")
            return True
    
    # Generar clave secreta
    secret_key = generate_secret_key()
    
    env_content = f'''# =============================================================================
# FRAME FORGE - CONFIGURACIÓN DE VARIABLES DE ENTORNO
# =============================================================================
# Este archivo contiene configuraciones sensibles. NO lo compartas ni lo subas
# a GitHub (ya está en .gitignore para protegerlo).
# =============================================================================

# -----------------------------------------------------------------------------
# 1. FLASK SECRET KEY (REQUERIDO)
# -----------------------------------------------------------------------------
# ¿Qué es?: Una clave secreta única que Flask usa para:
#   - Firmar cookies de sesión (seguridad)
#   - Proteger contra ataques CSRF
#   - Cifrar datos sensibles temporalmente
#
# ¿Para qué sirve?: Seguridad de la aplicación. Sin esto, cualquiera podría
# falsificar sesiones y acceder como administrador.
#
# ¿Dónde conseguirlo?: Se genera automáticamente (abajo). Puedes cambiarlo
# manualmente si quieres, pero debe ser:
#   - Mínimo 16 caracteres
#   - Letras, números y símbolos mezclados
#   - COMPLETAMENTE ALEATORIO (no uses palabras comunes)
#
# Ejemplo de generación manual en Python:
#   import secrets; print(secrets.token_hex(32))
# -----------------------------------------------------------------------------
FLASK_SECRET_KEY={secret_key}

# -----------------------------------------------------------------------------
# 2. MODO DE DEBUG (OPCIONAL - Desarrollo vs Producción)
# -----------------------------------------------------------------------------
# ¿Qué es?: Controla si Flask muestra información detallada de errores.
#
# Valores:
#   development = Muestra errores detallados, recarga automática (para programar)
#   production  = Oculta errores, máximo rendimiento (para usuarios finales)
#
# ⚠️  IMPORTANTE: NUNCA uses 'development' en producción público.
#    Los errores detallados pueden revelar información sensible.
# -----------------------------------------------------------------------------
FLASK_ENV=development
FLASK_DEBUG=1

# -----------------------------------------------------------------------------
# 3. DISCORD WEBHOOK URL (OPCIONAL - Notificaciones)
# -----------------------------------------------------------------------------
# ¿Qué es?: Una URL especial que permite enviar mensajes automáticos a un
# canal de Discord cuando ocurren eventos en FrameForge.
#
# ¿Para qué sirve?: Recibir notificaciones en tiempo real sobre:
#   - Videos subidos
#   - Transcripciones completadas
#   - Progreso de las 4 fases de edición
#   - Errores o advertencias
#
# ¿Dónde conseguirlo?:
#   1. Abre Discord (app o web: https://discord.com)
#   2. Ve al servidor donde quieres recibir notificaciones
#   3. Click derecho en el canal → "Configuración del canal" (o "Editar canal")
#   4. Integraciones → Webhooks → "Nuevo webhook"
#   5. Dale nombre (ej: "FrameForge Bot") y copia la URL
#   6. Pega la URL aquí abajo
#
# Ejemplo de URL:
#   https://discord.com/api/webhooks/123456789/abcdefg-hijklmnop
#
# Si no quieres notificaciones, déjalo vacío o coméntalo con #
# -----------------------------------------------------------------------------
DISCORD_WEBHOOK_URL=

# -----------------------------------------------------------------------------
# 4. PUERTO DEL SERVIDOR (OPCIONAL)
# -----------------------------------------------------------------------------
# ¿Qué es?: El número de puerto donde correrá FrameForge.
#
# ¿Para qué sirve?: Si el puerto 5000 está ocupado por otra aplicación,
# puedes cambiarlo aquí.
#
# Valores comunes:
#   5000 = Puerto por defecto de Flask (recomendado)
#   8080 = Alternativa común
#   3000 = Usado por Node.js (puede haber conflictos)
#
# Acceder después:
#   Local:  http://localhost:5000
#   Red:    http://TU_IP:5000 (reemplaza TU_IP con tu IP local)
# -----------------------------------------------------------------------------
PORT=5000

# -----------------------------------------------------------------------------
# 5. LÍMITE DE TAMAÑO DE VIDEO (OPCIONAL)
# -----------------------------------------------------------------------------
# ¿Qué es?: El tamaño máximo de archivo que se puede subir.
#
# ¿Para qué sirve?: Evita que usuarios suban archivos enormes que llenen
# el disco duro.
#
# Formato: En bytes. Ejemplos:
#   536870912   = 512 MB
#   1073741824  = 1 GB
#   2147483648  = 2 GB (por defecto)
#   4294967296  = 4 GB
#
# ⚠️  Asegúrate de tener suficiente espacio en disco.
# -----------------------------------------------------------------------------
MAX_CONTENT_LENGTH=2147483648

# =============================================================================
# FIN DE LA CONFIGURACIÓN
# =============================================================================
# Guarda este archivo y reinicia FrameForge para aplicar los cambios:
#   python app.py
#
# Para más ayuda: README.md o https://github.com/litelis/FrameForge
# =============================================================================
'''
    
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print_success("Archivo .env creado exitosamente")
        print_info(f"Ubicación: {env_path.absolute()}")
        print_info("Este archivo contiene configuraciones sensibles - NO lo compartas")
        
        # Mostrar resumen de variables
        print_config("\nVariables configuradas:")
        print(f"  • FLASK_SECRET_KEY: {'*' * 20} (generada automáticamente)")
        print(f"  • FLASK_ENV: development (modo desarrollo)")
        print(f"  • DISCORD_WEBHOOK_URL: (vacío - configurar manualmente si se desea)")
        print(f"  • PORT: 5000")
        print(f"  • MAX_CONTENT_LENGTH: 2GB")
        
        print(f"\n{Colors.YELLOW}⚠️  IMPORTANTE:{Colors.END}")
        print("  El archivo .env está protegido por .gitignore")
        print("  NUNCA lo subas a GitHub ni lo compartas públicamente")
        
        return True
        
    except Exception as e:
        print_error(f"No se pudo crear .env: {e}")
        return False

def explain_env_variables():
    """Muestra explicación detallada de cada variable"""
    print_header("GUÍA DE VARIABLES DE ENTORNO")
    
    print(f"{Colors.CYAN}{Colors.BOLD}1. FLASK_SECRET_KEY{Colors.END}")
    print("   Propósito: Seguridad de sesiones y cookies")
    print("   Importancia: ⭐⭐⭐⭐⭐ CRÍTICA")
    print("   Generación: Automática (32 caracteres aleatorios)")
    print("   Cambiar: Solo si sospechas que fue comprometida\n")
    
    print(f"{Colors.CYAN}{Colors.BOLD}2. FLASK_ENV / FLASK_DEBUG{Colors.END}")
    print("   Propósito: Modo de operación")
    print("   Valores: development (programar) / production (usuarios)")
    print("   Importancia: ⭐⭐⭐⭐ Alta")
    print("   Cambiar: A 'production' antes de mostrar a terceros\n")
    
    print(f"{Colors.CYAN}{Colors.BOLD}3. DISCORD_WEBHOOK_URL{Colors.END}")
    print("   Propósito: Notificaciones automáticas a Discord")
    print("   Opcional: Sí - el sistema funciona sin esto")
    print("   Importancia: ⭐⭐⭐ Media")
    print("   Obtener: Discord → Canal → Integraciones → Webhooks\n")
    
    print(f"{Colors.CYAN}{Colors.BOLD}4. PORT{Colors.END}")
    print("   Propósito: Puerto de red para el servidor")
    print("   Default: 5000")
    print("   Importancia: ⭐⭐ Baja")
    print("   Cambiar: Solo si hay conflicto con otro programa\n")
    
    print(f"{Colors.CYAN}{Colors.BOLD}5. MAX_CONTENT_LENGTH{Colors.END}")
    print("   Propósito: Límite de tamaño de videos")
    print("   Default: 2GB")
    print("   Importancia: ⭐⭐⭐ Media")
    print("   Cambiar: Según espacio disponible en disco\n")

def check_git():
    """Verifica si git está instalado"""
    print_info("\nVerificando Git...")
    try:
        subprocess.check_call(['git', '--version'], 
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
        print_success("Git instalado ✅")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_warning("Git no encontrado")
        print_info("Descarga Git desde: https://git-scm.com/downloads")
        return False

def init_git_repo():
    """Inicializa el repositorio git"""
    print_header("CONFIGURACIÓN GIT")
    
    if not check_git():
        return False
    
    git_dir = Path('.git')
    if git_dir.exists():
        print_info("Repositorio Git ya inicializado")
        return True
    
    try:
        subprocess.check_call(['git', 'init'], 
                            stdout=subprocess.DEVNULL)
        print_success("Repositorio Git inicializado")
        
        # Configurar remote
        remote_url = 'https://github.com/litelis/FrameForge.git'
        try:
            subprocess.check_call(['git', 'remote', 'add', 'origin', remote_url],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
            print_success(f"Remote 'origin' configurado: {remote_url}")
        except subprocess.CalledProcessError:
            print_warning("Remote ya existe o error al configurar")
        
        return True
    except subprocess.CalledProcessError:
        print_error("No se pudo inicializar Git")
        return False

def print_final_instructions():
    """Muestra instrucciones finales"""
    print_header("SETUP COMPLETADO")
    
    print(f"{Colors.GREEN}{Colors.BOLD}🎬 FrameForge está listo para usar!{Colors.END}\n")
    
    print("Para iniciar el servidor:")
    print(f"  {Colors.YELLOW}python app.py{Colors.END}\n")
    
    print("Para ejecutar pruebas:")
    print(f"  {Colors.YELLOW}python test_api.py{Colors.END}\n")
    
    print("Para verificar actualizaciones:")
    print(f"  {Colors.YELLOW}python update.py{Colors.END}\n")
    
    print("Para hacer commit inicial:")
    print(f"  {Colors.YELLOW}git add .{Colors.END}")
    print(f"  {Colors.YELLOW}git commit -m \"Initial commit: FrameForge AI Video Editor\"{Colors.END}")
    print(f"  {Colors.YELLOW}git push -u origin master{Colors.END}\n")
    
    print(f"{Colors.CYAN}Configuración:{Colors.END}")
    print(f"  • Archivo .env creado con explicaciones")
    print(f"  • Clave secreta generada automáticamente")
    print(f"  • Webhook de Discord opcional (configurar en .env)\n")
    
    print(f"{Colors.BLUE}Repositorio:{Colors.END} https://github.com/litelis/FrameForge.git")
    print(f"{Colors.BLUE}Documentación:{Colors.END} README.md")
    print(f"{Colors.BLUE}Reporte de pruebas:{Colors.END} TEST_REPORT.md\n")

def main():
    """Función principal de setup"""
    print_header("FRAMEFORGE - AI CINEMATIC VIDEO EDITOR")
    print("Verificando e instalando dependencias...\n")
    
    # Verificar Python
    if not check_python_version():
        sys.exit(1)
    
    # Verificar e instalar dependencias
    if not check_and_install_packages():
        print_error("\nNo se pudieron instalar todas las dependencias requeridas")
        print_info("Por favor, instala manualmente:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    # Crear directorios
    create_directories()
    
    # Crear archivo .env con explicaciones
    create_env_file()
    
    # Mostrar guía de variables
    explain_env_variables()
    
    # Inicializar Git
    init_git_repo()
    
    # Instrucciones finales
    print_final_instructions()

if __name__ == '__main__':
    main()
