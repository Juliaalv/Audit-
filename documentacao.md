# 📋 Documentação Completa - Sistema de Monitoramento de Projetos 

## 📑 Índice
1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Componentes](#componentes)
4. [Fluxo de Execução](#fluxo-de-execução)
5. [Como Usar](#como-usar)
6. [Estrutura de Diretórios](#estrutura-de-diretórios)
7. [Roadmap de Melhorias](#roadmap-de-melhorias)

---

## 🎯 Visão Geral

O **Sistema de Monitoramento de Projetos** é uma aplicação que:

- **Monitora** alterações em arquivos (projetos Elipse)
- **Cria backups** automáticos de cada modificação
- **Rastreia** quem modificou e quando
- **Gera resumos** diários com estatísticas
- **Gerencia** limpeza automática de backups antigos

### Principais Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| **Monitoramento em Tempo Real** | Captura modificações assim que ocorrem |
| **Backup Automático** | Cria cópia de cada versão modificada |
| **Rastreabilidade** | Registra usuário, data e hora de cada ação |
| **Log Detalhado** | Arquivo log com todas as ações |
| **Resumo Diário** | Estatísticas consolidadas por dia |
| **Auto-limpeza** | Remove backups e resumos antigos automaticamente |

---

## Arquitetura

O código segue uma **arquitetura em camadas** com separação clara de responsabilidades:

```
┌─────────────────────────────────────────────────┐
│         CAMADA 4: INICIALIZAÇÃO                 │
│          (main, setup_logging)                  │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│    CAMADA 3: PROJECT MONITOR                    │
│   (Captura eventos do sistema)                  │
└────────────────┬────────────────────────────────┘
                 │
        ┌────────┴──────────┐
        │                   │
┌───────▼─────────┐  ┌──────▼──────────┐
│  CAMADA 2:      │  │   CAMADA 1:     │
│  LOG MANAGER    │  │  BACKUP MANAGER │
│ (Resumos/Stats) │  │  (Cópias arquiv)│
└─────────────────┘  └─────────────────┘
```

### Princípios de Design

1. **Separação de Responsabilidades**: Cada classe tem UMA responsabilidade
2. **Coesão Alta**: Métodos relacionados ficam na mesma classe
3. **Acoplamento Baixo**: Classes não dependem umas das outras diretamente
4. **Extensibilidade**: Fácil adicionar novos recursos

---

## 🔧 Componentes

### CAMADA 1: BackupManager

**Responsabilidade**: Gerenciar criação e limpeza de backups

#### O que faz:

```
Arquivo modificado
        ↓
BackupManager.create_backup()
        ↓
├─ Cria subdiretório para o projeto
├─ Gera nome com timestamp + usuário
├─ Copia arquivo com metadados
├─ Chama cleanup para remover antigos
└─ Registra em log
```

#### Métodos Principais

**`__init__(backup_dir, max_backups=10)`**
- Inicializa o gerenciador
- Cria diretório se não existir
- Define limite de backups por arquivo

**`create_backup(filepath)`**
- Cria cópia do arquivo
- Nome: `projeto_20250101_120000_usuario.prj`
- Retorna `True/False` indicando sucesso

**`cleanup_old_backups(backup_folder)`**
- Lista todos os backups da pasta
- Ordena por data de modificação
- Remove os mais antigos quando excedem limite

#### Exemplo de Estrutura Gerada:

```
C:\Temp\Logs Monitor\
├── ProjetoA\
│   ├── ProjetoA_20250101_100000_joao.prj
│   ├── ProjetoA_20250101_120000_joao.prj
│   ├── ProjetoA_20250101_140000_maria.prj
│   └── ProjetoA_20250101_160000_joao.prj
└── ProjetoB\
    ├── ProjetoB_20250101_110000_joao.prj
    └── ProjetoB_20250101_130000_joao.prj
```

---

### CAMADA 2: LogManager

**Responsabilidade**: Gerenciar logs e resumos diários

#### O que faz:

```
Modificação ocorre
        ↓
LogManager.register_modification()
        ↓
├─ Verifica se mudou de dia
│  ├─ Se SIM: salva resumo anterior
│  └─ Se NÃO: continua
├─ Incrementa contador do projeto
├─ Incrementa total de modificações
└─ Aguarda para salvar resumo
```

#### Atributos

```python
mod_count_per_project: Dict[str, int]  # {projeto: quantidade}
total_modifications: int                # Total do dia
current_day: date                       # Data atual
```

#### Métodos Principais

**`__init__(resumo_dir, max_resumo_files=30)`**
- Inicializa gerenciador
- Cria diretório de resumos
- Reseta contadores

**`register_modification(filepath)`**
- Verifica mudança de dia
- Incrementa contadores
- Detecta automaticamente mudança de dia

**`save_daily_summary()`**
- Gera arquivo de resumo
- Formata com estatísticas
- Remove resumos antigos automaticamente

#### Exemplo de Resumo Gerado:

```
============================================================
RESUMO DE MONITORAMENTO - 01/01/2025
============================================================

1. TOTAL DE MODIFICAÇÕES: 42
   Número de alterações realizadas no diretório monitorado.

2. PROJETOS MODIFICADOS: 3
   Quantidade de projetos diferentes que sofreram alterações.

3. DETALHAMENTO POR PROJETO:
------------------------------------------------------------
   ProjetoA                            -  15 modificações
   ProjetoB                            -  22 modificações
   ProjetoC                            -   5 modificações
------------------------------------------------------------
Gerado em: 2025-01-01 18:30:45
```

---

### CAMADA 3: ProjectMonitor

**Responsabilidade**: Capturar e processar eventos do sistema

#### O que faz:

```
Sistema de Arquivos gera evento
        ↓
ProjectMonitor.on_modified/on_created/on_deleted()
        ↓
├─ Valida o arquivo 
├─ Filtra eventos duplicados (menos 5 seg)
├─ Registra em log
└─ Coordena ações:
   ├─ Se criado/modificado: chama BackupManager
   └─ Se criado/modificado: chama LogManager
```

#### Métodos Principais

**`process_event(event, action)`**
- Método central que processa eventos
- Filtra duplicatas com 5 segundos de tolerância
- Coordena chamadas para BackupManager e LogManager

**`on_modified(event)`**
- Executado quando arquivo é modificado
- Dispara `process_event` com action="MODIFICADO"

**`on_created(event)`**
- Executado quando arquivo é criado
- Dispara `process_event` com action="CRIADO"

**`on_deleted(event)`**
- Executado quando arquivo é deletado
- Apenas registra, não faz backup

#### Por que Filtra Duplicatas?

Quando você salva um arquivo, o sistema de arquivos pode gerar VÁRIOS eventos:
- Um evento de modificação na criação do arquivo
- Múltiplos eventos conforme o arquivo é escrito
- Um evento final de fechamento

O filtro evita backups desnecessários mantendo um registro por arquivo a cada 5 segundos.

---

### CAMADA 4: Inicialização

**Responsabilidade**: Configurar e iniciar o sistema

#### `setup_logging(log_file)`

Configura o sistema de logging global:
```
├─ Arquivo de log
├─ Nível: INFO (informações, avisos, erros)
├─ Formato: "data-hora - tipo - mensagem"
└─ Separa sessões com linha divisória
```

#### `main()`

Orquestra toda a inicialização:

1. **Define caminhos**
   ```python
   path_to_watch = r"C:\BKPS Elipse\..."  # O que monitorar
   backup_dir = r"C:\Temp\..."            # Onde salvar backups
   resumo_dir = ...                        # Onde salvar resumos
   ```

2. **Cria diretórios**
   ```python
   os.makedirs(backup_dir, exist_ok=True)
   os.makedirs(resumo_dir, exist_ok=True)
   ```

3. **Inicializa sistema de logging**
   ```python
   setup_logging()
   ```

4. **Cria gerenciadores**
   ```python
   backup_mgr = BackupManager(...)
   log_mgr = LogManager(...)
   ```

5. **Cria monitor**
   ```python
   monitor = ProjectMonitor(backup_mgr, log_mgr)
   ```

6. **Inicia observação**
   ```python
   observer = Observer()
   observer.schedule(monitor, path=path_to_watch, recursive=True)
   observer.start()
   ```

7. **Loop principal** (aguarda eventos)
   ```python
   while True:
       time.sleep(1)
   ```

---

## 🔄 Fluxo de Execução

### Cenário: Usuário modifica arquivo "ProjetoA.prj"

```
1️⃣  Sistema detecta: "arquivo modificado"
        ↓
2️⃣  on_modified(event) é acionado
        ↓
3️⃣  process_event(event, "MODIFICADO")
        ├─ Valida: É arquivo .prj? ✓
        ├─ Filtro: Passou 5 segundos? ✓
        └─ Registra usuário em log
        ↓
4️⃣  backup_manager.create_backup(filepath)
        ├─ Cria: C:\Temp\Logs Monitor\ProjetoA\
        ├─ Copia: ProjetoA_20250101_143022_joao.prj
        ├─ Registra: "Backup criado: ..."
        └─ Limpa: Remove backups > 10
        ↓
5️⃣  log_manager.register_modification(filepath)
        ├─ Verifica: Mudou de dia? Não
        ├─ Incrementa: total_modifications += 1
        ├─ Incrementa: ProjetoA count += 1
        └─ Aguarda próxima mudança de dia
        ↓
6️⃣  23h59m59s -> 00h00m00s (mudou de dia)
        ├─ Detecta: current_day != today
        └─ save_daily_summary()
            ├─ Gera: resumo_20250101.txt
            ├─ Registra: Estatísticas do dia
            └─ Limpa: Remove resumos > 30

```

---

## 📖 Como Usar

### Instalação de Dependências

```bash
pip install watchdog
```

### Configuração

Abra `monitor_prj_refactored.py` e ajuste os caminhos na função `main()`:

```python
def main():
    # AJUSTE ESTES CAMINHOS PARA SUA REALIDADE
    path_to_watch = r"C:\BKPS Elipse\ESS\EnergisaSulSudeste_180225"
    backup_dir = r"C:\Temp\Logs Monitor"
    resumo_dir = os.path.join(backup_dir, "Logs Resumo")
    
    # ... resto do código
```

### Execução

**Terminal/CMD:**
```bash
python monitor_prj_refactored.py
```

**Saída esperada:**
```
======================================================================
MONITORAMENTO DE PROJETOS INICIADO
======================================================================
Diretório: C:\BKPS Elipse\ESS\EnergisaSulSudeste_180225
Backups em: C:\Temp\Logs Monitor
Resumos em: C:\Temp\Logs Monitor\Logs Resumo
Pressione Ctrl+C para parar...
======================================================================

  [MODIFICADO] ProjetoA.prj | Usuário: joao
  ✓ Resumo salvo: C:\Temp\Logs Monitor\Logs Resumo\resumo_20250101.txt
```

### Parada Segura

```
Pressione: Ctrl+C

Saída:
  Parando monitoramento...
  ✓ Resumo final salvo. Até logo!
```

---

## 📁 Estrutura de Diretórios

Após execução, você terá:

```
C:\Temp\Logs Monitor\
│
├── monitor_prj.log                    # Log detalhado de todas ações
│
├── ProjetoA\                          # Backups do ProjetoA
│   ├── ProjetoA_20250101_100000_joao.prj
│   ├── ProjetoA_20250101_120000_joao.prj
│   ├── ProjetoA_20250101_140000_maria.prj
│   └── ProjetoA_20250101_160000_joao.prj
│
├── ProjetoB\                          # Backups do ProjetoB
│   ├── ProjetoB_20250101_110000_joao.prj
│   └── ProjetoB_20250101_130000_joao.prj
│
└── Logs Resumo\                       # Resumos diários
    ├── resumo_20241231.txt
    ├── resumo_20250101.txt
    └── resumo_20250102.txt
```

---

## Roadmap de Melhorias

### ✅ FASE 1 (Atual)
- [x] Monitoramento básico de arquivos 
- [x] Backup automático com timestamp
- [x] Log detalhado
- [x] Resumo diário
- [x] Auto-limpeza de backups antigos

### 📋 FASE 2 (Melhorias)

1. **Revisão de Estrutura de Código** ✅
   - Organizar código por estrutura de desenvolvimento de software
   - Separar em camadas de responsabilidade
   - Documentar cada função

2. **Análise de Salvamento** (Novo)
   - Backup full diário em horário determinado
   - Origem e destino configurável
   - Diferencial entre modificações antes/depois

3. **Log Detalhado** ✅ (em progresso)
   - Armazenar toda ação de modificação
   - Quem modificou, quando, qual arquivo

4. **Log Resumido** ✅ (em progresso)
   - Resumo diário consolidado
   - Estatísticas por projeto



---

## 🔍 Troubleshooting

### Problema: "Nenhum arquivo de resumo é criado"

**Solução**: Verifique se há modificações happening em arquivos `.txt`. O resumo é salvo:
- Quando muda de dia
- Quando você pressiona Ctrl+C para parar

### Problema: "Muitos backups sendo criados muito rápido"

**Solução**: Aumentar o filtro de duplicatas de 5 para 10 segundos:
```python
if now - last_time < 10:  # Aumentado de 5
    return
```

### Problema: "Permissão negada ao criar backup"

**Solução**: 
1. Verifique permissões na pasta de destino
2. Execute como Administrador
3. Mude o `backup_dir` para local com permissão de escrita

### Problema: "Watchdog não funciona"

**Solução**:
```bash
# Reinstale dependência
pip install --upgrade watchdog
```

---


**Princípio**: Cada classe é responsável por uma coisa e faz isso bem!