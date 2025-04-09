FROM python:3.9

WORKDIR /app

# Копируем все файлы в контейнер
COPY . /app/
COPY wait-for-mysql.sh /app/
RUN chmod +x /app/wait-for-mysql.sh

# Устанавливаем mysql-client
RUN apt-get update && \
    apt-get install -y default-mysql-client && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт 8000
EXPOSE 8000

# Запускаем Django сервер после того, как MySQL будет готов
CMD ["./wait-for-mysql.sh", "python", "/app/manage.py", "migrate", "&&", "python", "/app/manage.py", "createsuperuser", "--noinput", "--username", "admin", "--email", "admin@example.com", "&&", "python", "/app/manage.py", "runserver", "0.0.0.0:8000"]
