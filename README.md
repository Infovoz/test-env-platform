# Инфраструктура для автоматического развертывания тестовых сред разработчиков

Курсовая работа по дисциплине «Настройка и администрирование сервисного программного обеспечения»  
Кафедра ИиППО, РТУ МИРЭА.

## Архитектура системы
Проект реализует инфраструктуру динамических тестовых сред на базе Docker Swarm:
1. `registry` — локальный реестр Docker образов (порт 5000).
2. `traefik` — динамический пограничный маршрутизатор (порты 80, 8080).
3. `db` — СУБД PostgreSQL 16 с предзагруженными тестовыми данными.
4. `backend` — REST API на FastAPI (порт 8000) с healthcheck-эндпоинтом.
5. `frontend` — веб-интерфейс панели управления на базе Nginx Alpine.

## Команды запуска
```bash
docker swarm init
docker run -d -p 5000:5000 --restart=always --name registry registry:2
docker build -t 127.0.0.1:5000/testenv-backend:latest ./backend
docker build -t 127.0.0.1:5000/testenv-frontend:latest ./frontend
docker push 127.0.0.1:5000/testenv-backend:latest
docker push 127.0.0.1:5000/testenv-frontend:latest
docker stack deploy -c docker-compose.yml testenv