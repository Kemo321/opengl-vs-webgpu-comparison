"""Module for analyzing source files and collecting simple complexity metrics.

This module inspects Python renderer source files to compute lines of code,
shader lines, API-specific calls, and resource creation occurrences. It
produces a CSV report with the results.
"""

import csv
import os
import re
from typing import Dict, List, Optional, Union


def analyze_file(filepath: str, api_name: str) -> Optional[Dict[str, Union[str, int]]]:
    """Analyze a single source file and return complexity metrics.

    The analysis counts non-empty non-comment lines, extracts shader blocks
    delimited by triple quotes, and detects API-specific calls and resource
    creation invocations using regular expressions.

    Args:
        filepath: Path to the file to analyze.
        api_name: Name of the API (e.g. "OpenGL" or "WebGPU") used to
            select API-specific detection patterns.

    Returns:
        A mapping with metric names as keys and their computed values, or
        None if the provided file path does not exist.
    """
    if not os.path.exists(filepath):
        return None

    with open(filepath, "r", encoding="utf-8") as fh:
        content: str = fh.read()

    # Count non-empty, non-comment Python lines
    lines: List[str] = content.split("\n")
    loc: int = len([
        line for line in lines if line.strip() and not line.strip().startswith("#")
    ])

    # Extract shader blocks enclosed in triple quotes and count their non-empty lines
    shaders: List[str] = re.findall(r'"""(.*?)"""', content, re.DOTALL)
    shader_loc: int = sum(len([line for line in s.split("\n") if line.strip()]) for s in shaders)

    # Count API-specific state calls and resource creation calls
    if api_name == "OpenGL":
        api_calls: int = len(re.findall(r"gl[A-Z][a-zA-Z0-9_]+", content))
        resource_creation: int = len(re.findall(r"glGen[A-Za-z]+", content))
    else:
        api_calls = len(re.findall(r"device\.[a-z_]+|pass_enc\.[a-z_]+", content))
        resource_creation = len(re.findall(r"create_(buffer|bind_group|pipeline|texture)", content))

    return {
        "API": api_name,
        "Total_Lines_of_Code": loc,
        "Shader_Lines_of_Code": shader_loc,
        "Python_Logic_Lines": loc - shader_loc,
        "API_State_Calls": api_calls,
        "Resource_Creation_Calls": resource_creation,
    }


def main() -> None:
    """Execute analysis for configured renderer files and emit a CSV report.

    The function analyzes the OpenGL and WebGPU renderer source files and
    writes a CSV report with a fixed set of fields.

    Returns:
        None
    """
    opengl_data: Optional[Dict[str, Union[str, int]]] = analyze_file(
        "../src/opengl/opengl_renderer.py", "OpenGL"
    )
    webgpu_data: Optional[Dict[str, Union[str, int]]] = analyze_file(
        "../src/webgpu/webgpu_renderer.py", "WebGPU"
    )

    results: List[Dict[str, Union[str, int]]] = [data for data in (opengl_data, webgpu_data) if data]

    csv_path: str = "../reports/complexity_report.csv"
    fieldnames: List[str] = [
        "API",
        "Total_Lines_of_Code",
        "Shader_Lines_of_Code",
        "Python_Logic_Lines",
        "API_State_Calls",
        "Resource_Creation_Calls",
    ]

    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer: csv.DictWriter = csv.DictWriter(csvfile, fieldnames=fieldnames)  # type: ignore[attr-defined]
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"Analysis complete. Report saved to: {csv_path}")


if __name__ == "__main__":
    main()
