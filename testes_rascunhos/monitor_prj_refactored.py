"""
Sistema de Monitoramento de Arquivos .txt com Log Consolidado
Monitora alterações em arquivos, cria backups e gera logs detalhados
"""

import time
import os
import logging
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import getpass
from datetime import datetime, date
from typing import Dict


class BackupManager:
    """Gerencia criação e limpeza de backups"""
    
    def __init__(self, backup_dir: str, max_backups: int = 10):
        self.backup_dir = backup_dir
        self.max_backups = max_backups
        os.makedirs(self.backup_dir, exist_ok=True)
        logging.info(f"BackupManager inicializado: {backup_dir}")

    def create_backup(self, filepath: str) -> str:
        try:
            filename = os.path.basename(filepath)
            name_only, ext = os.path.splitext(filename)
            file_backup_dir = os.path.join(self.backup_dir, name_only)
            os.makedirs(file_backup_dir, exist_ok=True)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            user = getpass.getuser()
            backup_filename = f"{name_only}_{timestamp}_{user}{ext}"
            backup_path = os.path.join(file_backup_dir, backup_filename)
            
            shutil.copy2(filepath, backup_path)
            self.cleanup_old_backups(file_backup_dir)
            return backup_path
            
        except Exception as e:
            logging.error(f"Erro ao criar backup de {filepath}: {e}")
            return ""

    def cleanup_old_backups(self, backup_folder: str) -> None:
        try:
            backups = sorted(
                (os.path.join(backup_folder, f) for f in os.listdir(backup_folder)),
                key=os.path.getmtime
            )
            while len(backups) > self.max_backups:
                oldest = backups.pop(0)
                os.remove(oldest)
                logging.info(f"Backup antigo removido: {oldest}")
        except Exception as e:
            logging.error(f"Erro ao limpar backups: {e}")


class LogManager:
    """Gerencia logs detalhados, consolidados e resumos diários"""
    
    def __init__(self, resumo_dir: str, log_dir: str, max_resumo_files: int = 30):
        self.resumo_dir = resumo_dir
        self.log_dir = log_dir
        self.max_resumo_files = max_resumo_files
        os.makedirs(self.resumo_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.mod_count_per_file: Dict[str, int] = {}
        self.total_modifications = 0
        self.current_day = date.today()
        self.log_entries: list = []
        
        logging.info(f"LogManager inicializado: {resumo_dir}")
        self.save_daily_summary()

    def register_modification(self, filepath: str) -> None:
        today = date.today()
        if today != self.current_day:
            self.save_daily_summary()
            self.save_daily_log()
            self.mod_count_per_file.clear()
            self.total_modifications = 0
            self.log_entries.clear()
            self.current_day = today
        
        filename = os.path.basename(filepath)
        name_only, _ = os.path.splitext(filename)
        self.total_modifications += 1
        self.mod_count_per_file[name_only] = self.mod_count_per_file.get(name_only, 0) + 1

    def add_log_entry(self, entry: str) -> None:
        """Adiciona entrada ao log consolidado do dia"""
        self.log_entries.append(entry)

    def save_daily_log(self) -> None:
        """Salva log consolidado do dia"""
        if not self.log_entries:
            return
            
        try:
            today_str = self.current_day.strftime("%Y%m%d")
            log_path = os.path.join(self.log_dir, f"log_consolidado_{today_str}.txt")
            
            lines = [
                f"{'='*80}\n",
                f"LOG CONSOLIDADO - {self.current_day.strftime('%d/%m/%Y')}\n",
                f"{'='*80}\n\n"
            ]
            
            for entry in self.log_entries:
                lines.append(f"{entry}\n")
            
            lines.append(f"\n{'='*80}\n")
            lines.append(f"Total de eventos registrados: {len(self.log_entries)}\n")
            lines.append(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            lines.append(f"{'='*80}\n")
            
            with open(log_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            logging.info(f"Log consolidado salvo: {log_path}")
            print(f"✓ Log consolidado salvo: {log_path}")
            self.cleanup_old_logs()
            
        except Exception as e:
            logging.error(f"Erro ao salvar log consolidado: {e}")

    def save_daily_summary(self) -> None:
        """Salva resumo diário com estatísticas"""
        try:
            today_str = self.current_day.strftime("%Y%m%d")
            resumo_path = os.path.join(self.resumo_dir, f"resumo_{today_str}.txt")
            
            total_files = len(self.mod_count_per_file)
            lines = [
                f"{'='*70}\n",
                f"RESUMO DE MONITORAMENTO - {self.current_day.strftime('%d/%m/%Y')}\n",
                f"{'='*70}\n\n",
                f"1. TOTAL DE MODIFICAÇÕES: {self.total_modifications}\n",
                f"   Número de alterações realizadas no diretório monitorado.\n\n",
                f"2. ARQUIVOS MODIFICADOS: {total_files}\n",
                f"   Quantidade de arquivos diferentes que sofreram alterações.\n\n",
                f"3. DETALHAMENTO POR ARQUIVO:\n",
                f"{'-'*70}\n"
            ]
            
            for file in sorted(self.mod_count_per_file.keys()):
                count = self.mod_count_per_file[file]
                lines.append(f"   {file:40} - {count:3} modificações\n")
            
            lines.append(f"{'-'*70}\n")
            lines.append(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            with open(resumo_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            logging.info(f"Resumo diário salvo: {resumo_path}")
            print(f"✓ Resumo salvo: {resumo_path}")
            self.cleanup_old_resumos()
            
        except Exception as e:
            logging.error(f"Erro ao salvar resumo: {e}")

    def cleanup_old_logs(self) -> None:
        """Remove logs consolidados antigos"""
        try:
            arquivos = sorted(
                (os.path.join(self.log_dir, f) for f in os.listdir(self.log_dir)),
                key=os.path.getmtime
            )
            while len(arquivos) > self.max_resumo_files:
                mais_antigo = arquivos.pop(0)
                os.remove(mais_antigo)
                logging.info(f"Log consolidado antigo removido: {mais_antigo}")
        except Exception as e:
            logging.error(f"Erro ao limpar logs: {e}")

    def cleanup_old_resumos(self) -> None:
        """Remove resumos antigos"""
        try:
            arquivos = sorted(
                (os.path.join(self.resumo_dir, f) for f in os.listdir(self.resumo_dir)),
                key=os.path.getmtime
            )
            while len(arquivos) > self.max_resumo_files:
                mais_antigo = arquivos.pop(0)
                os.remove(mais_antigo)
                logging.info(f"Resumo antigo removido: {mais_antigo}")
        except Exception as e:
            logging.error(f"Erro ao limpar resumos: {e}")


class FileMonitor(FileSystemEventHandler):
    """Monitora eventos de arquivos .txt"""
    
    def __init__(self, backup_manager: BackupManager, log_manager: LogManager):
        super().__init__()
        self.backup_manager = backup_manager
        self.log_manager = log_manager
        self.last_events: Dict[str, float] = {}
        logging.info("FileMonitor inicializado")

    def process_event(self, event, action: str) -> None:
        # Valida se é arquivo .txt
        if event.is_directory or not event.src_path.endswith('.txt'):
            return
        
        # Filtra eventos duplicados muito próximos
        now = time.time()
        last_time = self.last_events.get(event.src_path, 0)
        if now - last_time < 5:
            return
        self.last_events[event.src_path] = now
        
        # Registra a ação
        user = getpass.getuser()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filepath = event.src_path
        message = f"{timestamp} - {action}: {filepath} | Usuário: {user}"
        logging.info(message)
        print(f"{message}")
        
        # Adiciona ao log consolidado
        self.log_manager.add_log_entry(message)
        
        # Executa ações específicas
        if action in ("MODIFICADO", "CRIADO"):
            backup_path = self.backup_manager.create_backup(event.src_path)
            if backup_path:
                backup_msg = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Backup criado: {backup_path}"
                logging.info(backup_msg)
                print(f"{backup_msg}")
                self.log_manager.add_log_entry(backup_msg)
            self.log_manager.register_modification(event.src_path)

    def on_modified(self, event):
        self.process_event(event, "MODIFICADO")

    def on_created(self, event):
        self.process_event(event, "CRIADO")

    def on_deleted(self, event):
        self.process_event(event, "DELETADO")


def setup_logging(log_file: str = 'monitor_txt.log') -> None:
    """Configura o sistema de logging"""
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info("=" * 80)
    logging.info("MONITORAMENTO INICIADO")
    logging.info("=" * 80)


def main():
    """Função principal"""
    # CONFIGURE SEUS CAMINHOS AQUI:
    path_to_watch = r"C:\Users\Júlia\Desktop\Teste\BKPS Elipse\ESS\EnergisaSulSudeste_180225"
    backup_dir = r"C:\Users\Júlia\Desktop\Teste\Temp\Logs Monitor"
    resumo_dir = os.path.join(backup_dir, "Logs Resumo")
    log_consolidado_dir = os.path.join(backup_dir, "Logs Consolidados")
    
    # Cria diretórios
    os.makedirs(backup_dir, exist_ok=True)
    os.makedirs(resumo_dir, exist_ok=True)
    os.makedirs(log_consolidado_dir, exist_ok=True)
    
    # Configura logging
    setup_logging('monitor_txt.log')
    
    try:
        # Inicializa gerenciadores
        backup_mgr = BackupManager(backup_dir=backup_dir, max_backups=10)
        log_mgr = LogManager(resumo_dir=resumo_dir, log_dir=log_consolidado_dir, max_resumo_files=30)
        
        # Inicializa monitor
        monitor = FileMonitor(backup_mgr, log_mgr)
        
        # Configura observer
        observer = Observer()
        observer.schedule(monitor, path=path_to_watch, recursive=True)
        observer.start()
        
        # Registra início
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_message = f"{timestamp} - Monitoramento iniciado em: {path_to_watch}"
        logging.info(start_message)
        print("\n" + "=" * 80)
        print("MONITORAMENTO DE ARQUIVOS INICIADO")
        print("=" * 80)
        print(f"Timestamp: {timestamp}")
        print(f"Diretório: {path_to_watch}")
        print(f"Backups em: {backup_dir}")
        print(f"Resumos em: {resumo_dir}")
        print(f"Logs consolidados em: {log_consolidado_dir}")
        print("Pressione Ctrl+C para parar...")
        print("=" * 80 + "\n")
        
        # Loop principal
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n\n{timestamp} - Parando monitoramento...")
        log_mgr.save_daily_log()  # Salva log consolidado
        log_mgr.save_daily_summary()
        observer.stop()
        logging.info(f"{timestamp} - Monitoramento interrompido pelo usuário")
        print("✓ Log consolidado e resumo final salvos. Até logo!")
        
    except Exception as e:
        logging.error(f"Erro crítico: {e}")
        print(f"✗ Erro: {e}")
        
    finally:
        observer.join()


if __name__ == "__main__":
    main()