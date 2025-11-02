#!/bin/bash

CONFIG_DIR="/etc"
SERVICE_NAME="backupd"
CONFIG_FILE="$CONFIG_DIR/backupd.yaml"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

case "$1" in
    start)
        sudo systemctl start $SERVICE_NAME
        echo "Демон запущен"
        ;;
    stop)
        sudo systemctl stop $SERVICE_NAME
        echo "Демон остановлен"
        ;;
    restart)
        sudo systemctl restart $SERVICE_NAME
        echo "Демон перезапущен"
        ;;
    enable)
        sudo systemctl enable $SERVICE_NAME
        echo "Демон добавлен в автозагрузку"
        ;;
    disable)
        sudo systemctl disable $SERVICE_NAME
        echo "Демон удален из автозагрузки"
        ;;
    status)
        systemctl status $SERVICE_NAME
        ;;
    logs)
        journalctl -u $SERVICE_NAME -f
        ;;
    setup)
        # Создание каталога для копий
        mkdir -p /home/zyablyak/linux_and_functional_programming/daemon/copytest
        # Перезагрузка демона
        sudo systemctl daemon-reload
        echo "Настройка завершена"
        ;;
    clean)
        # Очистка резервных копий
        rm -rf /home/zyablyak/linux_and_functional_programming/daemon/copytest/*
        echo "Резервные копии очищены"
        ;;
    *)
        echo "Использование: $0 {start|stop|restart|enable|disable|status|logs|setup|clean}"
        exit 1
        ;;
esac