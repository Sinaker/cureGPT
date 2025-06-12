FROM python:3.12-slim
WORKDIR /curegpt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Command to run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "wsgi:app"]