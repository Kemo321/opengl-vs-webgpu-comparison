#!/bin/bash
export DISPLAY=:99
export XDG_RUNTIME_DIR=/tmp

export LIBGL_ALWAYS_SOFTWARE=1
export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp.json

Xvfb :99 -screen 0 1280x720x24 &
sleep 2

echo "Starting benchmark series (Headless Mode)..."

python src/tools/run_benchmarks.py

echo "Benchmarks completed. Results saved to /app/reports/"