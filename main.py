"""
CAMADA 4: MAIN - INICIALIZAÇÃO E CONFIGURAÇÃO
Responsável por inicializar o sistema e executar o monitoramento
"""

import os
import time
import logging
from datetime import datetime
from watchdog.observers import Observer

from backup_manager import BackupManager
from log_manager import LogManager
from file_monitor import FileMonitor


def setup_logging(log_file: str = 'monitor_arquivos.log') -> None:
    """
    Configura o sistema de logging
    
    Args:
        log_file (str): Arquivo onde será gravado o log
    """
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info("=" * 80)
    logging.info("MONITORAMENTO DE MÚLTIPLOS ARQUIVOS INICIADO")
    logging.info("Extensões monitoradas: .dom, .prj, .xml, .lib, .txt")
    logging.info("=" * 80)


def main():
    """
    Função principal que inicializa e executa o monitoramento
    
    Configura:
    1. Diretórios de monitoramento, backup e logs
    2. Sistema de logging
    3. Gerenciadores de backup e logs
    4. Monitor de arquivos
    5. Observer do watchdog
    
    Extensões monitoradas: .dom, .prj, .xml, .lib, .txt
    """
    # ========================================================================
    # CONFIGURE SEUS CAMINHOS AQUI:
    # ========================================================================
    path_to_watch = r"C:/Users/Júlia/Desktop/Teste/monitor"
    backup_dir = r"C:/Users/Júlia/Desktop/Teste/b"
    resumo_dir = os.path.join(backup_dir, "Logs Resumo")
    log_consolidado_dir = os.path.join(backup_dir, "Logs Consolidados")
    backup_folder_dir = os.path.join(backup_dir, "Backups Pasta Monitorada")
    # ========================================================================
    
    # Inicializa observer ANTES de tudo para evitar UnboundLocalError
    observer = None
    
    try:
        # Cria diretórios
        os.makedirs(backup_dir, exist_ok=True)
        os.makedirs(resumo_dir, exist_ok=True)
        os.makedirs(log_consolidado_dir, exist_ok=True)
        os.makedirs(backup_folder_dir, exist_ok=True)
        
        # Configura logging
        setup_logging('monitor_arquivos.log')
        
        # ====================================================================
        # INICIALIZA CAMADAS
        # ====================================================================
        
        # Camada 1: Backup Manager
        backup_mgr = BackupManager(backup_dir=backup_dir, max_backups=10)
        
        # Camada 2: Log Manager
        log_mgr = LogManager(
            resumo_dir=resumo_dir, 
            log_dir=log_consolidado_dir,
            backup_folder_dir=backup_folder_dir,
            max_resumo_files=30
        )
        
        # Camada 3: File Monitor
        monitor = FileMonitor(backup_mgr, log_mgr)
        
        # ====================================================================
        # INICIA MONITORAMENTO
        # ====================================================================
        observer = Observer()
        observer.schedule(monitor, path=path_to_watch, recursive=True)
        observer.start()
        
        # Registra início
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_message = f"{timestamp} - Monitoramento iniciado em: {path_to_watch}"
        logging.info(start_message)
        
        # Mostra informações de inicialização
        print("\n" + "=" * 80)
        print("MONITORAMENTO DE ARQUIVOS INICIADO")
        print("=" * 80)
        print(f"Timestamp: {timestamp}")
        print(f"Diretório: {path_to_watch}")
        print(f"Extensões monitoradas: .dom, .prj, .xml, .lib, .txt")
        print(f"Backups em: {backup_dir}")
        print(f"Resumos em: {resumo_dir}")
        print(f"Logs consolidados em: {log_consolidado_dir}")
        print(f"Backups da pasta em: {backup_folder_dir}")
        print("Pressione Ctrl+C para parar...")
        print("=" * 80 + "\n")
        
        # ====================================================================
        # LOOP PRINCIPAL
        # ====================================================================
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        # ====================================================================
        # PARADA LIMPA (Ctrl+C)
        # ====================================================================
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n\n{timestamp} - Parando monitoramento...")
        
        # Salva logs antes de parar
        if observer and observer.is_alive():
            print(f"\n✓ Fazendo backup da pasta monitorada...")
            log_mgr.backup_monitored_folder(path_to_watch)
            log_mgr.save_daily_log()
            log_mgr.save_daily_summary()
            
            # Para o observer
            observer.stop()
            
            logging.info(f"{timestamp} - Monitoramento interrompido pelo usuário")
            print("✓ Backup da pasta, log consolidado e resumo final salvos. Até logo!")
        
    except Exception as e:
        # ====================================================================
        # TRATAMENTO DE ERROS
        # ====================================================================
        logging.error(f"Erro crítico: {e}")
        print(f"✗ Erro: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # ====================================================================
        # LIMPEZA FINAL
        # ====================================================================
        if observer:
            observer.join()


if __name__ == "__main__":
    main()