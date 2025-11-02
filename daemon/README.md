# Демон резервного копирования

Системный демон для автоматического резервного копирования данных.

# Даем права на выполнение
chmod +x backup_manager.sh
chmod +x backupd.py

# Использование менеджера
./backup_manager.sh setup    # Настройка
./backup_manager.sh enable   # Включить автозагрузку
./backup_manager.sh start    # Запустить
./backup_manager.sh status   # Проверить статус
./backup_manager.sh logs     # Просмотреть логи
./backup_manager.sh stop     # Остановить

# Ручной запуск для тестирования
python3 backupd.py