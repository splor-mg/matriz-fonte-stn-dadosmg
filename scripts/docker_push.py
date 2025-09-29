#!/usr/bin/env python3
"""
Script para enviar imagem Docker para o Docker Hub
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def load_config():
    """Carrega variáveis do config.mk"""
    config = {}
    config_file = Path("config.mk")
    
    if not config_file.exists():
        print("❌ Arquivo config.mk não encontrado")
        print("💡 Execute 'poetry run config' primeiro")
        sys.exit(1)
    
    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    return config

def check_docker_login():
    """Verifica se está logado no Docker Hub"""
    try:
        result = subprocess.run(
            ["docker", "system", "info", "--format", "{{.RegistryConfig.IndexConfigs}}"],
            capture_output=True, text=True, check=True
        )
        return "docker.io" in result.stdout
    except subprocess.CalledProcessError:
        return False

def login_docker_hub():
    """Faz login no Docker Hub"""
    print("🔐 Fazendo login no Docker Hub...")
    try:
        subprocess.run(["docker", "login"], check=True)
        print("✅ Login realizado com sucesso!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Falha no login do Docker Hub")
        return False

def push_docker_image(config, verbose=False):
    """Envia a imagem Docker para o Docker Hub"""
    image_name = f"{config['DOCKER_USER']}/{config['DOCKER_IMAGE']}:{config['DOCKER_TAG']}"
    
    print(f"📤 Enviando imagem para o Docker Hub...")
    print(f"📦 Imagem: {image_name}")
    print()
    
    cmd = ["docker", "push", image_name]
    
    if verbose:
        print("🔍 Comando executado:")
        print(" ".join(cmd))
        print()
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ Imagem enviada com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao enviar imagem: {e}")
        return False

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Envia imagem Docker para o Docker Hub")
    parser.add_argument("--verbose", "-v", action="store_true", help="Modo verboso")
    args = parser.parse_args()
    
    try:
        # Carrega configurações
        config = load_config()
        
        # Verifica se está logado
        if not check_docker_login():
            if not login_docker_hub():
                sys.exit(1)
        
        # Envia imagem
        success = push_docker_image(config, args.verbose)
        
        if success:
            print(f"\n🎉 Push concluído com sucesso!")
            print(f"📦 Imagem: {config['DOCKER_USER']}/{config['DOCKER_IMAGE']}:{config['DOCKER_TAG']}")
            print(f"🔗 Docker Hub: https://hub.docker.com/r/{config['DOCKER_USER']}/{config['DOCKER_IMAGE']}")
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Operação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
