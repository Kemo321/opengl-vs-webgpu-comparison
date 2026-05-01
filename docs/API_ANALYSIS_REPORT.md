# API Analysis Report: OpenGL vs WebGPU

## 1. Code Organization and Architecture (Issue #12)
### OpenGL
* **State Machine:** OpenGL operates as a massive global state machine. Functions like `glBindVertexArray` or `glUseProgram` change the global state. This makes simple scripts easy to write but leads to spaghetti code in larger projects if the state isn't carefully managed.
* **Resource Creation:** Creating resources (VBO, VAO, EBO) involves generating IDs (`glGenBuffers`) and binding them to targets (`glBindBuffer`). It is highly implicit.
* **Validation:** OpenGL provides very little upfront validation. Errors usually occur silently or require querying `glGetError()`, making debugging difficult.

### WebGPU
* **Object-Oriented & Stateless:** WebGPU requires explicit creation of pipelines, bind groups, and command encoders. State is encapsulated within the `RenderPipeline`.
* **Resource Creation:** Resources are created explicitly via descriptors (e.g., `device.create_buffer()`). To map data to shaders, WebGPU uses `BindGroups` and `BindGroupLayouts`, which strictly define what data the shader expects.
* **Validation:** WebGPU performs heavy validation during the creation of pipelines and command encoding. If a buffer size doesn't match the shader signature, it throws an error immediately in Python/JS, long before the draw call.

## 2. Shaders: GLSL vs WGSL (Issue #13)
### GLSL (OpenGL)
* **Syntax:** C-like syntax. Very familiar to most graphics programmers.
* **Structure:** Vertex and Fragment shaders are often written as completely separate strings or files. Inputs and outputs are linked by variable names (e.g., `out vec3 FragPos;` in Vertex matches `in vec3 FragPos;` in Fragment).
* **Bindings:** Uniforms are queried dynamically at runtime using `glGetUniformLocation`.

### WGSL (WebGPU)
* **Syntax:** Rust-like syntax. Uses explicit type declarations (e.g., `vec3<f32>`, `mat4x4<f32>`).
* **Structure:** Vertex and Fragment shaders are usually housed in the same file. They communicate using strictly defined `structs` with `@location` decorators. 
* **Bindings:** Requires explicit `@group(X) @binding(Y)` decorators, which directly map to the `BindGroup` layout configured in the application code. This enforces strict memory alignment (e.g., 16-byte padding for structs).

## 3. Implementation Complexity Conclusion
While WebGPU requires significantly more boilerplate code to set up the initial rendering pipeline and bind groups, it provides a much safer and more predictable architecture for complex scenes. OpenGL is faster for prototyping but prone to silent state-leaking bugs.