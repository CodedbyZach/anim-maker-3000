# main.py
# Render all scenes: python main.py
# Manim CLI: manim -pqh main.py 1,2,3,4
# Tests: python main.py --selftest

from __future__ import annotations
import sys, argparse, platform, unittest, importlib.util, math
import numpy as np

# Try to import manim
MANIM_OK = False
MANIM_IMPORT_ERROR = None
try:
    from manim import *  # CE 0.19+
    MANIM_OK = True
except Exception as e:
    MANIM_IMPORT_ERROR = e
    MANIM_OK = False

TAU_F = 2.0 * math.pi

# ---------- math helpers ----------
def lissajous_point(t: float, a: float, b: float, kx: float, ky: float, phase: float) -> np.ndarray:
    return np.array([a * math.sin(kx * t + phase), b * math.sin(ky * t), 0.0], dtype=float)

def surface_height(u: float, v: float, t: float) -> float:
    return 0.35 * math.sin(2.2 * u + 1.2 * t) + 0.35 * math.cos(2.2 * v - 0.9 * t)

# ---------- scenes ----------
if MANIM_OK:

    class HypnoticLissajous(Scene):
        def construct(self):
            self.camera.background_color = rgb_to_color((0.04, 0.05, 0.07))
            t_tracker = ValueTracker(0.0)
            kx, ky = 3.0, 2.0
            a, b = 3.5, 2.0
            phase_tracker = ValueTracker(0.0)

            def curve_point(t: float, phase: float) -> np.ndarray:
                return lissajous_point(t, a, b, kx, ky, phase)

            mover = Dot(radius=0.06, color=YELLOW)
            mover.add_updater(lambda m: m.move_to(curve_point(t_tracker.get_value() % TAU, phase_tracker.get_value())))

            trail = TracedPath(mover.get_center, stroke_width=3, stroke_opacity=0.85)
            trail.set_color_by_gradient(BLUE_E, PURPLE_E, PINK)

            bg_group = VGroup()
            for i in range(18):
                ph = i * (TAU / 18)
                c = always_redraw(
                    lambda ph=ph: ParametricFunction(
                        lambda t: curve_point(t, phase_tracker.get_value() + ph),
                        t_range=[0, TAU],
                        use_smoothing=True,
                    ).set_stroke(width=1.8, opacity=0.22).set_color_by_gradient(PURPLE_D, BLUE_D)
                )
                bg_group.add(c)

            # Safe MathTex fallback
            try:
                eq = MathTex(r"x=a\sin(k_x t+\phi),\ y=b\sin(k_y t)").scale(0.8)
            except Exception:
                eq = Text("x=a sin(kx t+φ), y=b sin(ky t)").scale(0.6)

            title = VGroup(
                Text("Lissajous Flow", font="Montserrat", weight=BOLD).scale(0.8),
                eq,
            ).arrange(DOWN, buff=0.15).to_edge(UL).set_opacity(0.7)

            self.add(bg_group, trail, mover, title)
            self.play(
                t_tracker.animate.set_value(10 * TAU),
                phase_tracker.animate.set_value(8 * PI),
                run_time=10,
                rate_func=rate_functions.ease_in_out_sine,
            )
            self.play(
                t_tracker.animate.set_value(20 * TAU),
                phase_tracker.animate.set_value(20 * PI),
                run_time=12,
                rate_func=rate_functions.linear,
            )
            self.wait(0.5)

    class PulseGrid(Scene):
        def construct(self):
            self.camera.background_color = rgb_to_color((0.03, 0.05, 0.06))
            cols, rows = 22, 12
            spacing = 0.6
            grid = VGroup()
            for j in range(rows):
                row = VGroup()
                for i in range(cols):
                    dot = Circle(radius=0.09, stroke_width=0, fill_opacity=1)
                    dot.move_to(np.array([
                        (i - (cols - 1) / 2) * spacing,
                        (j - (rows - 1) / 2) * spacing,
                        0.0,
                    ]))
                    row.add(dot)
                grid.add(row)
            grid.set_color_by_gradient(BLUE_E, TEAL_E, GREEN_E)

            t = ValueTracker(0.0)
            source = Dot(color=YELLOW).scale(0.7)
            source.move_to(LEFT * 5 + DOWN * 2.5)

            def update_grid(g: VGroup):
                time = t.get_value()
                src = source.get_center()
                for row in g:
                    for dot in row:
                        d = np.linalg.norm(dot.get_center() - src)
                        k = 2.5
                        phase = k * d - 2.2 * time
                        s = 0.5 + 0.45 * math.sin(phase)
                        dot.set_fill(opacity=0.9)
                        dot.set_stroke(width=0)
                        dot.set_width(0.18 + 0.12 * s)
                return g

            grid.add_updater(update_grid)

            label = Text("Pulse Grid", font="Montserrat", weight=MEDIUM).scale(0.8).to_corner(UL).set_opacity(0.8)

            self.add(grid, source, label)
            self.play(t.animate.set_value(10), run_time=5, rate_func=linear)
            self.play(
                t.animate.set_value(28),
                source.animate.shift(RIGHT * 8 + UP * 3),
                run_time=7,
                rate_func=rate_functions.ease_in_out_sine,
            )
            self.wait(0.6)

    class SurfaceWave3D(ThreeDScene):
        def construct(self):
            self.camera.background_color = rgb_to_color((0.02, 0.03, 0.06))
            self.set_camera_orientation(phi=60 * DEGREES, theta=30 * DEGREES, zoom=1.0)
            self.begin_ambient_camera_rotation(rate=0.12)

            t = ValueTracker(0.0)

            def make_surface():
                # Manim CE 0.19: use Surface, not ParametricSurface
                s = Surface(
                    lambda u, v: np.array([u, v, surface_height(u, v, t.get_value())]),
                    u_range=[-3, 3], v_range=[-3, 3],
                    resolution=(32, 32),
                    fill_opacity=0.95,
                    stroke_opacity=0.15,
                    checkerboard_colors=[BLUE_E, TEAL_D],
                )
                s.set_shade_in_3d(True)
                return s

            surface = always_redraw(make_surface)

            axes = ThreeDAxes(x_range=[-4, 4, 2], y_range=[-4, 4, 2], z_range=[-2, 2, 1])
            axes.set_opacity(0.25)

            title = Text("Surface Waves", font="Montserrat").scale(0.8).to_corner(UL).set_opacity(0.8)

            self.add(axes, surface, title)
            self.play(t.animate.set_value(12), run_time=6, rate_func=linear)
            self.play(t.animate.set_value(36), run_time=10, rate_func=linear)
            self.wait(0.6)

    class TextMorph(Scene):
        def construct(self):
            self.camera.background_color = rgb_to_color((0.04, 0.04, 0.04))
            t1 = Text("ZACHARY", weight=BOLD, font="Montserrat").scale(1.2)
            t2 = Text("MANIM", weight=BOLD, font="Montserrat").scale(1.2).set_color_by_gradient(BLUE_E, PURPLE_E)
            t3 = Text("ANIMATION", weight=BOLD, font="Montserrat").scale(1.0).set_color_by_gradient(TEAL_E, GREEN_E)

            underline = Line(LEFT * 3.5, RIGHT * 3.5).set_stroke(width=6)
            underline.set_color_by_gradient(BLUE_E, PURPLE_E)

            self.play(FadeIn(t1, shift=UP * 0.5), Create(underline))
            self.wait(0.3)
            self.play(TransformMatchingShapes(t1, t2), run_time=1.6)
            self.play(underline.animate.set_color_by_gradient(TEAL_E, GREEN_E), run_time=0.8)
            self.play(TransformMatchingShapes(t2, t3), run_time=1.6)

            sparks = VGroup()
            for k in range(20):
                ang = k * TAU / 20
                r1, r2 = 0.2, 1.5
                ln = Line(r1 * RIGHT, r2 * RIGHT).rotate(ang)
                ln.set_stroke(color=YELLOW, width=4)
                ln.set_opacity(0.9)
                sparks.add(ln)
            sparks.move_to(ORIGIN)
            self.play(LaggedStart(*[Create(s) for s in sparks], lag_ratio=0.04), run_time=0.7)
            self.play(
                AnimationGroup(
                    *[s.animate.set_opacity(0).scale(1.8) for s in sparks],
                    lag_ratio=0.05,
                    run_time=0.9,
                )
            )
            self.play(FadeOut(VGroup(sparks, underline, t3)))
            self.wait(0.2)

# ---------- self-tests ----------
class SelfTests(unittest.TestCase):
    def test_numpy_available(self):
        self.assertTrue(importlib.util.find_spec("numpy") is not None)

    def test_lissajous_center(self):
        p = lissajous_point(0.0, a=3.5, b=2.0, kx=3.0, ky=2.0, phase=0.0)
        self.assertAlmostEqual(float(p[0]), 0.0, places=7)
        self.assertAlmostEqual(float(p[1]), 0.0, places=7)
        self.assertAlmostEqual(float(p[2]), 0.0, places=7)

    def test_lissajous_bounds(self):
        a, b, kx, ky = 3.5, 2.0, 3.0, 2.0
        ts = np.linspace(0, TAU_F, 1000)
        xs = [abs(lissajous_point(t, a, b, kx, ky, 0.3)[0]) for t in ts]
        ys = [abs(lissajous_point(t, a, b, kx, ky, 0.3)[1]) for t in ts]
        self.assertLessEqual(max(xs), a + 1e-9)
        self.assertLessEqual(max(ys), b + 1e-9)

    def test_surface_height_bounds(self):
        us = np.linspace(-3, 3, 21)
        vs = np.linspace(-3, 3, 21)
        vals = [abs(surface_height(u, v, t=1.23)) for u in us for v in vs]
        self.assertLessEqual(max(vals), 0.71)

    def test_scene_names_defined_when_manim_ok(self):
        if MANIM_OK:
            for cls in ("HypnoticLissajous","PulseGrid","SurfaceWave3D","TextMorph"):
                self.assertIn(cls, globals())

# ---------- runner ----------
def render_all(hq: bool = False) -> int:
    if not MANIM_OK:
        print("Manim not found.")
        print("Install: pip install manim")
        if platform.system() == "Windows":
            print("FFmpeg: use Chocolatey as admin or manual ZIP. See docs.")
        else:
            print("FFmpeg: sudo apt-get install ffmpeg")
        if MANIM_IMPORT_ERROR:
            print("Import error detail:\n", repr(MANIM_IMPORT_ERROR))
        return 1

    if hq:
        config.pixel_width = 1920
        config.pixel_height = 1080
        config.frame_rate = 60
        config.quality = "high_quality"
    else:
        config.pixel_width = 1280
        config.pixel_height = 720
        config.frame_rate = 30
        config.quality = "medium_quality"

    scenes = [HypnoticLissajous, PulseGrid, SurfaceWave3D, TextMorph]
    for S in scenes:
        print(f"Rendering {S.__name__} ...")
        scene = S()
        scene.render()
    print("Done.")
    return 0

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true", help="Run math unit tests.")
    ap.add_argument("--hq", action="store_true", help="Render at 1080p60.")
    args = ap.parse_args(argv)

    if args.selftest:
        result = unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(SelfTests)
        )
        return 0 if result.wasSuccessful() else 1

    # If invoked via Manim CLI, Manim constructs scenes itself.
    # If run as a script, render all scenes.
    if "manim" in sys.argv[0].lower():
        return 0
    return render_all(hq=args.hq)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))