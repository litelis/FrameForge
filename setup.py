#!/usr/bin/env python3
"""
FrameForge - AI Cinematic Video Editor
Setup Script - Verifica e instala dependencias automáticamente
"""

import sys
import subprocess
import importlib
from pathlib import Path

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
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
    'python_dotenv': 'python-dotenv>=1.0.0',
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

def check_package(package_name, install_name):
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
    
    print("Para hacer commit inicial:")
    print(f"  {Colors.YELLOW}git add .{Colors.END}")
    print(f"  {Colors.YELLOW}git commit -m \"Initial commit: FrameForge AI Video Editor\"{Colors.END}")
    print(f"  {Colors.YELLOW}git push -u origin main{Colors.END}\n")
    
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
    
    # Inicializar Git
    init_git_repo()
    
    # Instrucciones finales
    print_final_instructions()

if __name__ == '__main__':
    main()
