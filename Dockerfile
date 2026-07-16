FROM python:3.12-slim

WORKDIR /app

# Системные зависимости для Playwright + Xvfb.
# xvfb и базовые либы ставим явно — они нужны независимо от версии
# Playwright. Остальные библиотеки Chrome (libnss3, libatk и т.п.)
# подтягиваются автоматически шагом `playwright install --with-deps`
# ниже — он сам знает точный список под установленную версию пакета,
# поэтому вручную их здесь не перечисляем (это раньше было хрупким
# местом: список менялся между версиями Playwright и легко рассинхронился
# бы с тем, что реально нужно).
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*


RUN apt-get update && apt-get install -y \
    xvfb \
    libnss3 libnspr4 libatk-bridge2.0-0 libatk1.0-0 libcups2 libdrm2 libdbus-1-3 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 \
    libpango-1.0-0 libcairo2 libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Зависимости Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Установка Chrome для Playwright + всех системных зависимостей под него.
# --with-deps делает то же самое, что раньше делал руками собранный список
# apt-get install — но всегда актуально для установленной версии playwright.
RUN playwright install --with-deps chrome

# Копируем приложение. .env НЕ копируется — см. .dockerignore.
# Секреты (OPENAI_API_KEY, пароли БД) передаются через environment в
# docker-compose.yml, а не зашиваются в слои образа.
COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
