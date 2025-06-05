FROM python:3.9-alpine

# Install runtime dependencies
RUN apk add --no-cache graphviz cairo-dev pango-dev ttf-freefont

# Install build dependencies, install Python deps, then remove build deps
COPY requirements.txt /tmp/requirements.txt
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev build-base linux-headers g++ \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && apk del .build-deps

WORKDIR /app

COPY . .

EXPOSE 5050

COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]
