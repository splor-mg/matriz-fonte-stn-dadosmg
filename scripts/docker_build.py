#!/usr/bin/env python3
"""
Script para construir imagem Docker conforme parâmetros do config.mk
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

def validate_environment():
    """Valida se o ambiente está configurado corretamente"""
    errors = []
    
    # Verificar se .env existe
    if not Path(".env").exists():
        errors.append("Arquivo .env não encontrado")
    
    # Verificar se Docker está rodando
    try:
        subprocess.run(["docker", "version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        errors.append("Docker não está rodando ou não está instalado")
    
    if errors:
        print("❌ Problemas encontrados:")
        for error in errors:
            print(f"   • {error}")
        print("\n💡 Resolva os problemas acima e tente novamente")
        sys.exit(1)

def build_docker_image(config, verbose=False):
    """Constrói a imagem Docker"""
    print("🔨 Iniciando build da imagem Docker...")
    full_image = f"{config['DOCKER_USER']}/{config['DOCKER_IMAGE']}:{config['DOCKER_TAG']}"
    print(f"📦 Imagem: {full_image}")
    print(f"👤 Usuário: {config['DOCKER_USER']}")
    print(f"📅 Ano Matriz: {config['ANO_MATRIZ']}")
    print()

    # Detectar branch e SHA curtos para espelhar tags do CI
    try:
        branch = subprocess.check_output([
            'git', 'rev-parse', '--abbrev-ref', 'HEAD'
        ]).decode().strip()
    except Exception:
        branch = 'local'

    try:
        short_sha = subprocess.check_output([
            'git', 'rev-parse', '--short', 'HEAD'
        ]).decode().strip()
    except Exception:
        short_sha = 'unknown'

    # Montar lista de tags: tag configurada, branch-sha e latest (se branch padrão)
    image_base = f"{config['DOCKER_USER']}/{config['DOCKER_IMAGE']}"
    tags = [
        f"{image_base}:{config['DOCKER_TAG']}",                 # ex: matriz-stn2025
        f"{image_base}:{branch}-{short_sha}",                   # ex: main-a1b2c3d
    ]
    default_branch = 'main'
    if branch == default_branch:
        tags.append(f"{image_base}:latest")

    # Comando docker buildx build com múltiplas tags
    cmd = [
        "docker", "buildx", "build",
        "--secret", "id=secret,src=.env",
        "--build-arg", f"relatorios_version={config['RELATORIOS_VERSION']}",
        "--build-arg", f"execucao_version={config['EXECUCAO_VERSION']}",
        "--build-arg", f"reest_version={config['REEST_VERSION']}",
        "--build-arg", f"ano_matriz={config['ANO_MATRIZ']}",
        "--build-arg", f"docker_tag={config['DOCKER_TAG']}",
        "--build-arg", f"docker_user={config['DOCKER_USER']}",
        "--build-arg", f"docker_image={config['DOCKER_IMAGE']}",
        "."
    ]

    # Inserir flags --tag para cada tag calculada (antes do contexto ".")
    # Mantemos a ordem: configurada, branch-sha, (latest se default)
    # cmd atualmente termina com "."; vamos reconstruí-lo para inserir tags antes do contexto
    context_path = cmd.pop()  # remove "."
    # Adiciona as múltiplas tags
    tag_flags = []
    for t in tags:
        tag_flags.extend(["--tag", t])
    cmd[3:3] = tag_flags  # insere após "docker buildx build"
    # Reinsere o contexto ao final
    cmd.append(context_path)

    if verbose:
        print("🔍 Comando executado:")
        print(" ".join(cmd))
        print()
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ Imagem Docker construída com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao construir imagem Docker: {e}")
        return False

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Constrói imagem Docker para matriz-fonte-stn-dadosmg")
    parser.add_argument("--verbose", "-v", action="store_true", help="Modo verboso")
    args = parser.parse_args()
    
    try:
        # Valida ambiente
        validate_environment()
        
        # Carrega configurações
        config = load_config()
        
        # Constrói imagem
        success = build_docker_image(config, args.verbose)
        
        if success:
            full_image = f"{config['DOCKER_USER']}/{config['DOCKER_IMAGE']}:{config['DOCKER_TAG']}"
            print(f"\n🎉 Build concluído com sucesso!")
            print(f"📦 Imagem: {full_image}")
            print(f"\n💡 Para executar a imagem:")
            print(f"   docker run -it --rm -v $(pwd):/project {full_image}")
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
