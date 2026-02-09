#!/usr/bin/env python3
"""
FrameForge - AI Cinematic Video Editor
Update Script - Verifica y aplica actualizaciones desde GitHub
"""

import subprocess
import sys
import requests
import os
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

def get_local_commit():
    """Obtiene el hash del commit local actual"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None
    except FileNotFoundError:
        print_error("Git no está instalado")
        return None

def get_remote_commit():
    """Obtiene el hash del último commit en GitHub"""
    try:
        # Usar GitHub API para obtener el último commit
        url = "https://api.github.com/repos/litelis/FrameForge/commits/master"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data['sha']
        elif response.status_code == 404:
            # Intentar con 'main' en lugar de 'master'
            url = "https://api.github.com/repos/litelis/FrameForge/commits/main"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data['sha']
            else:
                print_error(f"No se pudo acceder al repositorio (Status: {response.status_code})")
                return None
        else:
            print_error(f"Error al consultar GitHub API: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print_error(f"Error de conexión: {e}")
        print_info("Verifica tu conexión a internet")
        return None
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        return None

def get_commit_info(commit_hash):
    """Obtiene información del commit (mensaje, fecha, autor)"""
    try:
        # Primero intentar obtener localmente
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%h|%s|%ci|%an', commit_hash],
            capture_output=True,
            text=True,
            check=True
        )
        parts = result.stdout.strip().split('|')
        if len(parts) >= 4:
            return {
                'short_hash': parts[0],
                'message': parts[1],
                'date': parts[2],
                'author': parts[3]
            }
    except:
        pass
    
    # Si falla localmente, intentar con GitHub API
    try:
        url = f"https://api.github.com/repos/litelis/FrameForge/commits/{commit_hash}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                'short_hash': data['sha'][:7],
                'message': data['commit']['message'].split('\n')[0],
                'date': data['commit']['committer']['date'],
                'author': data['commit']['author']['name']
            }
    except:
        pass
    
    return None

def check_for_updates():
    """Verifica si hay actualizaciones disponibles"""
    print_header("VERIFICANDO ACTUALIZACIONES")
    
    print_info("Consultando versión local...")
    local_commit = get_local_commit()
    
    if not local_commit:
        print_error("No se pudo determinar la versión local")
        print_info("¿Estás en un repositorio Git?")
        return False, None, None
    
    print_success(f"Versión local: {local_commit[:7]}")
    
    print_info("\nConsultando versión en GitHub...")
    remote_commit = get_remote_commit()
    
    if not remote_commit:
        print_error("No se pudo consultar la versión remota")
        return False, None, None
    
    print_success(f"Versión remota: {remote_commit[:7]}")
    
    # Comparar commits
    if local_commit == remote_commit:
        print_success("\n✨ Tienes la última versión instalada")
        print_info("No hay actualizaciones disponibles")
        return False, local_commit, remote_commit
    else:
        print_warning("\n📦 Hay una nueva actualización disponible")
        
        # Obtener info del commit remoto
        commit_info = get_commit_info(remote_commit)
        if commit_info:
            print(f"\n{Colors.BOLD}Últimos cambios:{Colors.END}")
            print(f"  Commit: {commit_info['short_hash']}")
            print(f"  Mensaje: {commit_info['message']}")
            print(f"  Fecha: {commit_info['date']}")
            print(f"  Autor: {commit_info['author']}")
        
        return True, local_commit, remote_commit

def ask_for_update():
    """Pregunta al usuario si quiere actualizar"""
    print(f"\n{Colors.YELLOW}{Colors.BOLD}¿Deseas actualizar a la última versión?{Colors.END}")
    
    while True:
        try:
            response = input(f"{Colors.BOLD}[Y/n]: {Colors.END}").strip().lower()
            
            if response in ['y', 'yes', 's', 'si', '']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print_warning("Por favor responde 'y' (sí) o 'n' (no)")
        except KeyboardInterrupt:
            print("\n")
            return False
        except EOFError:
            return False

def perform_update():
    """Realiza la actualización con git pull"""
    print_header("ACTUALIZANDO FRAME FORGE")
    
    print_info("Descargando última versión...")
    
    try:
        # Verificar si hay cambios locales sin commit
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout.strip():
            print_warning("Tienes cambios locales sin guardar")
            print_info("Se intentará hacer stash de los cambios...")
            
            # Hacer stash de cambios locales
            stash_result = subprocess.run(
                ['git', 'stash'],
                capture_output=True,
                text=True
            )
            
            if stash_result.returncode != 0:
                print_error("No se pudieron guardar los cambios locales")
                print_info("Por favor, commitea o descarta tus cambios manualmente:")
                print("  git add .")
                print("  git commit -m 'mis cambios'")
                return False
        
        # Realizar pull
        print_info("Ejecutando git pull...")
        pull_result = subprocess.run(
            ['git', 'pull', 'origin', 'master'],
            capture_output=True,
            text=True
        )
        
        # Si master falla, intentar con main
        if pull_result.returncode != 0 and "master" in pull_result.stderr:
            print_info("Intentando con branch 'main'...")
            pull_result = subprocess.run(
                ['git', 'pull', 'origin', 'main'],
                capture_output=True,
                text=True
            )
        
        if pull_result.returncode == 0:
            print_success("Código actualizado exitosamente")
            
            # Verificar si hay nuevas dependencias
            print_info("\nVerificando dependencias...")
            check_dependencies()
            
            # Restaurar cambios locales si se hizo stash
            subprocess.run(
                ['git', 'stash', 'pop'],
                capture_output=True,
                text=True
            )
            
            print_success("\n🎉 Actualización completada")
            print_info("Reinicia el servidor para aplicar los cambios:")
            print(f"  {Colors.YELLOW}python app.py{Colors.END}")
            
            return True
        else:
            print_error(f"Error al actualizar: {pull_result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print_error(f"Error de Git: {e}")
        return False
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        return False

def check_dependencies():
    """Verifica si hay nuevas dependencias en requirements.txt"""
    try:
        if not Path('requirements.txt').exists():
            print_warning("No se encontró requirements.txt")
            return
        
        print_info("Verificando nuevas dependencias...")
        
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt', '--quiet'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success("Dependencias actualizadas")
        else:
            print_warning("Algunas dependencias no se pudieron actualizar")
            print_info("Intenta manualmente: pip install -r requirements.txt")
            
    except Exception as e:
        print_warning(f"No se pudieron verificar dependencias: {e}")

def show_version_info(local_commit, remote_commit):
    """Muestra información de versiones"""
    print(f"\n{Colors.BOLD}Información de versiones:{Colors.END}")
    print(f"  Local:  {local_commit[:7] if local_commit else 'N/A'}")
    print(f"  Remota: {remote_commit[:7] if remote_commit else 'N/A'}")
    print(f"\nRepositorio: {Colors.BLUE}https://github.com/litelis/FrameForge{Colors.END}")

def main():
    """Función principal"""
    print_header("FRAME FORGE - ACTUALIZADOR")
    
    # Verificar que estamos en un repo git
    if not Path('.git').exists():
        print_error("No se encontró repositorio Git")
        print_info("Este script debe ejecutarse desde el directorio del proyecto")
        print_info("Clona el repositorio primero:")
        print(f"  {Colors.YELLOW}git clone https://github.com/litelis/FrameForge.git{Colors.END}")
        sys.exit(1)
    
    # Verificar actualizaciones
    has_update, local_commit, remote_commit = check_for_updates()
    
    if not has_update:
        show_version_info(local_commit, remote_commit)
        print_info("\nTu instalación está al día ✨")
        sys.exit(0)
    
    # Preguntar si quiere actualizar
    if ask_for_update():
        success = perform_update()
        sys.exit(0 if success else 1)
    else:
        print_info("\nActualización cancelada")
        print_info("Puedes actualizar más tarde ejecutando:")
        print(f"  {Colors.YELLOW}python update.py{Colors.END}")
        sys.exit(0)

if __name__ == '__main__':
    main()
