# FROM python:3.11-slim
# WORKDIR /app
# COPY requirements.txt .
# # RUN pip install -r requirements.txt
# # RUN pip install --default-timeout=200000 -r requirements.txt
# RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
# COPY . .
# EXPOSE 8000
# CMD ["python", "app.py"]

FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Download SpaCy model
RUN python -m spacy download en_core_web_sm

# Copy project files
COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
