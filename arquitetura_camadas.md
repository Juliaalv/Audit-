#  ARQUITETURA EM CAMADAS 

## 📋 Estrutura dos Arquivos

Seu código foi separado em **4 camadas independentes**:

```
┌────────────────────────────────────────────┐
│         Camada 4: MAIN (main.py)          │
│  Inicialização e Configuração             │
└──────────┬─────────────────────────────────┘
           │
┌──────────┴────────────────────────────────┐
│    Camada 3: FILE MONITOR (file_monitor.py)  │
│    Monitora eventos do sistema            │
└──────────┬────────────────────────────────┘
           │
     ┌─────┴─────────────────────┐
     │                           │
┌────┴──────────┐    ┌──────────┴────┐
│ Camada 1:    │    │ Camada 2:     │
│ BACKUP       │    │ LOG MANAGER   │
│ (backup_...) │    │ (log_manager) │
└──────────────┘    └───────────────┘
```

---

## 📄 ARQUIVOS CRIADOS:

### 1️⃣ `backup_manager.py` (Camada 1)
**Responsabilidade:** Gerenciar backups

```python
class BackupManager:
    ✅ create_backup()        # Cria backup com timestamp
    ✅ cleanup_old_backups()  # Remove backups antigos
```

**Uso:**
```python
from backup_manager import BackupManager

backup_mgr = BackupManager(backup_dir="C:\backups")
backup_path = backup_mgr.create_backup("arquivo.txt")
```

---

### 2️⃣ `log_manager.py` (Camada 2)
**Responsabilidade:** Gerenciar logs

```python
class LogManager:
    ✅ add_log_entry()        # Adiciona ação ao log
    ✅ register_modification() # Registra modificação
    ✅ save_daily_log()       # Salva log consolidado
    ✅ save_daily_summary()   # Salva resumo diário
    ✅ cleanup_old_logs()     # Remove logs antigos
    ✅ cleanup_old_resumos()  # Remove resumos antigos
```

**Uso:**
```python
from log_manager import LogManager

log_mgr = LogManager(resumo_dir="...", log_dir="...")
log_mgr.add_log_entry("2025-01-01 10:00:00 - MODIFICADO: arquivo.txt")
log_mgr.save_daily_log()
```

---

### 3️⃣ `file_monitor.py` (Camada 3)
**Responsabilidade:** Monitorar eventos de arquivos

```python
class FileMonitor(FileSystemEventHandler):
    ✅ on_modified()   # Quando arquivo é modificado
    ✅ on_created()    # Quando arquivo é criado
    ✅ on_deleted()    # Quando arquivo é deletado
    ✅ process_event() # Processa o evento
```

**Uso:**
```python
from file_monitor import FileMonitor

monitor = FileMonitor(backup_manager, log_manager)
observer.schedule(monitor, path="C:\arquivos")
observer.start()
```

---

### 4️⃣ `main.py` (Camada 4)
**Responsabilidade:** Inicializar e orquestrar tudo

```python
def main():
    # Configura tudo
    # Instancia todas as camadas
    # Inicia o monitoramento
    # Trata Ctrl+C
```

**Uso:**
```bash
python main.py
```

---

## 🔄 FLUXO DE DADOS:

```
1. main.py inicia
   ↓
2. Cria BackupManager (Camada 1)
   ↓
3. Cria LogManager (Camada 2)
   ↓
4. Cria FileMonitor (Camada 3) passando as duas camadas anteriores
   ↓
5. Inicia Observer
   ↓
6. Aguarda eventos em loop infinito
   ↓
7. Evento detectado → FileMonitor.process_event()
   ├── Chama BackupManager.create_backup()
   └── Chama LogManager.add_log_entry()
```

---

## 💡 VANTAGENS DA SEPARAÇÃO:

### ✅ **Responsabilidade Única**
Cada camada cuida de uma coisa:
- `backup_manager.py` → Apenas backups
- `log_manager.py` → Apenas logs
- `file_monitor.py` → Apenas monitoramento
- `main.py` → Apenas inicialização

### ✅ **Fácil de Testar**
Testa cada camada isoladamente:
```python
# Testa BackupManager
backup_mgr = BackupManager("C:\test")
backup_mgr.create_backup("arquivo.txt")

# Testa LogManager
log_mgr = LogManager("resumos", "logs")
log_mgr.add_log_entry("teste")
```

### ✅ **Fácil de Manter**
Problema no backup? Procura em `backup_manager.py`
Problema em logs? Procura em `log_manager.py`

### ✅ **Fácil de Reutilizar**
Quer usar BackupManager em outro projeto?
```python
from backup_manager import BackupManager

backup_mgr = BackupManager("C:\outros\backups")
# Pronto! Funciona em qualquer lugar
```

### ✅ **Fácil de Estender**
Quer adicionar compressão aos backups?
Modifica só `backup_manager.py`:
```python
def create_backup(self, filepath: str) -> str:
    # Código existente...
    # Adiciona compressão aqui
    compress_backup(backup_path)
```

---

## 📂 ESTRUTURA RECOMENDADA:

```
seu_projeto/
├── main.py                 ← Inicia tudo
├── backup_manager.py       ← Camada 1
├── log_manager.py          ← Camada 2
├── file_monitor.py         ← Camada 3
├── requirements.txt        ← Dependências
└── README.md              ← Documentação
```

---

## 🚀 COMO EXECUTAR:

### Passo 1: Instale Dependência
```bash
pip install watchdog
```

### Passo 2: Coloque os 4 arquivos na mesma pasta
```
main.py
backup_manager.py
log_manager.py
file_monitor.py
```

### Passo 3: Configure o caminho em `main.py`
```python
path_to_watch = r"C:\seu\caminho"
backup_dir = r"C:\seu\backup"
```

### Passo 4: Execute
```bash
python main.py
```

### Passo 5: Para parar
```
Ctrl + C
```

---

## 📊 DEPENDÊNCIAS ENTRE CAMADAS:

```
main.py
  ├── usa → backup_manager.py
  ├── usa → log_manager.py
  ├── usa → file_monitor.py
  │           ├── usa → backup_manager.py
  │           └── usa → log_manager.py
  └── usa → watchdog (biblioteca externa)
```

---

## 🔗 IMPORTS CORRETOS:

Em `file_monitor.py`:
```python
from backup_manager import BackupManager
from log_manager import LogManager
```

Em `main.py`:
```python
from backup_manager import BackupManager
from log_manager import LogManager
from file_monitor import FileMonitor
```

---

## ✅ CHECKLIST DE USO:

- [ ] Todos os 4 arquivos na mesma pasta
- [ ] Instalou `pip install watchdog`
- [ ] Configurou caminhos em `main.py`
- [ ] Executou `python main.py`
- [ ] Testou Ctrl+C para parar
- [ ] Verificou logs sendo criados
- [ ] Verificou backups sendo criados

---

## 🎯 ESTRUTURA FINAL:

```
✓ Camada 1: BackupManager     (backup_manager.py)
✓ Camada 2: LogManager        (log_manager.py)
✓ Camada 3: FileMonitor       (file_monitor.py)
✓ Camada 4: Main              (main.py)

Tudo bem organizado e separado!
```

---

## 📌 RESUMO:

Você tem **4 arquivos independentes**, cada um com sua responsabilidade:

1. **backup_manager.py** - Cria e limpa backups
2. **log_manager.py** - Gerencia logs
3. **file_monitor.py** - Monitora eventos
4. **main.py** - Inicializa e orquestra

