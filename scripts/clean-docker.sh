#! /bin/bash

echo "Parando containers..."
sudo docker stop $(sudo docker ps -aq) 2>/dev/null

echo "Removendo containers..."
sudo docker rm $(sudo docker ps -aq) 2>/dev/null

echo "Removendo imagens..."
sudo docker rmi -f $(sudo docker images -aq) 2>/dev/null

echo "Limpando sistema..."
sudo docker system prune -a -f

echo "Limpeza concluída."
