# main.py
from manim import *
from manim import config
config.renderer = "opengl"  # force OpenGL globally

from manim.opengl import OpenGLVMobject, OpenGLVGroup
import sys, argparse, math
import numpy as np
from PIL import Image

TAU_F = 2.0 * math.pi


def surface_height(u: float, v: float, t: float) -> float:
    return 0.35 * math.sin(2.2 * u + 1.2 * t) + 0.35 * math.cos(2.2 * v - 0.9 * t)


class SurfaceWave3D(ThreeDScene):
    def construct(self):
        self.camera.background_color = rgb_to_color((0.02, 0.03, 0.06))
        self.set_camera_orientation(phi=60 * DEGREES, theta=30 * DEGREES)
        self.begin_ambient_camera_rotation(rate=0.12)

        t = ValueTracker(0.0)

        tex_path = "cbz_icon.jpg"
        img = Image.open(tex_path).convert("RGB")
        arr = np.array(img)
        H, W = arr.shape[:2]

        umin, umax = -3, 3
        vmin, vmax = -3, 3
        nx, ny = 64, 64

        tiles = OpenGLVGroup()
        du = (umax - umin) / nx
        dv = (vmax - vmin) / ny

        for j in range(ny):
            for i in range(nx):
                uc = umin + (i + 0.5) * du
                vc = vmin + (j + 0.5) * dv

                px = int((i / nx) * (W - 1))
                py = int(((ny - 1 - j) / ny) * (H - 1))
                r, g, b = arr[py, px]

                sq = OpenGLVMobject()
                sq.set_points_as_corners([
                    [uc - du/2, vc - dv/2, 0],
                    [uc + du/2, vc - dv/2, 0],
                    [uc + du/2, vc + dv/2, 0],
                    [uc - du/2, vc + dv/2, 0],
                    [uc - du/2, vc - dv/2, 0],
                ])
                sq.set_fill(rgb_to_color((r/255, g/255, b/255)), opacity=1)
                sq.set_stroke(width=0)

                z = surface_height(uc, vc, t.get_value())
                sq.shift([0, 0, z])
                tiles.add(sq)

        def update_tiles(group):
            time = t.get_value()
            k = 0
            for j in range(ny):
                for i in range(nx):
                    uc = umin + (i + 0.5) * du
                    vc = vmin + (j + 0.5) * dv
                    z = surface_height(uc, vc, time)
                    group[k].move_to([uc, vc, z])
                    k += 1
            return group

        tiles.add_updater(update_tiles)

        axes = ThreeDAxes().set_opacity(0.2)

        self.add(axes, tiles)
        self.play(t.animate.set_value(36), run_time=10, rate_func=linear)
        self.wait(1)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--hq", action="store_true")
    args = ap.parse_args(argv)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
