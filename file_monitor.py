"""
CAMADA 3: FILE MONITOR
Responsável por monitorar eventos do sistema de arquivos
"""

import time
import logging
import getpass
from datetime import datetime
from typing import Dict
from watchdog.events import FileSystemEventHandler

from backup_manager import BackupManager
from log_manager import LogManager


class FileMonitor(FileSystemEventHandler):
    """
    Monitora eventos do sistema de arquivos para múltiplas extensões
    Coordena backup e registro de modificações
    Extensões monitoradas: .dom, .prj, .xml, .lib, .txt
    """
    
    # Extensões de arquivo a monitorar
    MONITORED_EXTENSIONS = ('.dom', '.prj', '.xml', '.lib', '.txt')
    
    def __init__(self, backup_manager: BackupManager, log_manager: LogManager):
        """
        Inicializa o monitor de arquivos
        
        Args:
            backup_manager (BackupManager): Instância do gerenciador de backups
            log_manager (LogManager): Instância do gerenciador de logs
        """
        super().__init__()
        self.backup_manager = backup_manager
        self.log_manager = log_manager
        self.last_events: Dict[str, float] = {}
        extensions_str = ', '.join(self.MONITORED_EXTENSIONS)
        logging.info(f"FileMonitor inicializado para monitorar: {extensions_str}")

    def is_monitored_file(self, filepath: str) -> bool:
        """
        Verifica se o arquivo tem uma extensão monitorada
        
        Args:
            filepath (str): Caminho do arquivo
            
        Returns:
            bool: True se extensão está na lista de monitoramento
        """
        for ext in self.MONITORED_EXTENSIONS:
            if filepath.lower().endswith(ext):
                return True
        return False

    def process_event(self, event, action: str) -> None:
        """
        Processa um evento do sistema de arquivos
        
        Args:
            event: Evento capturado pelo watchdog
            action (str): Tipo de ação (CRIADO, MODIFICADO, DELETADO)
        """
        # Valida se é arquivo com extensão monitorada
        if event.is_directory or not self.is_monitored_file(event.src_path):
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
        """Capturado quando arquivo é modificado"""
        self.process_event(event, "MODIFICADO")

    def on_created(self, event):
        """Capturado quando arquivo é criado"""
        self.process_event(event, "CRIADO")

    def on_deleted(self, event):
        """Capturado quando arquivo é deletado"""
        self.process_event(event, "DELETADO")