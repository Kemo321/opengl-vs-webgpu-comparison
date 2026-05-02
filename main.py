import glfw
import argparse
from typing import Any

from src.core.camera import Camera
from src.core.scene import Scene
from src.core.profiler import Profiler
from src.core.window_manager import WindowManager
import src.core.scenarios as scenarios


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for benchmark configuration.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="GKOM Benchmark: OpenGL vs WebGPU")
    parser.add_argument(
        "--api",
        type=str,
        choices=["opengl", "webgpu"],
        default="webgpu",
        help="Select the graphics API to test (default: webgpu)",
    )
    parser.add_argument(
        "--scenario",
        type=int,
        choices=[1, 2, 3],
        default=3,
        help="Select the test scenario. 1: Village, 2: Forest, 3: Stress Test (default: 3)",
    )
    parser.add_argument(
        "--benchmark-frames",
        type=int,
        default=0,
        help="Number of frames to render before automatic closing (0 = disabled)",
    )
    parser.add_argument(
        "--width", type=int, default=1280, help="Window width (default: 1280)"
    )
    parser.add_argument(
        "--height", type=int, default=720, help="Window height (default: 720)"
    )
    return parser.parse_args()


def main() -> None:
    """Run the benchmark application.

    Returns:
        None: This function executes the application until it exits.
    """
    args = parse_arguments()

    # Initialize the camera and window manager.
    camera = Camera(aspect_ratio=args.width / args.height)
    win_manager = WindowManager(
        args.width, args.height, f"GKOM - {args.api.upper()}", camera
    )

    window: Any = win_manager.init_api(args.api)
    if not window:
        print("Failed to initialize window")
        return

    scene = Scene()

    # Load the selected scenario.
    print(f"Loading Scenario {args.scenario}...")
    if args.scenario == 1:
        scenarios.setup_village_scenario(scene)
    elif args.scenario == 2:
        scenarios.setup_forest_scenario(scene)
    else:
        scenarios.setup_mega_grid_scenario(scene)

    profiler = Profiler()

    # Select the renderer based on the chosen API.
    if args.api == "opengl":
        from src.opengl.opengl_renderer import OpenGLRenderer

        renderer = OpenGLRenderer()
    else:
        from src.webgpu.webgpu_renderer import WebGPURenderer

        renderer = WebGPURenderer()

    renderer.init_context(window)
    print(f"Running on {args.api.upper()} API...")

    start_time = glfw.get_time()
    last_time = start_time
    frame_count = 0

    if args.api == "opengl":
        while not glfw.window_should_close(win_manager.glfw_window_ptr):
            current_time = glfw.get_time()
            dt = current_time - last_time
            last_time = current_time

            glfw.poll_events()
            win_manager.process_input(dt)
            renderer.render_frame(scene, camera)

            glfw.swap_buffers(window)

            if profiler.update():
                fps_text = f"GKOM | OPENGL | Scen: {args.scenario} | FPS: {profiler.fps:.0f} | {profiler.frame_time_ms:.2f}ms"
                glfw.set_window_title(win_manager.glfw_window_ptr, fps_text)

            frame_count += 1
            if args.benchmark_frames > 0 and frame_count >= args.benchmark_frames:
                break

        if args.benchmark_frames > 0:
            total_time = glfw.get_time() - start_time
            avg_fps = frame_count / total_time
            avg_frame_time_ms = (total_time / frame_count) * 1000
            print(f"BENCHMARK_RESULT,opengl,{args.scenario},{avg_fps:.2f},{avg_frame_time_ms:.2f}")

        renderer.cleanup()
        glfw.terminate()

    else:
        import wgpu.gui.glfw

        def draw_frame():
            nonlocal last_time, frame_count
            
            if args.benchmark_frames > 0 and frame_count >= args.benchmark_frames:
                glfw.set_window_should_close(win_manager.glfw_window_ptr, True)
                total_time = glfw.get_time() - start_time
                avg_fps = frame_count / total_time
                avg_frame_time_ms = (total_time / frame_count) * 1000
                print(f"BENCHMARK_RESULT,webgpu,{args.scenario},{avg_fps:.2f},{avg_frame_time_ms:.2f}")
                return

            current_time = glfw.get_time()
            dt = current_time - last_time
            last_time = current_time

            glfw.poll_events()
            win_manager.process_input(dt)
            renderer.render_frame(scene, camera)

            if profiler.update():
                fps_text = f"GKOM | WEBGPU | Scen: {args.scenario} | FPS: {profiler.fps:.0f} | {profiler.frame_time_ms:.2f}ms"
                glfw.set_window_title(win_manager.glfw_window_ptr, fps_text)

            frame_count += 1
            
            window.request_draw()

        window.request_draw(draw_frame)
        
        wgpu.gui.glfw.run()
        
        renderer.cleanup()

if __name__ == "__main__":
    main()
