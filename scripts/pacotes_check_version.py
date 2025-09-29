#!/usr/bin/env python3
"""
Script para verificar e atualizar versões dos pacotes DCAF no config.mk
Compara versões atuais com as mais recentes no GitHub
"""

import os
import sys
import re
import requests
from pathlib import Path
from datetime import datetime

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

def load_env_file():
    """Carrega variáveis do arquivo .env, se existir (sem depender de python-dotenv)."""
    env_path = Path('.env')
    if not env_path.exists():
        return
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    continue
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                # Não sobrescrever se já existir
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception:
        # Silencioso por segurança; uso opcional
        pass

def get_latest_release(repo_name):
    """Obtém a versão mais recente de um repositório GitHub"""
    # URLs para releases e tags
    releases_url = f"https://api.github.com/repos/splor-mg/{repo_name}/releases/latest"
    tags_url = f"https://api.github.com/repos/splor-mg/{repo_name}/tags"
    
    # Headers com token se disponível
    headers = {"User-Agent": "matriz-fonte-stn-dadosmg-version-check/1.0"}
    github_token = os.getenv('GITHUB_TOKEN') or os.getenv('GH_PAT')
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    
    try:
        # Tentar releases primeiro
        response = requests.get(releases_url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            tag_name = data.get('tag_name', '')
        else:
            # Se não houver releases, buscar tags
            if response.status_code in (401, 403):
                try:
                    msg = response.json().get('message', '')
                except Exception:
                    msg = ''
                print(f"{Colors.YELLOW}⚠️  Releases de {repo_name} inacessíveis (status {response.status_code}). {msg}{Colors.END}")
            response = requests.get(tags_url, headers=headers, timeout=15)
            if response.status_code == 200:
                tags = response.json()
                if tags:
                    # Pegar a primeira tag (mais recente)
                    tag_name = tags[0].get('name', '')
                else:
                    return None
            else:
                try:
                    msg = response.json().get('message', '')
                except Exception:
                    msg = ''
                print(f"{Colors.YELLOW}⚠️  Repositório {repo_name} não encontrado/privado (status {response.status_code}). {msg}{Colors.END}")
                return None
        
        # Garantir que a versão comece com 'v'
        if tag_name and not tag_name.startswith('v'):
            tag_name = f"v{tag_name}"
        
        return tag_name
    except requests.exceptions.RequestException as e:
        print(f"{Colors.YELLOW}⚠️  Erro ao consultar {repo_name}: {e}{Colors.END}")
        return None
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Erro inesperado ao consultar {repo_name}: {e}{Colors.END}")
        return None

def update_config_mk(config, updates):
    """Atualiza o config.mk com as novas versões"""
    config_file = Path("config.mk")
    
    with open(config_file, 'r') as f:
        lines = f.readlines()
    
    changes_made = False
    
    for package, new_version in updates.items():
        var_name = f"{package.upper()}_VERSION"
        
        # Procurar e atualizar a linha
        for i, line in enumerate(lines):
            if line.startswith(f"{var_name}="):
                old_value = line.split('=', 1)[1].strip()
                if old_value != new_version:
                    lines[i] = f"{var_name}={new_version}\n"
                    print(f"📝 {var_name}: {old_value} → {new_version}")
                    changes_made = True
                break
    
    if changes_made:
        # Adicionar comentário de atualização
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for i, line in enumerate(lines):
            if line.startswith("# Última atualização:"):
                lines[i] = f"# Última atualização: {timestamp} (auto-update)\n"
                break
        
        # Salvar arquivo atualizado
        with open(config_file, 'w') as f:
            f.writelines(lines)
        
        print(f"{Colors.GREEN}✅ config.mk atualizado com sucesso!{Colors.END}")
        return True
    else:
        print(f"{Colors.BLUE}ℹ️  Nenhuma atualização necessária{Colors.END}")
        return False

def check_package_versions():
    """Verifica e atualiza versões dos pacotes DCAF"""
    print(f"{Colors.BLUE}{Colors.BOLD}")
    print("=" * 60)
    print("📦 VERIFICAÇÃO DE VERSÕES DOS PACOTES DCAF")
    print("   MATRIZ-FONTE-STN-DADOSMG")
    print("=" * 60)
    print(f"{Colors.END}")
    
    # Verificar se há token do GitHub
    github_token = os.getenv('GITHUB_TOKEN')
    if github_token:
        print(f"🔑 Usando token do GitHub para acessar repositórios privados")
    else:
        print(f"⚠️  GITHUB_TOKEN não encontrado - repositórios privados podem não ser acessíveis")
    print()
    
    # Mapeamento de pacotes
    packages = {
        'relatorios': 'RELATORIOS_VERSION',
        'execucao': 'EXECUCAO_VERSION', 
        'reest': 'REEST_VERSION'
    }
    
    try:
        # Carrega configurações atuais
        config = load_config()
        
        print(f"🔍 Verificando versões no GitHub...")
        print()
        
        updates = {}
        errors = []
        
        # Verificar cada pacote
        for package, var_name in packages.items():
            current_version = config.get(var_name, 'NÃO_DEFINIDO')
            print(f"📦 {package}:")
            print(f"   Atual: {current_version}")
            
            # Obter versão mais recente
            latest_version = get_latest_release(package)
            
            if latest_version:
                print(f"   GitHub: {latest_version}")
                
                if current_version != latest_version:
                    updates[package] = latest_version
                    print(f"   {Colors.YELLOW}🔄 Atualização disponível!{Colors.END}")
                else:
                    print(f"   {Colors.GREEN}✅ Já está atualizado{Colors.END}")
            else:
                print(f"   {Colors.RED}❌ Não foi possível obter versão{Colors.END}")
                errors.append(package)
            
            print()
        
        # Mostrar resumo de erros
        if errors:
            print(f"{Colors.YELLOW}⚠️  Não foi possível verificar: {', '.join(errors)}{Colors.END}")
            if not github_token:
                print(f"{Colors.BLUE}💡 Dica: Configure GITHUB_TOKEN para acessar repositórios privados{Colors.END}")
            print()
        
        # Atualizar config.mk se necessário
        if updates:
            print(f"🔧 Atualizando config.mk...")
            updated = update_config_mk(config, updates)
            
            if updated:
                print(f"\n{Colors.GREEN}🎉 Atualizações aplicadas com sucesso!{Colors.END}")
                print(f"📋 Pacotes atualizados: {', '.join(updates.keys())}")
                return True
            else:
                print(f"\n{Colors.RED}❌ Erro ao atualizar config.mk{Colors.END}")
                return False
        else:
            if errors and not updates:
                print(f"{Colors.YELLOW}ℹ️  Nenhuma atualização possível devido a erros de acesso{Colors.END}")
                return False
            else:
                print(f"{Colors.BLUE}ℹ️  Todos os pacotes verificados já estão atualizados{Colors.END}")
                return False
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Operação cancelada pelo usuário{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}❌ Erro inesperado: {e}{Colors.END}")
        sys.exit(1)

def main():
    """Função principal"""
    try:
        # Carrega .env se existir
        load_env_file()
        # Verificar se requests está disponível
        try:
            import requests
        except ImportError:
            print(f"{Colors.RED}❌ Biblioteca 'requests' não encontrada{Colors.END}")
            print(f"{Colors.BLUE}💡 Execute: pip install requests{Colors.END}")
            sys.exit(1)
        
        # Executar verificação
        has_updates = check_package_versions()
        
        # Retornar código de saída apropriado
        if has_updates:
            print(f"\n{Colors.GREEN}✅ Script concluído com atualizações{Colors.END}")
            sys.exit(0)  # Sucesso com mudanças
        else:
            print(f"\n{Colors.BLUE}ℹ️  Script concluído sem mudanças{Colors.END}")
            sys.exit(1)  # Sucesso sem mudanças (para o workflow)
            
    except Exception as e:
        print(f"{Colors.RED}❌ Erro fatal: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()
