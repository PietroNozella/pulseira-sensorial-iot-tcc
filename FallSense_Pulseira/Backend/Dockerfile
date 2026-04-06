## 1. Pega um Linux bem leve com Python já instalado
FROM python:3.10-slim
 
# 2. Cria uma pasta chamada /app dentro do servidor
WORKDIR /app
 
# 3. Copia o seu requirements.txt para o servidor e instala tudo
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
# 4. Copia todos os arquivos do seu backend para dentro do servidor
COPY . .
 
# 5. Avisa o Google que nossa API vai funcionar na porta 8080
EXPOSE 8080
 
# 6. O comando que liga a API (igual você faz no seu PC, mas na porta 8080)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]