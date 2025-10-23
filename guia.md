# 📊 Guia Visual - Sistema de Monitoramento de Projetos


---

### monitor_prj_refactored.py 

```python
✅ Vantagens:
├─ Cada classe tem UMA responsabilidade
├─ Fácil encontrar e entender cada função
├─ Código modular e reutilizável
├─ Fácil de manutenção
├─ Cada parte pode ser testada isoladamente
├─ Fácil de estender com novos recursos
└─ Documentação integrada (docstrings)

# CAMADA 1: Responsável APENAS por Backup
class BackupManager:
    """Gerencia criação e limpeza de backups"""
    - create_backup()
    - cleanup_old_backups()

# CAMADA 2: Responsável APENAS por Logs e Resumos
class LogManager:
    """Gerencia logs e resumos diários"""
    - register_modification()
    - save_daily_summary()
    - cleanup_old_resumos()

# CAMADA 3: Responsável APENAS por Monitoramento
class ProjectMonitor:
    """Monitora eventos do sistema de arquivos"""
    - process_event()
    - on_modified()
    - on_created()
    - on_deleted()

# CAMADA 4: Responsável APENAS por Inicialização
def main():
    """Coordena tudo"""
    pass
```

---

## 📈 Pirâmide de Responsabilidades

```
                          ▲
                          │
                    ┌─────┴─────┐
                    │   main()  │  Orquestra
                    │ (CAMADA4) │  (Coordena
                    └─────┬─────┘   todos)
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
    ┌───  ──┐         ┌─── ───┐        ┌─── ────┐
    │MONITOR│         │ BACKUP│        │  LOGS  │
    │(C3)   │         │(C1)   │        │(C2)    │
    └───────┘         └───────┘        └────────┘
    Captura           Cria e           Registra
    Eventos           Limpa            Estatísticas
    
 
```

---

## 🔗 Fluxo de Dados - Diagrama Detalhado

### Quando usuário MODIFICA um arquivo:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. SISTEMA DETECTA MUDANÇA NO ARQUIVO                       │
│    └─ Watchdog captura evento do SO                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. ProjectMonitor.on_modified() é chamado                   │
│    └─ Recebe: event (arquivo que mudou)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. ProjectMonitor.process_event()                           │
│    ├─ Valida: É arquivo .prj? → event.src_path.endswith()   │
│    ├─ Não é diretório? → not event.is_directory             │
│    ├─ Filtra duplicatas: passou 5 seg? → time.time()        │
│    └─ Registra em log: print() + logging.info()             │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────────┐      ┌──────────────────┐
│ BackupManager    │      │  LogManager      │
│ .create_backup() │      │ .register_mod()  │
└────────┬─────────┘      └────────┬─────────┘
         │                         │
    ┌────▼────┐               ┌────▼──── ┐
    │Cria dir │               │Incrementa│
    │subproj. |                │contador  │
    │         │               │          │
    │Gera nome│               │Verifica  │
    │com TS   │               │mudança   │
    │         │               │de dia    │
    │Copia    │               │          │
    │arquivo  │               │Se sim:   │
    │         │               │Salva     │
    │Limpa    │               │resumo    │
    │antigos  │               │anterior  │
    └────┬────┘               └──────────┘
         │
         ▼
    Log: "Backup criado: C:\...\ProjetoA_20250101_143022_joao.prj"
    


---

## 🎯 Mapa Mental - Entendendo Cada Classe

### BackupManager (CAMADA 1)

```
┌──────────────────────────────────────────┐
│         BackupManager                    │
│   (Gerencia BACKUPS de arquivos)         │
└──────────────────────────────────────────┘
            │
    ┌───────┴────────┐
    │                │
    ▼                ▼
create_backup()   cleanup_old_backups()
├─ Cria subdir   ├─ Lista arquivos
├─ Copia arquivo │  ordenado por data
├─ Nome com TS   ├─ Remove antigos
└─ Registra log  └─ Limita a max_backups

INPUT:   filepath = "C:\...\ProjetoA.prj"
                    │
                    ▼
         Cria em: C:\Temp\Logs Monitor\ProjetoA\
                  ProjetoA_20250101_143022_joao.prj
                    │
                    ▼
OUTPUT:  True (sucesso) / False (erro)
```

### LogManager (CAMADA 2)

```
┌──────────────────────────────────────────┐
│          LogManager                      │
│  (Gerencia LOGS e RESUMOS diários)       │
└──────────────────────────────────────────┘
            │
    ┌───────┼────────┬──────────────┐
    │       │        │              │
    ▼       ▼        ▼              ▼
 register  save_   cleanup_    __init__
 _mod()    daily   old_        (estado)
           _summary resumos

Atributos internos:
├─ mod_count_per_project: {
│     "ProjetoA": 15,
│     "ProjetoB": 22,
│     "ProjetoC": 5
│  }
├─ total_modifications: 42
└─ current_day: date(2025, 1, 1)

Fluxo:
1. register_modification() incrementa contadores
2. Detecta mudança de dia (automaticamente)
3. Chama save_daily_summary()
4. Gera resumo_20250101.txt
5. cleanup_old_resumos() remove > 30 arquivos
```

### ProjectMonitor (CAMADA 3)

```
┌──────────────────────────────────────────┐
│        ProjectMonitor                    │
│  (Monitora EVENTOS do sistema)           │
└──────────────────────────────────────────┘
            │
    ┌───────┼────────┬──────────┐
    │       │        │          │
    ▼       ▼        ▼          ▼
on_modified on_created on_deleted process_event()

Fluxo por evento:

ARQUIVO MODIFICADO
        │
        ▼
on_modified(event)
        │
        ▼
process_event(event, "MODIFICADO")
        │
    ┌───┴───────────────┬───────────────────┐
    │ VALIDAÇÕES        │ Se válido:        │
    ├─ É .txt?          ├─ Registra log     │
    ├─ Não é dir?       ├─ Chama backup()   │
    ├─ >5 seg passou?   └─ Chama register() │
    └─ Se não: sai                          │
       (return)
```

---

## 📝 Exemplos Práticos de Uso

### Exemplo 1: Entender o Log

**Arquivo gerado: `monitor_prj.log`**

```
2025-01-01 10:00:00 - BackupManager inicializado: C:\Temp\Logs Monitor
2025-01-01 10:00:00 - LogManager inicializado: C:\Temp\Logs Monitor\Logs Resumo
2025-01-01 10:00:00 - ProjectMonitor inicializado
2025-01-01 10:00:00 - ======================================================================
2025-01-01 10:00:00 - SISTEMA DE MONITORAMENTO INICIADO
2025-01-01 10:00:00 - ======================================================================
2025-01-01 10:00:00 - Monitorando: C:\BKPS Elipse\ESS\EnergisaSulSudeste_180225

2025-01-01 14:30:22 - [MODIFICADO] ProjetoA.prj | Usuário: joao
2025-01-01 14:30:22 - Backup criado com sucesso: C:\Temp\Logs Monitor\ProjetoA\ProjetoA_20250101_143022_joao.prj
2025-01-01 14:30:23 - Backup antigo removido: C:\Temp\Logs Monitor\ProjetoA\ProjetoA_20250101_100000_joao.prj

2025-01-01 16:15:45 - [MODIFICADO] ProjetoB.prj | Usuário: maria
2025-01-01 16:15:45 - Backup criado com sucesso: C:\Temp\Logs Monitor\ProjetoB\ProjetoB_20250101_161545_maria.prj

2025-01-02 00:00:01 - Mudança de dia detectada
2025-01-02 00:00:01 - Resumo diário salvo: C:\Temp\Logs Monitor\Logs Resumo\resumo_20250101.txt
```

### Exemplo 2: Interpretar o Resumo

**Arquivo: `resumo_20250101.txt`**

```
============================================================
RESUMO DE MONITORAMENTO - 01/01/2025
============================================================

1. TOTAL DE MODIFICAÇÕES: 27
   Número de alterações realizadas no diretório monitorado.

2. PROJETOS MODIFICADOS: 3
   Quantidade de projetos diferentes que sofreram alterações.

3. DETALHAMENTO POR PROJETO:
------------------------------------------------------------
   ProjetoA                            -  12 modificações
   ProjetoB                            -  10 modificações
   ProjetoC                            -   5 modificações
------------------------------------------------------------
Gerado em: 2025-01-01 23:59:45
```

**O que significa:**
- ✓ 27 mudanças ocorreram neste dia
- ✓ 3 projetos diferentes foram afetados
- ✓ ProjetoA foi o mais modificado (12 vezes)
- ✓ ProjetoC teve menos mudanças (5 vezes)

### Exemplo 3: Explorar Backups

```
C:\Temp\Logs Monitor\ProjetoA\

ProjetoA_20250101_100000_joao.prj      ← Primeira modificação (10:00)
ProjetoA_20250101_110000_joao.prj      ← Segunda modificação (11:00)
ProjetoA_20250101_120000_maria.prj     ← Maria modificou (12:00)
ProjetoA_20250101_130000_joao.prj      ← João de novo (13:00)
ProjetoA_20250101_140000_joao.prj      ← Última (14:00)

Você pode:
1. Comparar versões (diferenças entre cada backup)
2. Restaurar versão anterior de qualquer hora
3. Verificar quem fez a última modificação (Maria no nome do arquivo!)
4. Ver histórico completo de mudanças
```
