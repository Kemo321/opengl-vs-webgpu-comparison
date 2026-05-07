import OpenGL.GL as gl
from OpenGL.GL.shaders import compileProgram, compileShader
from typing import Any, Dict, List, Optional
import numpy as np
import ctypes
from src.core.renderer import Renderer

"""OpenGL renderer implementation.

This module provides an OpenGL-based Renderer subclass that compiles
simple vertex/fragment shaders and renders instanced meshes using
vertex buffers, normal buffers and instance offset attributes.
"""

# Vertex shader: applies per-instance offset to vertex positions and
# outputs world position and normal to the fragment shader.
VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec3 aOffset; // per-instance translation

uniform mat4 view;
uniform mat4 projection;

out vec3 FragPos;
out vec3 Normal;

void main() {
    vec3 worldPos = aPos + aOffset;
    FragPos = worldPos;
    Normal = aNormal;
    gl_Position = projection * view * vec4(worldPos, 1.0);
}
"""

# Fragment shader: simple two-light Phong lighting model with ambient,
# diffuse and specular components. The shader expects two light
# positions/colors, the camera position (viewPos) and an object color.
FRAGMENT_SHADER = """
#version 330 core
out vec4 FragColor;

in vec3 FragPos;
in vec3 Normal;

uniform vec3 lightPos1;
uniform vec3 lightColor1;
uniform vec3 lightPos2;
uniform vec3 lightColor2;
uniform vec3 viewPos;
uniform vec3 objectColor;

vec3 CalcPhong(vec3 lPos, vec3 lColor, vec3 norm, vec3 viewDir) {
    float ambientStrength = 0.1;
    vec3 ambient = ambientStrength * lColor;

    vec3 lightDir = normalize(lPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lColor;

    float specularStrength = 0.5;
    vec3 reflectDir = reflect(-lightDir, norm);
    // FIX: use reflectDir for the specular calculation
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    vec3 specular = specularStrength * spec * lColor;

    return ambient + diffuse + specular;
}

void main() {
    vec3 norm = normalize(Normal);
    vec3 viewDir = normalize(viewPos - FragPos);

    vec3 result = CalcPhong(lightPos1, lightColor1, norm, viewDir);
    result += CalcPhong(lightPos2, lightColor2, norm, viewDir);

    FragColor = vec4(result * objectColor, 1.0);
}
"""


class OpenGLRenderer(Renderer):
    """Render scenes using a modern OpenGL shader pipeline."""

    def __init__(self) -> None:
        """Initialize renderer state.

        Returns:
            None.
        """
        self.shader: Optional[int] = None
        self.gpu_objects: List[Dict[str, Any]] = []

    def init_context(self, window: Any) -> None:
        """Initialize OpenGL state and compile the shader program.

        Args:
            window: Application window or context.

        Returns:
            None.
        """
        _ = window
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_FRAMEBUFFER_SRGB)
        gl.glClearColor(0.05, 0.05, 0.05, 1.0)

        # Create a temporary VAO for shader validation (required by modern OpenGL)
        temp_vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(temp_vao)

        self.shader = compileProgram(
            compileShader(VERTEX_SHADER, gl.GL_VERTEX_SHADER),
            compileShader(FRAGMENT_SHADER, gl.GL_FRAGMENT_SHADER),
        )

        # Clean up temporary VAO
        gl.glBindVertexArray(0)
        gl.glDeleteBuffers(1, [temp_vao])

    def _prepare_buffers(self, scene_obj: Any) -> None:
        """Create GPU buffers and configure vertex attributes.

        Args:
            scene_obj: Scene object with mesh data and instance offsets.

        Returns:
            None.
        """
        mesh = scene_obj.mesh
        vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(vao)

        vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, mesh.vertices.nbytes, mesh.vertices, gl.GL_STATIC_DRAW
        )
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(0)

        nbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, nbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, mesh.normals.nbytes, mesh.normals, gl.GL_STATIC_DRAW
        )
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(1)

        offsets = np.array(
            [o.to_list() for o in scene_obj.instance_offsets], dtype=np.float32
        ).flatten()
        ibo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, ibo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, offsets.nbytes, offsets, gl.GL_STATIC_DRAW)
        gl.glVertexAttribPointer(2, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(2)
        gl.glVertexAttribDivisor(2, 1)

        ebo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)
        gl.glBufferData(
            gl.GL_ELEMENT_ARRAY_BUFFER, mesh.indices.nbytes, mesh.indices, gl.GL_STATIC_DRAW
        )

        gl.glBindVertexArray(0)

        self.gpu_objects.append(
            {
                "vao": vao,
                "index_count": len(mesh.indices),
                "instance_count": len(scene_obj.instance_offsets),
                "color": scene_obj.color,
            }
        )

    def render_frame(self, scene: Any, camera: Any) -> None:
        """Render a single frame.

        Args:
            scene: Scene containing objects and lights.
            camera: Active camera providing view and projection matrices.

        Returns:
            None.
        """
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glUseProgram(self.shader)

        view = np.array(camera.get_view_matrix(), dtype=np.float32)
        proj = np.array(camera.get_projection_matrix(), dtype=np.float32)

        gl.glUniformMatrix4fv(gl.glGetUniformLocation(self.shader, "view"), 1, gl.GL_TRUE, view)
        gl.glUniformMatrix4fv(
            gl.glGetUniformLocation(self.shader, "projection"), 1, gl.GL_TRUE, proj
        )
        gl.glUniform3fv(
            gl.glGetUniformLocation(self.shader, "viewPos"),
            1,
            np.array(camera.position, dtype=np.float32),
        )

        if len(scene.lights) >= 2:
            for i, light in enumerate(scene.lights[:2]):
                gl.glUniform3fv(
                    gl.glGetUniformLocation(self.shader, f"lightPos{i+1}"),
                    1,
                    np.array(light.position, dtype=np.float32),
                )
                gl.glUniform3fv(
                    gl.glGetUniformLocation(self.shader, f"lightColor{i+1}"),
                    1,
                    np.array(light.color, dtype=np.float32),
                )

        if not self.gpu_objects:
            for obj in scene.objects:
                self._prepare_buffers(obj)

        obj_color_loc = gl.glGetUniformLocation(self.shader, "objectColor")

        for gpu_obj in self.gpu_objects:
            gl.glUniform3fv(obj_color_loc, 1, np.array(gpu_obj["color"], dtype=np.float32))
            gl.glBindVertexArray(gpu_obj["vao"])
            gl.glDrawElementsInstanced(
                gl.GL_TRIANGLES,
                gpu_obj["index_count"],
                gl.GL_UNSIGNED_INT,
                None,
                gpu_obj["instance_count"],
            )
            gl.glBindVertexArray(0)

    def cleanup(self) -> None:
        """Release renderer resources.

        Returns:
            None.
        """
        pass
