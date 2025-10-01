#!/usr/bin/env python3
"""
Script de configuração para matriz-fonte-stn-dadosmg
Baseado no volumes-docker/config.py
"""

import os
import sys
import shutil
import hashlib
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

def print_header():
    """Imprime cabeçalho do script"""
    print(f"{Colors.BLUE}{Colors.BOLD}")
    print("=" * 60)
    print("🔧 CONFIGURAÇÃO DE VARIÁVEIS DOCKER")
    print("   MATRIZ-FONTE-STN-DADOSMG")
    print("=" * 60)
    print(f"{Colors.END}")

def safe_config_update():
    """Cria backup seguro do config.mk antes de modificar"""
    config_path = Path("config.mk")
    if not config_path.exists():
        print(f"{Colors.RED}❌ Arquivo config.mk não encontrado!{Colors.END}")
        return False, None, None
    
    # Cria backup com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = Path(f"config.mk.backup_{timestamp}")
    
    try:
        shutil.copy2(config_path, backup_path)
        print(f"✅ Backup criado: {backup_path}")
        
        # Calcula hash do arquivo original
        with open(config_path, 'rb') as f:
            original_hash = hashlib.md5(f.read()).hexdigest()
        
        return True, backup_path, original_hash
    except Exception as e:
        print(f"{Colors.RED}❌ Erro ao criar backup: {e}{Colors.END}")
        return False, None, None

def read_config_file():
    """Lê o arquivo config.mk atual e extrai os valores"""
    config_path = Path("config.mk")
    values = {}
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # Remove comentários inline
                    if '#' in value:
                        value = value.split('#')[0].strip()
                    values[key] = value
    
    return values

def validate_docker_tag(tag):
    """Valida se a tag do Docker é válida"""
    if not tag:
        return False, "Tag não pode estar vazia"
    
    # Verifica se contém apenas caracteres válidos
    valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_")
    if not all(c in valid_chars for c in tag):
        return False, "Tag contém caracteres inválidos"
    
    return True, None

def validate_ano_matriz(ano):
    """Valida se o ano da matriz é válido"""
    if not ano:
        return False, "Ano não pode estar vazio"
    
    if not ano.isdigit():
        return False, "Ano deve conter apenas números"
    
    if len(ano) != 4:
        return False, "Ano deve ter 4 dígitos"
    
    ano_int = int(ano)
    if ano_int < 2000 or ano_int > 2100:
        return False, "Ano deve estar entre 2000 e 2100"
    
    return True, None

def show_preview(new_values):
    """Mostra preview no formato do volumes-loa (sem diff)."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}📋 PREVIEW DAS CONFIGURAÇÕES{Colors.END}")
    print(f"{Colors.BLUE}{'─' * 35}{Colors.END}")
    # Ordem de exibição específica deste projeto
    ordered_keys = ['ANO_MATRIZ', 'DOCKER_TAG', 'DOCKER_USER', 'DOCKER_IMAGE']
    for key in ordered_keys:
        value = new_values.get(key, '')
        print(f"{key:<22} = {value}")

def update_config_mk(values):
    """Atualiza as variáveis no config.mk"""
    config_path = Path("config.mk")
    
    if not config_path.exists():
        print(f"{Colors.RED}Arquivo config.mk não encontrado!{Colors.END}")
        return False
    
    with open(config_path, 'r') as f:
        lines = f.readlines()
    
    # Mapear posições existentes de todas as chaves
    all_keys = ['ANO_MATRIZ', 'DOCKER_TAG', 'DOCKER_USER', 'DOCKER_IMAGE']
    key_to_idx = {k: None for k in all_keys}
    
    # Procurar em todo o arquivo
    for idx, line in enumerate(lines):
        for k in all_keys:
            if line.startswith(f"{k}="):
                key_to_idx[k] = idx

    # Atualizar valores
    for key, value in values.items():
        if key in key_to_idx and key_to_idx[key] is not None:
            lines[key_to_idx[key]] = f"{key}={value}\n"

    with open(config_path, 'w') as f:
        f.writelines(lines)
    
    return True

def finalize_config_update(new_values, backup_path, original_hash):
    """Finaliza a atualização com validação"""
    if not update_config_mk(new_values):
        return False
    
    # Valida se o arquivo foi modificado corretamente
    config_path = Path("config.mk")
    with open(config_path, 'rb') as f:
        new_hash = hashlib.md5(f.read()).hexdigest()
    
    if new_hash == original_hash:
        print(f"{Colors.YELLOW}⚠️  Nenhuma mudança foi feita{Colors.END}")
        if backup_path and backup_path.exists():
            backup_path.unlink()
        return True  # Retorna True para indicar sucesso (sem mudanças)
    
    return True

def restore_from_backup(backup_path):
    """Restaura o arquivo do backup"""
    if backup_path and backup_path.exists():
        shutil.copy2(backup_path, "config.mk")
        print(f"✅ Arquivo restaurado do backup: {backup_path}")

def cleanup_backup(backup_path):
    """Remove o arquivo de backup"""
    if backup_path and backup_path.exists():
        try:
            backup_path.unlink()
            return True
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Erro ao remover backup {backup_path}: {e}{Colors.END}")
            return False
    return True

def main():
    """Função principal"""
    # Verifica se é modo não-interativo
    non_interactive = '--non-interactive' in sys.argv or not sys.stdin.isatty()
    
    print_header()
    
    # Variáveis para o protocolo de conferência
    backup_path = None
    original_hash = None
    
    # Tratamento de erro mais elegante
    try:
        # PROTOCOLO DE CONFERÊNCIA: Inicia preparação
        success, backup_path, original_hash = safe_config_update()
        if not success:
            print(f"{Colors.RED}❌ Falha no protocolo de conferência{Colors.END}")
            sys.exit(1)
        
        # Lê valores atuais
        current_values = read_config_file()
        
        # Define valores padrão se não existirem
        default_values = {
            'ANO_MATRIZ': '2025',
            'DOCKER_TAG': 'matriz-stn2025',
            'DOCKER_USER': 'aidsplormg',
            'DOCKER_IMAGE': 'matriz-fonte-stn-dadosmg'
        }
        
        for key, default_value in default_values.items():
            if key not in current_values:
                current_values[key] = default_value
        
        if not non_interactive:
            print(f"{Colors.BLUE}Configuração atual:{Colors.END}")
            for key in ['ANO_MATRIZ', 'DOCKER_TAG', 'DOCKER_USER', 'DOCKER_IMAGE']:
                value = current_values.get(key, 'NÃO DEFINIDO')
                print(f"  {key} = {value}")
            
            print(f"\n{Colors.YELLOW}Digite os novos valores (Enter para manter o atual):{Colors.END}")
            
            new_values = {}
            for key in ['ANO_MATRIZ', 'DOCKER_TAG', 'DOCKER_USER', 'DOCKER_IMAGE']:
                current_value = current_values.get(key, '')
                prompt = f"{key} [{current_value}]: "
                
                try:
                    new_value = input(prompt).strip()
                    if new_value:
                        # Validação específica por tipo de campo
                        if key == 'ANO_MATRIZ':
                            is_valid, error_msg = validate_ano_matriz(new_value)
                            if not is_valid:
                                print(f"{Colors.RED}❌ {error_msg}{Colors.END}")
                                print(f"{Colors.YELLOW}Mantendo valor atual: {current_value}{Colors.END}")
                                new_value = current_value
                        elif key == 'DOCKER_TAG':
                            is_valid, error_msg = validate_docker_tag(new_value)
                            if not is_valid:
                                print(f"{Colors.RED}❌ {error_msg}{Colors.END}")
                                print(f"{Colors.YELLOW}Mantendo valor atual: {current_value}{Colors.END}")
                                new_value = current_value
                        
                        new_values[key] = new_value
                    else:
                        new_values[key] = current_value
                except KeyboardInterrupt:
                    print(f"\n{Colors.YELLOW}Operação cancelada.{Colors.END}")
                    sys.exit(0)
        else:
            # Modo não-interativo: usa valores atuais
            new_values = {k: v for k, v in current_values.items() if k in ['ANO_MATRIZ', 'DOCKER_TAG', 'DOCKER_USER', 'DOCKER_IMAGE']}
            print(f"{Colors.BLUE}{Colors.BOLD}⚡ MODO NÃO-INTERATIVO{Colors.END}")
            print(f"{Colors.BLUE}{'─' * 20}{Colors.END}")
            print(f"{Colors.GREEN}Usando configurações atuais do config.mk{Colors.END}\n")
        # Preview e confirmação (UX volumes-loa)
        show_preview(new_values)
        if not non_interactive:
            try:
                confirm = input("\nSalvar configurações? (y/N): ").strip().lower()
            except KeyboardInterrupt:
                confirm = 'n'
        else:
            confirm = 'y'

        if confirm != 'y':
            # Cancela: restaura backup e remove backup
            print(f"\n{Colors.YELLOW}Operação cancelada. Restaurando backup...{Colors.END}")
            restore_from_backup(backup_path)
            cleanup_backup(backup_path)
            print(f"{Colors.GREEN}✅ Estado original restaurado e backup removido{Colors.END}")
            sys.exit(0)

        # PROTOCOLO DE CONFERÊNCIA: Finaliza com validação
        if finalize_config_update(new_values, backup_path, original_hash):
            # Remover backup após sucesso
            cleanup_backup(backup_path)
            # Verificar se houve mudanças reais
            config_path = Path("config.mk")
            with open(config_path, 'rb') as f:
                new_hash = hashlib.md5(f.read()).hexdigest()
            if new_hash == original_hash:
                print(f"\n{Colors.BLUE}ℹ️  Configuração confirmada - valores atuais mantidos{Colors.END}")
            else:
                print(f"\n{Colors.GREEN}🎉 Configuração atualizada com sucesso!{Colors.END}")
        else:
            print(f"\n{Colors.RED}❌ Falha na validação - configuração não foi salva{Colors.END}")
            # Em caso de falha, restaurar e limpar
            restore_from_backup(backup_path)
            cleanup_backup(backup_path)
            sys.exit(1)
        
        # Mensagem informativa sobre próximo passo
        print(f"\n{Colors.BLUE}{Colors.BOLD}💡 SUGESTÃO DE PRÓXIMO PASSO{Colors.END}")
        print(f"{Colors.BLUE}{'─' * 30}{Colors.END}")
        print(f"{Colors.GREEN}make docker-build{Colors.END} - Constrói a imagem Docker")
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Operação cancelada pelo usuário{Colors.END}")
        print(f"{Colors.BLUE}💡 Restaurando estado original...{Colors.END}")
        try:
            if backup_path and backup_path.exists():
                restore_from_backup(backup_path)
                cleanup_backup(backup_path)
                print(f"{Colors.GREEN}✅ Backup removido com sucesso{Colors.END}")
        except Exception as cleanup_error:
            print(f"{Colors.YELLOW}⚠️  Aviso: Erro ao limpar backup: {cleanup_error}{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Erro inesperado: {e}{Colors.END}")
        print(f"{Colors.BLUE}💡 Restaurando estado original...{Colors.END}")
        try:
            if backup_path and backup_path.exists():
                restore_from_backup(backup_path)
                cleanup_backup(backup_path)
                print(f"{Colors.GREEN}✅ Backup removido com sucesso{Colors.END}")
        except Exception as cleanup_error:
            print(f"{Colors.YELLOW}⚠️  Aviso: Erro ao limpar backup: {cleanup_error}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()
