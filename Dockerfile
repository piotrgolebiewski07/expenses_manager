FROM python:3.11-slim

WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy application code
COPY . .

# fix line endings and allow start script execution
RUN apt-get update && apt-get install -y dos2unix \
    && dos2unix start.sh \
    && chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]

