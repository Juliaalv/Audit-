"""
CAMADA 2: LOG MANAGER
Responsável por gerenciar logs detalhados, consolidados e resumos diários
"""

import os
import logging
import shutil
from datetime import datetime, date
from typing import Dict


class LogManager:
    """Gerencia logs detalhados, consolidados e resumos diários"""
    
    def __init__(self, resumo_dir: str, log_dir: str, backup_folder_dir: str = None, max_resumo_files: int = 30):
        """
        Inicializa o gerenciador de logs
        
        Args:
            resumo_dir (str): Diretório para armazenar resumos diários
            log_dir (str): Diretório para armazenar logs consolidados
            backup_folder_dir (str): Diretório para armazenar backups da pasta monitorada
            max_resumo_files (int): Número máximo de resumos a manter
        """
        self.resumo_dir = resumo_dir
        self.log_dir = log_dir
        self.backup_folder_dir = backup_folder_dir
        self.max_resumo_files = max_resumo_files
        os.makedirs(self.resumo_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        if self.backup_folder_dir:
            os.makedirs(self.backup_folder_dir, exist_ok=True)
        
        self.mod_count_per_file: Dict[str, int] = {}
        self.total_modifications = 0
        self.current_day = date.today()
        self.log_entries: list = []
        
        logging.info(f"LogManager inicializado: {resumo_dir}")
        self.save_daily_summary()

    def register_modification(self, filepath: str) -> None:
        """
        Registra uma modificação no contador diário
        Verifica se mudou de dia e salva logs anteriores
        
        Args:
            filepath (str): Caminho do arquivo modificado
        """
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
        """
        Adiciona entrada ao log consolidado do dia
        
        Args:
            entry (str): Linha do log (já formatada com timestamp)
        """
        self.log_entries.append(entry)

    def save_daily_log(self) -> None:
        """Salva log consolidado do dia em arquivo"""
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
        """Salva resumo diário com estatísticas das modificações"""
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

    def backup_monitored_folder(self, source_folder: str) -> None:
        """
        Faz backup de toda a pasta monitorada ao final do dia
        
        Args:
            source_folder (str): Caminho da pasta a fazer backup
        """
        if not self.backup_folder_dir:
            return
            
        try:
            # Nome com data legível: pasta_DD-MM-YYYY_HH-MM-SS
            backup_datetime = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
            folder_name = os.path.basename(source_folder.rstrip(os.sep))
            
            # Nome do backup: pasta_DD-MM-YYYY_HH-MM-SS
            backup_name = f"{folder_name}_{backup_datetime}"
            backup_path = os.path.join(self.backup_folder_dir, backup_name)
            
            # Copia pasta inteira
            shutil.copytree(source_folder, backup_path)
            
            logging.info(f"Backup da pasta monitorada salvo: {backup_path}")
            print(f"✓ Backup da pasta monitorada salvo: {backup_path}")
            
            self.cleanup_old_folder_backups()
            
        except Exception as e:
            logging.error(f"Erro ao fazer backup da pasta monitorada: {e}")

    def cleanup_old_folder_backups(self) -> None:
        """Remove backups de pasta antigos mantendo apenas os mais recentes"""
        try:
            if not os.path.exists(self.backup_folder_dir):
                return
                
            backups = sorted(
                (os.path.join(self.backup_folder_dir, f) for f in os.listdir(self.backup_folder_dir)),
                key=os.path.getmtime
            )
            
            # Mantém apenas últimos 5 backups de pasta
            max_backups = 5
            while len(backups) > max_backups:
                mais_antigo = backups.pop(0)
                shutil.rmtree(mais_antigo)
                logging.info(f"Backup de pasta antigo removido: {mais_antigo}")
                
        except Exception as e:
            logging.error(f"Erro ao limpar backups de pasta antigos: {e}")

    def cleanup_old_logs(self) -> None:
        """Remove logs consolidados antigos mantendo apenas os mais recentes"""
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
        """Remove resumos antigos mantendo apenas os mais recentes"""
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