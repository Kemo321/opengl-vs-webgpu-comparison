#!/bin/bash

export DISPLAY=:99
export XDG_RUNTIME_DIR=/tmp

export LIBGL_ALWAYS_SOFTWARE=1
export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp.json

Xvfb :99 -screen 0 ${WINDOW_WIDTH:-1280}x${WINDOW_HEIGHT:-720}x24 &
sleep 1

fluxbox &

x11vnc -display :99 -nopw -forever -shared -bg

websockify --web /usr/share/novnc/ 8080 localhost:5900 &

echo "==================================================="
echo "Container ready!"
echo "Open in your browser: http://localhost:8080"
echo "Starting: API=${API_TYPE}, Scenario=${SCENARIO}"
echo "==================================================="

python main.py \
    --api ${API_TYPE:-webgpu} \
    --scenario ${SCENARIO:-3} \
    --width ${WINDOW_WIDTH:-1280} \
    --height ${WINDOW_HEIGHT:-720}

tail -f /dev/null