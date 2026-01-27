# 1. Base Image: light Python 3.11 Slim version (minimize os size)
FROM python:3.11-slim

# 2. set working directory
WORKDIR /app

# 3. install dependencies (use cache by copying requirements.txt first)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. copy app source code
COPY . .

# 5. open Streamlit port
EXPOSE 8501

# 6. execute command (including Healthcheck settings)
# needs --server.address=0.0.0.0 option to allow external (outside container) access
CMD ["streamlit", "run", "main.py", "--server.address=0.0.0.0"]