FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN mkdir -p /tmp/runtime-root && chmod 0700 /tmp/runtime-root
ENV XDG_RUNTIME_DIR=/tmp/runtime-root

RUN apt-get update && apt-get install -y \
    xvfb \
    x11vnc \
    fluxbox \
    novnc \
    websockify \
    libgl1 \
    libglx-mesa0 \
    libegl1 \
    libglfw3 \
    mesa-utils \
    mesa-vulkan-drivers \
    libvulkan1 \
    vulkan-tools \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1

RUN ln -s /usr/share/novnc/vnc.html /usr/share/novnc/index.html

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]