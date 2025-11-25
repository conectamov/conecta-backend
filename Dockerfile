FROM python:3.11
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      pkg-config \
      python3-dev \
      libdbus-1-dev \
      dbus \                     
      dbus-user-session \
      libdbus-glib-1-dev \
      libglib2.0-dev \
      meson \
      ninja-build \
      cmake \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["sh", "/entrypoint.sh"]

CMD ["sh", "-c", "exec gunicorn -w 4 -b 0.0.0.0:8080 app:app"]
