---
title: Falha na execução do workflow em {{ date | date() }}
labels: bug
---

## 📋 Informações da Falha

**Workflow:** `{{ github.workflow }}`  
**Branch:** `{{ github.ref_name }}`  
**Commit:** `{{ github.sha }}`  
**Ator:** `{{ github.actor }}`  
**Data/Hora:** `{{ date | date() }}`  

## 🔗 Links Úteis

- [Execução do Workflow]({{ github.server_url }}/{{ github.repository }}/actions/runs/{{ github.run_id }})
- [Commit]({{ github.server_url }}/{{ github.repository }}/commit/{{ github.sha }})
- [Branch]({{ github.server_url }}/{{ github.repository }}/tree/{{ github.ref_name }})

## 📝 Próximos Passos

1. Verificar os logs da execução
2. Identificar a causa raiz da falha
3. Corrigir o problema
4. Fechar esta issue após resolução

---
*Issue criada automaticamente pelo GitHub Actions*
