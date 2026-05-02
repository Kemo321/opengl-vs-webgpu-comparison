import wgpu
import numpy as np
from typing import Any, Dict, List, Optional
from src.core.renderer import Renderer

WGSL_SHADER = """
struct FrameUniforms {
    view_proj: mat4x4<f32>,
    view_pos: vec4<f32>,
    light1_pos: vec4<f32>,
    light1_color: vec4<f32>,
    light2_pos: vec4<f32>,
    light2_color: vec4<f32>,
};
@group(0) @binding(0) var<uniform> frame_uniforms: FrameUniforms;

struct ObjectUniforms {
    object_color: vec4<f32>,
};
@group(1) @binding(0) var<uniform> object_uniforms: ObjectUniforms;

struct VertexInput {
    @location(0) position: vec3<f32>,
    @location(1) normal: vec3<f32>,
    @location(2) instance_offset: vec3<f32>,
};

struct VertexOutput {
    @builtin(position) clip_position: vec4<f32>,
    @location(0) frag_pos: vec3<f32>,
    @location(1) normal: vec3<f32>,
};

@vertex
fn vs_main(model: VertexInput) -> VertexOutput {
    var out: VertexOutput;
    let world_pos = model.position + model.instance_offset;
    out.frag_pos = world_pos;
    out.normal = model.normal;
    out.clip_position = frame_uniforms.view_proj * vec4<f32>(world_pos, 1.0);
    return out;
}

fn calc_phong(l_pos: vec3<f32>, l_color: vec3<f32>, norm: vec3<f32>, view_dir: vec3<f32>, frag_pos: vec3<f32>) -> vec3<f32> {
    let ambient = 0.1 * l_color;
    let light_dir = normalize(l_pos - frag_pos);
    let diff = max(dot(norm, light_dir), 0.0);
    let diffuse = diff * l_color;
    let reflect_dir = reflect(-light_dir, norm);
    let spec = pow(max(dot(view_dir, reflect_dir), 0.0), 32.0);
    let specular = 0.5 * spec * l_color;
    return ambient + diffuse + specular;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    let norm = normalize(in.normal);
    let view_dir = normalize(frame_uniforms.view_pos.xyz - in.frag_pos);

    var result = calc_phong(frame_uniforms.light1_pos.xyz, frame_uniforms.light1_color.xyz, norm, view_dir, in.frag_pos);
    result += calc_phong(frame_uniforms.light2_pos.xyz, frame_uniforms.light2_color.xyz, norm, view_dir, in.frag_pos);

    // Używamy koloru z dedykowanej dla obiektu grupy
    return vec4<f32>(result * object_uniforms.object_color.xyz, 1.0);
}
"""


class WebGPURenderer(Renderer):
    """WebGPU-based renderer implementing the Renderer interface.

    This class manages GPU resources, pipeline creation and per-frame rendering
    using the wgpu-python API.
    """

    def __init__(self) -> None:
        """Initialize internal state references for GPU resources.

        Attributes are initialized to None and populated during context
        initialization and buffer preparation.
        """
        self.device: Optional[Any] = None
        self.present_context: Optional[Any] = None
        self.pipeline: Optional[Any] = None
        self.gpu_objects: List[Dict[str, Any]] = []

        self.frame_buffer: Optional[Any] = None
        self.bg_frame: Optional[Any] = None
        self.bg_layout_obj: Optional[Any] = None

        self.depth_texture: Optional[Any] = None
        self.depth_view: Optional[Any] = None

    def init_context(self, window_canvas: Any) -> None:
        """Initialize GPU device, swap chain configuration and rendering pipeline.

        Args:
            window_canvas: Platform-specific canvas object exposing get_context()
                used to obtain the presentation context.

        Returns:
            None
        """
        adapter = wgpu.gpu.request_adapter(power_preference="high-performance")
        self.device = adapter.request_device()

        self.present_context = window_canvas.get_context("webgpu")
        self.present_format = self.present_context.get_preferred_format(adapter)
        self.present_context.configure(device=self.device, format=self.present_format)

        shader = self.device.create_shader_module(code=WGSL_SHADER)

        # Main scene uniform buffer (144 bytes)
        self.frame_buffer = self.device.create_buffer(
            size=144, usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST
        )

        # Bind group layouts: group 0 = scene/frame, group 1 = per-object
        bg_layout_frame = self.device.create_bind_group_layout(
            entries=[
                {
                    "binding": 0,
                    "visibility": wgpu.ShaderStage.VERTEX | wgpu.ShaderStage.FRAGMENT,
                    "buffer": {"type": wgpu.BufferBindingType.uniform},
                }
            ]
        )
        self.bg_layout_obj = self.device.create_bind_group_layout(
            entries=[
                {
                    "binding": 0,
                    "visibility": wgpu.ShaderStage.FRAGMENT,
                    "buffer": {"type": wgpu.BufferBindingType.uniform},
                }
            ]
        )

        # Bind group for the global frame uniforms
        self.bg_frame = self.device.create_bind_group(
            layout=bg_layout_frame,
            entries=[
                {
                    "binding": 0,
                    "resource": {"buffer": self.frame_buffer, "offset": 0, "size": 144},
                }
            ],
        )

        pipeline_layout = self.device.create_pipeline_layout(
            bind_group_layouts=[bg_layout_frame, self.bg_layout_obj]
        )

        vertex_buffers = [
            {
                "array_stride": 12,
                "step_mode": wgpu.VertexStepMode.vertex,
                "attributes": [
                    {
                        "format": wgpu.VertexFormat.float32x3,
                        "offset": 0,
                        "shader_location": 0,
                    }
                ],
            },
            {
                "array_stride": 12,
                "step_mode": wgpu.VertexStepMode.vertex,
                "attributes": [
                    {
                        "format": wgpu.VertexFormat.float32x3,
                        "offset": 0,
                        "shader_location": 1,
                    }
                ],
            },
            {
                "array_stride": 12,
                "step_mode": wgpu.VertexStepMode.instance,
                "attributes": [
                    {
                        "format": wgpu.VertexFormat.float32x3,
                        "offset": 0,
                        "shader_location": 2,
                    }
                ],
            },
        ]

        self.pipeline = self.device.create_render_pipeline(
            layout=pipeline_layout,
            vertex={
                "module": shader,
                "entry_point": "vs_main",
                "buffers": vertex_buffers,
            },
            fragment={
                "module": shader,
                "entry_point": "fs_main",
                "targets": [{"format": self.present_format}],
            },
            primitive={"topology": wgpu.PrimitiveTopology.triangle_list},
            depth_stencil={
                "format": wgpu.TextureFormat.depth24plus,
                "depth_write_enabled": True,
                "depth_compare": wgpu.CompareFunction.less,
            },
        )

    def _prepare_buffers(self, scene_obj: Any) -> None:
        """Create GPU buffers and a per-object bind group for a scene object.

        Args:
            scene_obj: Object containing mesh, color and instance_offsets attributes.

        Returns:
            None
        """
        mesh = scene_obj.mesh
        vbo = self.device.create_buffer_with_data(
            data=mesh.vertices, usage=wgpu.BufferUsage.VERTEX
        )
        nbo = self.device.create_buffer_with_data(
            data=mesh.normals, usage=wgpu.BufferUsage.VERTEX
        )

        offsets = np.array(
            [o.to_list() for o in scene_obj.instance_offsets], dtype=np.float32
        ).flatten()
        ibo = self.device.create_buffer_with_data(
            data=offsets, usage=wgpu.BufferUsage.VERTEX
        )
        ebo = self.device.create_buffer_with_data(
            data=mesh.indices, usage=wgpu.BufferUsage.INDEX
        )

        # Create a small uniform buffer holding the object's color and a bind group
        color_data = np.array(
            [scene_obj.color.x, scene_obj.color.y, scene_obj.color.z, 1.0],
            dtype=np.float32,
        ).tobytes()
        color_buf = self.device.create_buffer_with_data(
            data=color_data, usage=wgpu.BufferUsage.UNIFORM
        )

        bg_obj = self.device.create_bind_group(
            layout=self.bg_layout_obj,
            entries=[
                {
                    "binding": 0,
                    "resource": {"buffer": color_buf, "offset": 0, "size": 16},
                }
            ],
        )

        self.gpu_objects.append(
            {
                "vbo": vbo,
                "nbo": nbo,
                "ibo": ibo,
                "ebo": ebo,
                "index_count": len(mesh.indices),
                "instance_count": len(scene_obj.instance_offsets),
                "bg_obj": bg_obj,
            }
        )

    def render_frame(self, scene: Any, camera: Any) -> None:
        """Render a single frame for the provided scene and camera.

        Args:
            scene: Scene object containing lights and objects lists.
            camera: Camera object exposing projection and view matrix accessors
                and a position attribute.

        Returns:
            None
        """
        if not scene.lights:
            return

        current_texture = self.present_context.get_current_texture()
        color_view = current_texture.create_view()

        # Ensure depth texture matches the current render target size
        if (
            self.depth_texture is None
            or self.depth_texture.size[0] != current_texture.size[0]
            or self.depth_texture.size[1] != current_texture.size[1]
        ):
            self.depth_texture = self.device.create_texture(
                size=[current_texture.size[0], current_texture.size[1], 1],
                format=wgpu.TextureFormat.depth24plus,
                usage=wgpu.TextureUsage.RENDER_ATTACHMENT,
            )
            self.depth_view = self.depth_texture.create_view()

        proj = camera.get_projection_matrix()
        view = camera.get_view_matrix()
        
        vp_mat = proj * view 

        vp_bytes = np.array(vp_mat.to_list(), dtype=np.float32).flatten().tobytes()

        frame_data = (
            vp_bytes
            + np.array(
                [
                    *camera.position,
                    0.0,
                    *scene.lights[0].position,
                    0.0,
                    *scene.lights[0].color,
                    0.0,
                    *scene.lights[1].position,
                    0.0,
                    *scene.lights[1].color,
                    0.0,
                ],
                dtype=np.float32,
            ).tobytes()
        )

        self.device.queue.write_buffer(self.frame_buffer, 0, frame_data)

        if not self.gpu_objects:
            for obj in scene.objects:
                self._prepare_buffers(obj)

        command_encoder = self.device.create_command_encoder()

        render_pass = command_encoder.begin_render_pass(
            color_attachments=[
                {
                    "view": color_view,
                    "resolve_target": None,
                    "clear_value": (0.05, 0.05, 0.05, 1.0),
                    "load_op": wgpu.LoadOp.clear,
                    "store_op": wgpu.StoreOp.store,
                }
            ],
            depth_stencil_attachment={
                "view": self.depth_view,
                "depth_clear_value": 1.0,
                "depth_load_op": wgpu.LoadOp.clear,
                "depth_store_op": wgpu.StoreOp.store,

                "stencil_clear_value": 0,
                "stencil_load_op": wgpu.LoadOp.clear,
                "stencil_store_op": wgpu.StoreOp.store,
            },
        )

        render_pass.set_pipeline(self.pipeline)

        # Bind global frame uniforms (group 0)
        render_pass.set_bind_group(0, self.bg_frame, [], 0, 0)

        for gpu_obj in self.gpu_objects:
            # Bind per-object uniforms (group 1)
            render_pass.set_bind_group(1, gpu_obj["bg_obj"], [], 0, 0)

            render_pass.set_vertex_buffer(0, gpu_obj["vbo"], 0, gpu_obj["vbo"].size)
            render_pass.set_vertex_buffer(1, gpu_obj["nbo"], 0, gpu_obj["nbo"].size)
            render_pass.set_vertex_buffer(2, gpu_obj["ibo"], 0, gpu_obj["ibo"].size)
            render_pass.set_index_buffer(
                gpu_obj["ebo"], wgpu.IndexFormat.uint32, 0, gpu_obj["ebo"].size
            )
            render_pass.draw_indexed(
                gpu_obj["index_count"], gpu_obj["instance_count"], 0, 0, 0
            )

        render_pass.end()
        self.device.queue.submit([command_encoder.finish()])

    def cleanup(self) -> None:
        """Release or reset any GPU resources if needed.

        Currently a no-op; provided for compatibility with the Renderer
        interface and future extension.

        Returns:
            None
        """
        return None
