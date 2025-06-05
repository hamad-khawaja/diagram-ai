FROM python:3.9-alpine as builder

# Install build dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev build-base graphviz-dev

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt

# Copy only installed packages
FROM python:3.9-alpine

RUN apk add --no-cache graphviz

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

EXPOSE 8501 8080

COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]
