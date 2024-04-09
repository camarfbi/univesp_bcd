# Use a imagem base do Python
FROM python:3.9-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o arquivo de requisitos e instale as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie o script Python para o contêiner
COPY test_schedule.py .

# Comando padrão para executar o script
CMD ["python", "test_schedule.py"]
