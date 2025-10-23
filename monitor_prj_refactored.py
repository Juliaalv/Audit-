"""
Sistema de Monitoramento de Arquivos .prj (Elipse)

Este módulo monitora alterações em arquivos de projetos (.prj), criando backups
incrementais e gerando relatórios diários das modificações.

Estrutura:
- BackupManager: Gerencia backups de arquivos
- LogManager: Gerencia logs detalhados e resumidos
- ProjectMonitor: Monitora eventos do sistema de arquivos
- main(): Inicializa e executa o monitoramento
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


# ============================================================================
# CAMADA 1: BACKUP MANAGER - Responsável por gerenciar backups
# ============================================================================

class BackupManager:
    """
    Gerencia a criação e limpeza de backups de arquivos.
    
    Responsabilidades:
    - Criar cópia de segurança de arquivos modificados
    - Manter um número máximo de backups por arquivo
    - Limpar backups antigos automaticamente
    """
    
    def __init__(self, backup_dir: str, max_backups: int = 10):
        """
        Inicializa o gerenciador de backups.
        
        Args:
            backup_dir (str): Diretório raiz para armazenar backups
            max_backups (int): Número máximo de backups a manter por arquivo
        """
        self.backup_dir = backup_dir
        self.max_backups = max_backups
        os.makedirs(self.backup_dir, exist_ok=True)
        logging.info(f"BackupManager inicializado: {backup_dir}")

    def create_backup(self, filepath: str) -> bool:
        """
        Cria um backup do arquivo especificado.
        
        O backup é armazenado em um subdiretório nomeado pelo projeto,
        com timestamp e usuário no nome do arquivo para rastreabilidade.
        
        Args:
            filepath (str): Caminho completo do arquivo a fazer backup
            
        Returns:
            bool: True se backup foi criado com sucesso, False caso contrário
        """
        try:
            filename = os.path.basename(filepath)
            name_only, ext = os.path.splitext(filename)
            
            # Cria diretório específico para backups deste projeto
            file_backup_dir = os.path.join(self.backup_dir, name_only)
            os.makedirs(file_backup_dir, exist_ok=True)
            
            # Monta nome do backup com timestamp e usuário
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            user = getpass.getuser()
            backup_filename = f"{name_only}_{timestamp}_{user}{ext}"
            backup_path = os.path.join(file_backup_dir, backup_filename)
            
            # Copia arquivo preservando metadados
            shutil.copy2(filepath, backup_path)
            logging.info(f"Backup criado com sucesso: {backup_path}")
            
            # Limpa backups antigos
            self.cleanup_old_backups(file_backup_dir)
            
            return True
            
        except Exception as e:
            logging.error(f"Erro ao criar backup de {filepath}: {e}")
            return False

    def cleanup_old_backups(self, backup_folder: str) -> None:
        """
        Remove backups antigos mantendo apenas os mais recentes.
        
        Lista todos os backups, ordena por data de modificação e
        remove os mais antigos até ficar no limite máximo.
        
        Args:
            backup_folder (str): Diretório contendo os backups
        """
        try:
            # Lista e ordena backups por data (mais antigos primeiro)
            backups = sorted(
                (os.path.join(backup_folder, f) for f in os.listdir(backup_folder)),
                key=os.path.getmtime
            )
            
            # Remove backups que excedem o máximo permitido
            while len(backups) > self.max_backups:
                oldest = backups.pop(0)
                os.remove(oldest)
                logging.info(f"Backup antigo removido: {oldest}")
                
        except Exception as e:
            logging.error(f"Erro ao limpar backups antigos em {backup_folder}: {e}")


# ============================================================================
# CAMADA 2: LOG MANAGER - Responsável por gerenciar logs e resumos
# ============================================================================

class LogManager:
    """
    Gerencia logs detalhados e resumos diários das modificações.
    
    Responsabilidades:
    - Manter contador de modificações por dia
    - Gerar resumo diário automático quando muda de dia
    - Limpar arquivos de resumo antigos
    """
    
    def __init__(self, resumo_dir: str, max_resumo_files: int = 30):
        """
        Inicializa o gerenciador de logs.
        
        Args:
            resumo_dir (str): Diretório para armazenar resumos diários
            max_resumo_files (int): Número máximo de resumos a manter
        """
        self.resumo_dir = resumo_dir
        self.max_resumo_files = max_resumo_files
        os.makedirs(self.resumo_dir, exist_ok=True)
        
        # Contadores do dia atual
        self.mod_count_per_project: Dict[str, int] = {}
        self.total_modifications = 0
        self.current_day = date.today()
        
        logging.info(f"LogManager inicializado: {resumo_dir}")
        self.save_daily_summary()

    def register_modification(self, filepath: str) -> None:
        """
        Registra uma modificação no contador diário.
        
        Verifica se o dia mudou e, se necessário, salva o resumo anterior
        e reseta os contadores. Depois incrementa o contador do projeto.
        
        Args:
            filepath (str): Caminho do arquivo modificado
        """
        today = date.today()
        
        # Se mudou de dia, salva resumo anterior e reseta contadores
        if today != self.current_day:
            self.save_daily_summary()
            self.mod_count_per_project.clear()
            self.total_modifications = 0
            self.current_day = today
        
        # Incrementa contadores
        filename = os.path.basename(filepath)
        name_only, _ = os.path.splitext(filename)
        
        self.total_modifications += 1
        self.mod_count_per_project[name_only] = \
            self.mod_count_per_project.get(name_only, 0) + 1

    def save_daily_summary(self) -> None:
        """
        Salva um resumo diário com estatísticas das modificações.
        
        Gera arquivo de texto contendo:
        - Total de modificações do dia
        - Número de projetos diferentes modificados
        - Lista detalhada com contagem por projeto
        """
        try:
            today_str = self.current_day.strftime("%Y%m%d")
            resumo_path = os.path.join(self.resumo_dir, f"resumo_{today_str}.txt")
            
            total_projects = len(self.mod_count_per_project)
            
            # Monta conteúdo do resumo
            lines = [
                f"{'='*60}\n",
                f"RESUMO DE MONITORAMENTO - {self.current_day.strftime('%d/%m/%Y')}\n",
                f"{'='*60}\n\n",
                f"1. TOTAL DE MODIFICAÇÕES: {self.total_modifications}\n",
                f"   Número de alterações realizadas no diretório monitorado.\n\n",
                f"2. PROJETOS MODIFICADOS: {total_projects}\n",
                f"   Quantidade de projetos diferentes que sofreram alterações.\n\n",
                f"3. DETALHAMENTO POR PROJETO:\n",
                f"{'-'*60}\n"
            ]
            
            # Adiciona lista de projetos ordenada
            for proj in sorted(self.mod_count_per_project.keys()):
                count = self.mod_count_per_project[proj]
                lines.append(f"   {proj:40} - {count:3} modificações\n")
            
            lines.append(f"{'-'*60}\n")
            lines.append(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # Escreve resumo em arquivo
            with open(resumo_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            logging.info(f"Resumo diário salvo: {resumo_path}")
            print(f"✓ Resumo salvo: {resumo_path}")
            
            self.cleanup_old_resumos()
            
        except Exception as e:
            logging.error(f"Erro ao salvar resumo diário: {e}")

    def cleanup_old_resumos(self) -> None:
        """
        Remove arquivos de resumo antigos mantendo apenas os mais recentes.
        
        Lista e ordena por data, removendo os mais antigos quando
        excedem o limite máximo de arquivos.
        """
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
            logging.error(f"Erro ao limpar resumos antigos: {e}")


# ============================================================================
# CAMADA 3: PROJECT MONITOR - Monitora eventos do sistema de arquivos
# ============================================================================

class ProjectMonitor(FileSystemEventHandler):
    """
    Monitora eventos do sistema de arquivos para arquivos .prj.
    
    Responsabilidades:
    - Capturar eventos de criação, modificação e exclusão de arquivos
    - Filtrar eventos duplicados muito próximos
    - Coordenar backup e registro de modificações
    - Registrar todas as ações em log
    """
    
    def __init__(self, backup_manager: BackupManager, log_manager: LogManager):
        """
        Inicializa o monitor de projetos.
        
        Args:
            backup_manager (BackupManager): Instância do gerenciador de backups
            log_manager (LogManager): Instância do gerenciador de logs
        """
        super().__init__()
        self.backup_manager = backup_manager
        self.log_manager = log_manager
        self.last_events: Dict[str, float] = {}  # Rastreia último evento por arquivo
        logging.info("ProjectMonitor inicializado")

    def process_event(self, event, action: str) -> None:
        """
        Processa um evento do sistema de arquivos.
        
        Valida se o evento é relevante (arquivo .prj), filtra
        duplicatas próximas e coordena as ações apropriadas.
        
        Args:
            event: Evento capturado pelo watchdog
            action (str): Tipo de ação (CRIADO, MODIFICADO, DELETADO)
        """
        # Valida se é arquivo .txt
        if event.is_directory or not event.src_path.endswith('.txt'):
            return
        
        # Filtra eventos duplicados muito próximos (menos de 5 segundos)
        now = time.time()
        last_time = self.last_events.get(event.src_path, 0)
        if now - last_time < 5:
            return
        self.last_events[event.src_path] = now
        
        # Registra a ação
        user = getpass.getuser()
        message = f"[{action}] {os.path.basename(event.src_path)} | Usuário: {user}"
        logging.info(message)
        print(f"  {message}")
        
        # Executa ações específicas
        if action in ("MODIFICADO", "CRIADO"):
            self.backup_manager.create_backup(event.src_path)
            self.log_manager.register_modification(event.src_path)

    def on_modified(self, event):
        """Capturado quando arquivo é modificado."""
        self.process_event(event, "MODIFICADO")

    def on_created(self, event):
        """Capturado quando arquivo é criado."""
        self.process_event(event, "CRIADO")

    def on_deleted(self, event):
        """Capturado quando arquivo é deletado."""
        self.process_event(event, "DELETADO")


# ============================================================================
# CAMADA 4: INICIALIZAÇÃO E EXECUÇÃO
# ============================================================================

def setup_logging(log_file: str = 'monitor_prj.log') -> None:
    """
    Configura o sistema de logging.
    
    Args:
        log_file (str): Arquivo onde será gravado o log
    """
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info("="*70)
    logging.info("SISTEMA DE MONITORAMENTO INICIADO")
    logging.info("="*70)


def main():
    """
    Função principal que inicializa e executa o monitoramento.
    
    Configura:
    1. Diretórios de monitoramento, backup e logs
    2. Sistema de logging
    3. Gerenciadores de backup e logs
    4. Monitor de projetos
    5. Observer do watchdog
    """
    # Configuração de caminhos (AJUSTE CONFORME NECESSÁRIO)
    path_to_watch = r"C:/Users/Júlia/Desktop/Teste/BKPS Elipse/ESS/EnergisaSulSudeste_180225"
    backup_dir = r"C:/Users/Júlia/Desktop/Teste/Temp/Logs Monitor"
    resumo_dir = os.path.join(backup_dir, "Logs Resumo")
    
    # Cria diretórios se não existirem
    os.makedirs(backup_dir, exist_ok=True)
    os.makedirs(resumo_dir, exist_ok=True)
    
    # Configura logging
    setup_logging()
    
    try:
        # Inicializa gerenciadores
        backup_mgr = BackupManager(backup_dir=backup_dir, max_backups=10)
        log_mgr = LogManager(resumo_dir=resumo_dir, max_resumo_files=30)
        
        # Inicializa monitor
        monitor = ProjectMonitor(backup_mgr, log_mgr)
        
        # Configura observer
        observer = Observer()
        observer.schedule(monitor, path=path_to_watch, recursive=True)
        observer.start()
        
        print("\n" + "="*70)
        print("MONITORAMENTO DE PROJETOS INICIADO")
        print("="*70)
        print(f"Diretório: {path_to_watch}")
        print(f"Backups em: {backup_dir}")
        print(f"Resumos em: {resumo_dir}")
        print("Pressione Ctrl+C para parar...")
        print("="*70 + "\n")
        
        logging.info(f"Monitorando: {path_to_watch}")
        
        # Loop principal
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nParando monitoramento...")
        log_mgr.save_daily_summary()
        observer.stop()
        logging.info("Monitoramento interrompido pelo usuário")
        print("✓ Resumo final salvo. Até logo!")
        
    except Exception as e:
        logging.error(f"Erro crítico: {e}")
        print(f"✗ Erro: {e}")
        
    finally:
        observer.join()


if __name__ == "__main__":
    main()