FROM python:3.11-slim

WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy application code
COPY . .

# allow start script execution
RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]

