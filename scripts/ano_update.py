#!/usr/bin/env python3
"""
Script para atualização automática de anos nos arquivos do projeto
Atualiza ANO_MATRIZ no config.mk e anos hardcoded nos scripts R e data.toml
"""

import os
import sys
import re
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

def get_current_year():
    """Obtém o ano corrente"""
    return datetime.now().year

def update_config_mk(current_year):
    """Atualiza ANO_MATRIZ no config.mk se necessário"""
    config_file = Path("config.mk")
    
    with open(config_file, 'r') as f:
        lines = f.readlines()
    
    changes_made = False
    
    for i, line in enumerate(lines):
        if line.startswith("ANO_MATRIZ="):
            current_value = line.split('=', 1)[1].strip()
            if current_value != str(current_year):
                lines[i] = f"ANO_MATRIZ={current_year}\n"
                print(f"📝 ANO_MATRIZ: {current_value} → {current_year}")
                changes_made = True
            break
    
    if changes_made:
        with open(config_file, 'w') as f:
            f.writelines(lines)
        print(f"{Colors.GREEN}✅ config.mk atualizado{Colors.END}")
        return True
    else:
        print(f"{Colors.BLUE}ℹ️  ANO_MATRIZ já está atualizado ({current_year}){Colors.END}")
        return False

def update_script_file(file_path, current_year):
    """Atualiza anos hardcoded em um arquivo (R ou TOML)"""
    if not file_path.exists():
        print(f"{Colors.YELLOW}⚠️  Arquivo {file_path} não encontrado{Colors.END}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    changes_made = False
    
    # Calcular anos
    year_previous = current_year - 1
    year_current = current_year
    
    if file_path.suffix == '.R':
        # Para arquivos R: alterar apenas anos nos caminhos de arquivos
        # Padrões específicos para caminhos de arquivos
        patterns = [
            (rf'datapackages/armazem-siafi-(\d{{4}})', f'datapackages/armazem-siafi-{year_previous}'),
            (rf'datapackages/armazem-siafi-(\d{{4}})', f'datapackages/armazem-siafi-{year_current}')
        ]
        
        # Encontrar anos nos caminhos
        path_years = re.findall(r'datapackages/armazem-siafi-(\d{4})', content)
        if not path_years:
            print(f"{Colors.BLUE}ℹ️  {file_path.name}: nenhum ano encontrado nos caminhos{Colors.END}")
            return False
        
        years_int = [int(year) for year in path_years]
        min_year = min(years_int)
        max_year = max(years_int)
        
        print(f"🔍 {file_path.name}: anos nos caminhos {min_year}, {max_year}")
        
        # Aplicar regra: maior ano → ano corrente, menor ano → ano anterior
        if max_year != year_current or min_year != year_previous:
            # Substituir anos nos caminhos apenas
            content = re.sub(rf'datapackages/armazem-siafi-{max_year}', f'datapackages/armazem-siafi-{year_current}', content)
            content = re.sub(rf'datapackages/armazem-siafi-{min_year}', f'datapackages/armazem-siafi-{year_previous}', content)
            changes_made = True
            
            print(f"📝 {file_path.name}: caminhos {min_year} → {year_previous}, {max_year} → {year_current}")
        else:
            print(f"{Colors.BLUE}ℹ️  {file_path.name}: caminhos já estão corretos{Colors.END}")
            return False
            
    else:
        # Para arquivos TOML: alterar todos os anos encontrados
        year_pattern = r'\b(20\d{2})\b'
        years_found = re.findall(year_pattern, content)
        
        if not years_found:
            print(f"{Colors.BLUE}ℹ️  {file_path.name}: nenhum ano encontrado{Colors.END}")
            return False
        
        years_int = [int(year) for year in years_found]
        min_year = min(years_int)
        max_year = max(years_int)
        
        print(f"🔍 {file_path.name}: anos encontrados {min_year}, {max_year}")
        
        if max_year != year_current or min_year != year_previous:
            content = re.sub(rf'\b{max_year}\b', str(year_current), content)
            content = re.sub(rf'\b{min_year}\b', str(year_previous), content)
            changes_made = True
            
            print(f"📝 {file_path.name}: {min_year} → {year_previous}, {max_year} → {year_current}")
        else:
            print(f"{Colors.BLUE}ℹ️  {file_path.name}: anos já estão corretos{Colors.END}")
            return False
    
    if changes_made:
        # Salvar arquivo atualizado
        with open(file_path, 'w') as f:
            f.write(content)
        
        return True
    else:
        return False

def main():
    """Função principal"""
    print(f"{Colors.BLUE}{Colors.BOLD}")
    print("=" * 60)
    print("📅 ATUALIZAÇÃO AUTOMÁTICA DE ANOS")
    print("   MATRIZ-FONTE-STN-DADOSMG")
    print("=" * 60)
    print(f"{Colors.END}")
    
    try:
        # Obter ano corrente
        current_year = get_current_year()
        print(f"📅 Ano corrente: {current_year}")
        print()
        
        # Carregar configuração
        config = load_config()
        current_ano_matriz = int(config.get('ANO_MATRIZ', current_year))
        print(f"📋 ANO_MATRIZ atual: {current_ano_matriz}")
        print()
        
        # Atualizar config.mk
        print(f"🔧 Verificando config.mk...")
        config_updated = update_config_mk(current_year)
        print()
        
        # Sempre verificar e atualizar scripts R e data.toml
        print(f"📝 Verificando arquivos...")
        
        files_to_check = [
            Path("scripts/matriz_despesa.R"),
            Path("scripts/matriz_receita.R"),
            Path("data.toml")
        ]
        
        files_updated = 0
        for file_path in files_to_check:
            if update_script_file(file_path, current_year):
                files_updated += 1
            print()
        
        # Resumo final
        total_updated = (1 if config_updated else 0) + files_updated
        
        if total_updated > 0:
            print(f"{Colors.GREEN}🎉 Atualização concluída!{Colors.END}")
            print(f"📊 Arquivos atualizados: {total_updated}")
            if config_updated:
                print(f"   ✅ config.mk")
            if files_updated > 0:
                print(f"   ✅ {files_updated} arquivo(s) de dados")
        else:
            print(f"{Colors.BLUE}ℹ️  Nenhuma atualização necessária{Colors.END}")
        
        # SEMPRE retorna True (sucesso) - com ou sem mudanças
        return True
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Operação cancelada pelo usuário{Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ Erro inesperado: {e}{Colors.END}")
        return False

def main_cli():
    """Wrapper para rodar via Poetry (pyproject.toml)"""
    success = main()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main_cli()