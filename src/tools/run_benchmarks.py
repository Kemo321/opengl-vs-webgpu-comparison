"""Automated benchmark runner for OpenGL vs WebGPU comparison.

This module runs the project's main.py with different API and scenario
combinations, captures benchmark output lines that start with
"BENCHMARK_RESULT" and stores the aggregated results into a CSV file.

The module does not change benchmark logic; it only orchestrates process
invocation and result collection.
"""

import os
from typing import List, Dict, Any
import subprocess
import csv
import sys

# Benchmark configuration
APIS: List[str] = ["opengl", "webgpu"]
SCENARIOS: List[int] = [1, 2, 3]
FRAMES_TO_RENDER: int = 500
# Use the current Python interpreter (e.g. active venv)
PYTHON_EXEC: str = sys.executable


def run_benchmarks() -> None:
    """Run automated benchmarks and write results to a CSV file.

    The function invokes main.py for each API and scenario, parses any
    lines that begin with the special tag "BENCHMARK_RESULT" and collects
    the reported average FPS and average frame time.

    Args:
        None

    Returns:
        None: Results are written to a CSV file in the current working
        directory.
    """

    results: List[Dict[str, Any]] = []

    print(f"Starting automated benchmarks (frames per test: {FRAMES_TO_RENDER})...\n")

    for api in APIS:
        for scenario in SCENARIOS:
            print(f"Testing: API = {api.upper()}, Scenario = {scenario}...", end="", flush=True)

            # Build the command to execute the project's main entrypoint.
            # Use a relative path to main.py assuming execution from repo root.
            cmd: List[str] = [
                PYTHON_EXEC, "main.py",
                "--api", api,
                "--scenario", str(scenario),
                "--benchmark-frames", str(FRAMES_TO_RENDER),
            ]

            try:
                # Execute subprocess and capture combined stdout/stderr as text.
                output: str = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)

                # Search for lines prefixed with BENCHMARK_RESULT and parse them.
                for line in output.split("\n"):
                    if line.startswith("BENCHMARK_RESULT"):
                        _, res_api, res_scenario, avg_fps, avg_time = line.split(",")
                        results.append({
                            "API": res_api.upper(),
                            "Scenariusz": res_scenario,
                            "Srednie_FPS": float(avg_fps),
                            "Sredni_Czas_Klatki_ms": float(avg_time),
                        })
                        print(f" DONE ({avg_fps} FPS)")
                        break
            except subprocess.CalledProcessError as e:
                # Report subprocess error output for debugging.
                print(" ERROR!")
                print(e.output)

    # Persist results to CSV.
    csv_file: str = "./reports/performance_results.csv"

    os.makedirs(os.path.dirname(csv_file), exist_ok=True)
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["API", "Scenariusz", "Srednie_FPS", "Sredni_Czas_Klatki_ms"])
        writer.writeheader()
        writer.writerows(results)

    print(f"\nDone! Results written to: {csv_file}")
    print("You can now open it in Excel to generate charts for section 5.")


if __name__ == "__main__":
    run_benchmarks()
