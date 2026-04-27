# OpenGL vs WebGPU: 3D Renderer Comparison

## Project Overview
This project is a comparative analysis of two graphics APIs: **OpenGL** and **WebGPU**. We are developing two parallel rendering engines to achieve identical visual results while evaluating performance metrics and implementation workflows.

Developed as part of the **Computer Graphics** course at the Warsaw University of Technology.

## Technical Requirements
To ensure a fair comparison, both implementations include:
* **Identical Scene:** Rendering basic primitives or 3D models (OBJ/GLTF).
* **Camera System:** Perspective camera with full movement and rotation control.
* **Lighting Model:** Phong shading with a minimum of two light sources.
* **Transformations:** Support for object translation, rotation, and scaling.
* **Additional Technique:** Implementation of *[Instancing / Post-processing / Billboarding]* in both versions.

## Benchmarking & Analysis
The core of this project is a performance comparison based on:
* **FPS & Frame Time:** Real-time monitoring of average rendering speeds.
* **Scenarios:** Comparison across at least 3 different test scenes.
* **Implementation Study:** Detailed analysis of resource creation, shader preparation (GLSL vs WGSL), and code complexity.

## Project Milestones
* **Phase 1 (May 5, 2026):** Basic window implementation, shading, and object loading.
* **Phase 2 (June 9, 2026):** Final version with all features and performance analysis.

## Built With
* **Language:** Python or C++ (OpenGL & WebGPU)
* **Shaders:** GLSL & WGSL

## Development Team
* **Marek Dzięcioł**
* **Michał Gryglicki**
* **Tomasz Okoń**
