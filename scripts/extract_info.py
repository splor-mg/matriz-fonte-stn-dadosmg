#!/usr/bin/env python3
"""
Script para extrair informações de versões dos pacotes R da imagem Docker
e atualizar o config.mk automaticamente
"""

import os
import sys
import subprocess
import re
from pathlib import Path

class Colors:
    """Cores para output do terminal"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def load_config():
    """Carrega variáveis do config.mk"""
    config = {}
    config_file = Path("config.mk")
    
    if not config_file.exists():
        print(f"{Colors.RED}❌ Arquivo config.mk não encontrado{Colors.END}")
        sys.exit(1)
    
    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    return config

def extract_package_versions_from_image(image_name):
    """Extrai versões dos pacotes R da imagem Docker"""
    print(f"🔍 Extraindo versões da imagem: {image_name}")
    
    # Comando para extrair informações dos pacotes R
    cmd = [
        "docker", "run", "--rm", image_name,
        "Rscript", "-e",
        """
        packages <- c('relatorios', 'execucao', 'reest')
        versions <- sapply(packages, function(pkg) {
            if (requireNamespace(pkg, quietly = TRUE)) {
                as.character(packageVersion(pkg))
            } else {
                'NOT_INSTALLED'
            }
        })
        cat(paste(names(versions), versions, sep='=', collapse='\\n'))
        """
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        versions = {}
        
        for line in result.stdout.strip().split('\n'):
            if '=' in line:
                pkg, version = line.split('=', 1)
                if version != 'NOT_INSTALLED':
                    versions[pkg] = version
                else:
                    print(f"{Colors.YELLOW}⚠️  Pacote {pkg} não encontrado na imagem{Colors.END}")
        
        return versions
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}❌ Erro ao extrair versões: {e}{Colors.END}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return {}

def update_config_mk(config, new_versions):
    """Atualiza o config.mk com as novas versões"""
    config_file = Path("config.mk")
    
    with open(config_file, 'r') as f:
        lines = f.readlines()
    
    # Mapear pacotes para variáveis do config
    package_mapping = {
        'relatorios': 'RELATORIOS_VERSION',
        'execucao': 'EXECUCAO_VERSION', 
        'reest': 'REEST_VERSION'
    }
    
    changes_made = False
    
    for pkg, version in new_versions.items():
        if pkg in package_mapping:
            var_name = package_mapping[pkg]
            version_with_v = f"v{version}" if not version.startswith('v') else version
            
            # Procurar e atualizar a linha
            for i, line in enumerate(lines):
                if line.startswith(f"{var_name}="):
                    old_value = line.split('=', 1)[1].strip()
                    if old_value != version_with_v:
                        lines[i] = f"{var_name}={version_with_v}\n"
                        print(f"📝 {var_name}: {old_value} → {version_with_v}")
                        changes_made = True
                    break
    
    if changes_made:
        # Salvar arquivo atualizado
        with open(config_file, 'w') as f:
            f.writelines(lines)
        print(f"{Colors.GREEN}✅ config.mk atualizado com sucesso!{Colors.END}")
        return True
    else:
        print(f"{Colors.BLUE}ℹ️  Nenhuma atualização necessária{Colors.END}")
        return False

def main():
    """Função principal"""
    print(f"{Colors.BLUE}{Colors.BOLD}")
    print("=" * 60)
    print("📦 EXTRAÇÃO DE INFORMAÇÕES DA IMAGEM DOCKER")
    print("   MATRIZ-FONTE-STN-DADOSMG")
    print("=" * 60)
    print(f"{Colors.END}")
    
    try:
        # Carrega configurações
        config = load_config()
        
        # Monta nome da imagem
        image_name = f"{config['DOCKER_IMAGE']}:{config['DOCKER_TAG']}"
        
        # Verifica se a imagem existe localmente
        try:
            subprocess.run(["docker", "inspect", image_name], 
                         capture_output=True, check=True)
        except subprocess.CalledProcessError:
            print(f"{Colors.RED}❌ Imagem {image_name} não encontrada localmente{Colors.END}")
            print(f"{Colors.BLUE}💡 Execute 'make docker-build' primeiro{Colors.END}")
            sys.exit(1)
        
        # Extrai versões dos pacotes
        versions = extract_package_versions_from_image(image_name)
        
        if not versions:
            print(f"{Colors.RED}❌ Não foi possível extrair versões dos pacotes{Colors.END}")
            sys.exit(1)
        
        print(f"\n📋 Versões encontradas:")
        for pkg, version in versions.items():
            print(f"   {pkg}: {version}")
        
        # Atualiza config.mk
        print(f"\n🔧 Atualizando config.mk...")
        updated = update_config_mk(config, versions)
        
        if updated:
            print(f"\n{Colors.GREEN}🎉 Processo concluído com sucesso!{Colors.END}")
        else:
            print(f"\n{Colors.BLUE}ℹ️  Configurações já estão atualizadas{Colors.END}")
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Operação cancelada pelo usuário{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}❌ Erro inesperado: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()
