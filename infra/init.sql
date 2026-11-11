CREATE TABLE IF NOT EXISTS test_tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO test_tasks (title, description, status) VALUES
('Верификация сетевого взаимодействия', 'Проверка связи Frontend -> Backend -> PostgreSQL', 'completed'),
('Проверка динамического Ingress', 'Тестирование маршрутизации через Traefik Router', 'in_progress'),
('Автоматизированный smoke-тест', 'Прогон curl эндпоинта /health в CI/CD пайплайне', 'pending')
ON CONFLICT DO NOTHING;