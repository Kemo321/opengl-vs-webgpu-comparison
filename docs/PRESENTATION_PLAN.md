# Final Presentation Outline (Issue #14)
**Project:** OpenGL vs WebGPU Performance Comparison (Topic 13)
**Team:** Tomasz Okoń, Marek Dzięcioł, Michał Gryglicki

## Slide 1: Title & Introduction
* Project Title
* Team members and roles (Tomasz: Architecture, Marek: OpenGL, Michał: WebGPU).
* The Goal: Compare the legacy state-machine API (OpenGL) with the modern, explicit API (WebGPU).

## Slide 2: Technical Foundation
* **Language:** Python (glfw, PyOpenGL, wgpu)
* **Features Implemented:** Perspective Camera, 3D Object Loading (OBJ), Phong Shading (2 light sources).
* **Advanced Technique:** GPU Instancing (`glDrawElementsInstanced` vs WebGPU Instance buffers).

## Slide 3: Test Scenarios & Methodology
Explain how the benchmark was conducted (Tomasz's contribution):
* **Scenario 1:** Baseline rendering (1 complex object).
* **Scenario 2:** Medium load (1,000 instanced objects).
* **Scenario 3:** Stress test (27,000 instanced objects).
* Metrics measured: FPS and average frame time (ms).

## Slide 4: Performance Results (The Charts)
* *[Insert Bar Chart here: FPS comparison across the 3 scenarios]*
* *[Insert Line Chart here: Frame time stability]*
* **Talking point:** Discuss which API handled the 27,000 instances better. Usually, WebGPU handles CPU-side command encoding faster, but raw GPU rasterization is similar.

## Slide 5: Developer Experience (GLSL vs WGSL)
* Highlight the differences (Marek & Michał's contribution).
* **OpenGL/GLSL:** Fast to prototype, implicit state, C-like.
* **WebGPU/WGSL:** High boilerplate, strict validation, explicit memory layouts (Rust-like).

## Slide 6: Visual Showcase & Conclusion
* *[Insert Screenshots or a short GIF of the application running]*
* Final verdict on which technology the team prefers for future projects.
* Q&A.