import os
import time
import yaml
import shutil
import logging
import signal
import sys
from datetime import datetime
from pathlib import Path

CONFIG_PATH = "/etc/backupd.yaml"
DEFAULT_CONFIG = {
    "source_dir": "/home/zyablyak/linux_and_functional_programming/daemon/test",
    "backup_dir": "/home/zyablyak/linux_and_functional_programming/daemon/copytest",
    "interval_minutes": 1,
    "log_file": "/var/log/backupd.log",
    "max_backups": 10
}
running = True


def signal_handler(signum, frame):
    """Обработчик сигналов остановки"""
    global running
    logging.info("Получен сигнал остановки. Завершение работы...")
    running = False


def setup_signal_handlers():
    """Настройка обработчиков сигналов для graceful shutdown"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def create_default_config():
    """Создание конфигурационного файла по умолчанию"""
    try:
        with open(CONFIG_PATH, 'w') as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False)
        logging.info(f"Создан конфигурационный файл: {CONFIG_PATH}")
        return True
    except Exception as e:
        logging.error(f"Ошибка создания конфигурации: {e}")
        return False


def load_config():
    """Загрузка конфигурации"""
    if not os.path.exists(CONFIG_PATH):
        logging.warning(f"Конфигурационный файл не найден: {CONFIG_PATH}")
        if not create_default_config():
            return None
    
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = yaml.safe_load(f)

        required = ['source_dir', 'backup_dir', 'interval_minutes']
        for param in required:
            if param not in config:
                logging.error(f"Отсутствует обязательный параметр: {param}")
                return None
        
        return config
    except Exception as e:
        logging.error(f"Ошибка загрузки конфигурации: {e}")
        return None


def setup_logging(log_path):
    """Настройка логирования"""
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    except Exception as e:
        print(f"Ошибка настройки логирования: {e}")
        sys.exit(1)

def cleanup_old_backups(backup_dir, max_backups):
    """Удаление старых резервных копий"""
    try:
        backups = sorted(Path(backup_dir).glob("backup-*"))
        
        if len(backups) > max_backups:
            for old_backup in backups[:-max_backups]:
                shutil.rmtree(old_backup)
                logging.info(f"Удалена старая резервная копия: {old_backup}")
                
        logging.info(f"Текущее количество резервных копий: {len(backups)} (максимум: {max_backups})")
        
    except Exception as e:
        logging.error(f"Ошибка очистки старых резервных копий: {e}")


def create_backup(source, destination):
    """Создание резервной копии"""
    try:
        if not os.path.exists(source):
            logging.error(f"Исходная директория не найдена: {source}")
            return False

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = os.path.join(destination, f"backup-{timestamp}")

        os.makedirs(destination, exist_ok=True)
        
        shutil.copytree(source, backup_path)
        logging.info(f"Успешно создана резервная копия: {backup_path}")
        return True
        
    except Exception as e:
        logging.error(f"Ошибка при создании резервной копии: {e}")
        return False


def run_daemon():
    """Основной цикл демона"""
    global running
    
    config = load_config()
    if not config:
        logging.error("Не удалось загрузить конфигурацию. Завершение работы.")
        return
    
    source = config["source_dir"]
    destination = config["backup_dir"]
    interval = config["interval_minutes"]
    log_file = config["log_file"]
    max_backups = config["max_backups"]
    
    setup_logging(log_file)
    
    logging.info("=== Демон резервного копирования запущен ===")
    logging.info(f"Источник: {source}")
    logging.info(f"Каталог для резервных копий: {destination}")
    logging.info(f"Интервал копирования: {interval} мин.")
    logging.info(f"Максимум резервных копий: {max_backups}")
    
    while running:
        if create_backup(source, destination):
            cleanup_old_backups(destination, max_backups)

        for _ in range(interval * 60):
            if not running:
                break
            time.sleep(1)
    
    logging.info("=== Демон резервного копирования остановлен ===")


if __name__ == "__main__":
    setup_signal_handlers()
    run_daemon()