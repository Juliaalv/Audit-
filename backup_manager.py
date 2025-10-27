"""
CAMADA 1: BACKUP MANAGER
Responsável por gerenciar criação e limpeza de backups
"""

import os
import time
import shutil
import logging
import getpass


class BackupManager:
    """Gerencia criação e limpeza de backups"""
    
    def __init__(self, backup_dir: str, max_backups: int = 10):
        """
        Inicializa o gerenciador de backups
        
        Args:
            backup_dir (str): Diretório raiz para armazenar backups
            max_backups (int): Número máximo de backups a manter por arquivo
        """
        self.backup_dir = backup_dir
        self.max_backups = max_backups
        os.makedirs(self.backup_dir, exist_ok=True)
        logging.info(f"BackupManager inicializado: {backup_dir}")

    def create_backup(self, filepath: str) -> str:
        """
        Cria um backup do arquivo especificado
        
        Args:
            filepath (str): Caminho completo do arquivo a fazer backup
            
        Returns:
            str: Caminho do backup criado ou string vazia se erro
        """
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
        """
        Remove backups antigos mantendo apenas os mais recentes
        
        Args:
            backup_folder (str): Diretório contendo os backups
        """
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