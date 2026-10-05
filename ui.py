import sys
import math
import random

import numpy as np
import sounddevice as sd
import moderngl

from PyQt5.QtWidgets import QApplication, QMainWindow, QOpenGLWidget
from PyQt5.QtCore import QTimer, Qt


# ============================================================
# SETTINGS
# ============================================================

WINDOW_SIZE = 520
PARTICLE_COUNT = 4000

FPS = 120

BASE_RADIUS = 1.0

# ============================================================
# VERTEX SHADER
# ============================================================

VERTEX_SHADER = """
#version 330

uniform mat4 mvp;
uniform float u_time;
uniform float u_volume;

in vec3 in_position;

out float v_depth;
out float v_energy;

void main()
{
    vec3 pos = in_position;

    // --------------------------------------------------------
    // Organic layered wave deformation
    // --------------------------------------------------------

    float wave1 =
        sin(pos.x * 9.0 + u_time * 2.4) *
        cos(pos.y * 7.0 - u_time * 1.7);

    float wave2 =
        sin(pos.z * 13.0 - u_time * 3.1) *
        sin(pos.x * 5.0 + u_time * 1.3);

    float wave3 =
        cos((pos.x + pos.y + pos.z) * 11.0 + u_time * 2.0);

    float combined_wave =
        wave1 * 0.45 +
        wave2 * 0.30 +
        wave3 * 0.25;

    // Audio expands the surface
    float audio_energy =
        u_volume * 0.45;

    float displacement =
        combined_wave * (0.055 + audio_energy);

    pos += normalize(pos) * displacement;

    // --------------------------------------------------------
    // Slow 3D rotation
    // --------------------------------------------------------

    float angle = u_time * 0.22;

    float c = cos(angle);
    float s = sin(angle);

    mat3 rotation = mat3(
         c, 0.0,  s,
         0.0, 1.0, 0.0,
        -s, 0.0,  c
    );

    pos = rotation * pos;

    // --------------------------------------------------------
    // Position
    // --------------------------------------------------------

    gl_Position = mvp * vec4(pos, 1.0);

    // --------------------------------------------------------
    // Particle size
    // --------------------------------------------------------

    float depth_factor =
        clamp(1.0 / gl_Position.w, 0.25, 2.0);

    gl_PointSize =
        2.2 * depth_factor +
        u_volume * 4.0;

    // --------------------------------------------------------
    // Depth / energy information
    // --------------------------------------------------------

    v_depth =
        gl_Position.z / gl_Position.w;

    v_energy =
        abs(combined_wave) +
        u_volume * 2.0;
}
"""


# ============================================================
# FRAGMENT SHADER
# ============================================================

FRAGMENT_SHADER = """
#version 330

in float v_depth;
in float v_energy;

out vec4 f_color;

void main()
{
    // --------------------------------------------------------
    // Circular particle
    // --------------------------------------------------------

    vec2 uv =
        gl_PointCoord * 2.0 - 1.0;

    float distance_from_center =
        dot(uv, uv);

    if (distance_from_center > 1.0)
        discard;

    // Soft particle glow
    float glow =
        1.0 - smoothstep(
            0.0,
            1.0,
            distance_from_center
        );

    // --------------------------------------------------------
    // Futuristic blue/cyan color
    // --------------------------------------------------------

    vec3 core =
        vec3(
            0.35,
            0.95,
            1.0
        );

    vec3 edge =
        vec3(
            0.02,
            0.20,
            0.95
        );

    float mix_amount =
        clamp(
            distance_from_center + v_energy * 0.12,
            0.0,
            1.0
        );

    vec3 color =
        mix(core, edge, mix_amount);

    // --------------------------------------------------------
    // Depth lighting
    // --------------------------------------------------------

    float depth_light =
        1.0 - abs(v_depth) * 0.35;

    color *= depth_light + 0.35;

    // --------------------------------------------------------
    // Final glow
    // --------------------------------------------------------

    float alpha =
        glow * 0.82;

    f_color =
        vec4(color, alpha);
}
"""


# ============================================================
# ORB WIDGET
# ============================================================

class OpenGLOrbWidget(QOpenGLWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.time = 0.0

        self.volume = 0.0

        self.target_volume = 0.0

        self.ctx = None
        self.program = None
        self.vbo = None
        self.vao = None

        # ----------------------------------------------------
        # Audio input
        # ----------------------------------------------------

        try:

            self.stream = sd.InputStream(
                callback=self.audio_callback,
                channels=1,
                samplerate=44100,
                blocksize=512
            )

            self.stream.start()

        except Exception:

            self.stream = None


    # ========================================================
    # AUDIO
    # ========================================================

    def audio_callback(
        self,
        indata,
        frames,
        time_info,
        status
    ):

        try:

            rms = np.sqrt(
                np.mean(
                    np.square(indata)
                )
            )

            self.target_volume = min(
                float(rms * 8.0),
                1.0
            )

        except Exception:

            self.target_volume = 0.0


    # ========================================================
    # OPENGL INITIALIZATION
    # ========================================================

    def initializeGL(self):

        self.ctx = moderngl.create_context()

        # Particle rendering
        self.ctx.enable(
            moderngl.PROGRAM_POINT_SIZE
        )

        # Transparency / glow
        self.ctx.enable(
            moderngl.BLEND
        )

        self.ctx.blend_func = (
            moderngl.SRC_ALPHA,
            moderngl.ONE
        )

        # Depth
        self.ctx.enable(
            moderngl.DEPTH_TEST
        )

        # ----------------------------------------------------
        # Shader program
        # ----------------------------------------------------

        self.program = self.ctx.program(

            vertex_shader=VERTEX_SHADER,

            fragment_shader=FRAGMENT_SHADER
        )

        # ----------------------------------------------------
        # Generate particle sphere
        # ----------------------------------------------------

        vertices = []

        # Golden-angle sphere distribution
        golden_angle = math.pi * (
            3.0 - math.sqrt(5.0)
        )

        for i in range(PARTICLE_COUNT):

            # Even vertical distribution
            y = 1.0 - (
                2.0 * i /
                (PARTICLE_COUNT - 1)
            )

            radius = math.sqrt(
                max(
                    0.0,
                    1.0 - y * y
                )
            )

            theta = (
                golden_angle * i
            )

            x = (
                math.cos(theta)
                * radius
            )

            z = (
                math.sin(theta)
                * radius
            )

            # Slight organic irregularity
            jitter = (
                random.uniform(
                    -0.006,
                    0.006
                )
            )

            x += jitter
            y += jitter
            z += jitter

            vertices.extend(
                [
                    x * BASE_RADIUS,
                    y * BASE_RADIUS,
                    z * BASE_RADIUS
                ]
            )

        data = np.array(
            vertices,
            dtype="f4"
        )

        self.vbo = self.ctx.buffer(
            data.tobytes()
        )

        self.vao = self.ctx.vertex_array(
            self.program,
            [
                (
                    self.vbo,
                    "3f",
                    "in_position"
                )
            ]
        )


    # ========================================================
    # PAINT
    # ========================================================

    def paintGL(self):

        if not self.ctx:
            return

        # ----------------------------------------------------
        # Transparent background
        # ----------------------------------------------------

        self.ctx.clear(
            0.0,
            0.0,
            0.0,
            0.0
        )

        # ----------------------------------------------------
        # Time
        # ----------------------------------------------------

        self.time += 0.016

        # ----------------------------------------------------
        # Smooth audio response
        # ----------------------------------------------------

        self.volume += (
            self.target_volume -
            self.volume
        ) * 0.12

        # ----------------------------------------------------
        # Camera
        # ----------------------------------------------------

        aspect = (
            self.width() /
            max(self.height(), 1)
        )

        projection = self.projection_matrix(
            48.0,
            aspect,
            0.1,
            100.0
        )

        view = self.translate_matrix(
            0.0,
            0.0,
            -3.2
        )

        # Slight dynamic tilt
        tilt_x = (
            0.12 +
            math.sin(self.time * 0.45)
            * 0.04
        )

        rot_x = self.rotate_x_matrix(
            tilt_x
        )

        mvp = (
            projection
            @ view
            @ rot_x
        )

        # ----------------------------------------------------
        # Send data to GPU
        # ----------------------------------------------------

        self.program[
            "mvp"
        ].write(
            mvp.astype(
                "f4"
            ).tobytes()
        )

        self.program[
            "u_time"
        ].value = self.time

        self.program[
            "u_volume"
        ].value = self.volume

        # ----------------------------------------------------
        # Render
        # ----------------------------------------------------

        self.vao.render(
            moderngl.POINTS
        )


    # ========================================================
    # MATRIX HELPERS
    # ========================================================

    def projection_matrix(
        self,
        fov,
        aspect,
        near,
        far
    ):

        f = 1.0 / math.tan(
            math.radians(fov) / 2.0
        )

        return np.array(
            [
                [
                    f / aspect,
                    0,
                    0,
                    0
                ],

                [
                    0,
                    f,
                    0,
                    0
                ],

                [
                    0,
                    0,
                    (far + near) /
                    (near - far),
                    (2 * far * near) /
                    (near - far)
                ],

                [
                    0,
                    0,
                    -1,
                    0
                ]
            ],
            dtype="f4"
        )


    def translate_matrix(
        self,
        x,
        y,
        z
    ):

        return np.array(
            [
                [1, 0, 0, x],
                [0, 1, 0, y],
                [0, 0, 1, z],
                [0, 0, 0, 1]
            ],
            dtype="f4"
        )


    def rotate_x_matrix(
        self,
        theta
    ):

        c = math.cos(theta)
        s = math.sin(theta)

        return np.array(
            [
                [1, 0, 0, 0],
                [0, c, -s, 0],
                [0, s, c, 0],
                [0, 0, 0, 1]
            ],
            dtype="f4"
        )


    # ========================================================
    # CLEANUP
    # ========================================================

    def closeEvent(self, event):

        if self.stream:

            try:
                self.stream.stop()
                self.stream.close()

            except Exception:
                pass

        event.accept()


# ============================================================
# MAIN WINDOW
# ============================================================

class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )

        self.setAttribute(
            Qt.WA_TranslucentBackground,
            True
        )

        self.setAttribute(
            Qt.WA_NoSystemBackground,
            True
        )

        self.resize(
            WINDOW_SIZE,
            WINDOW_SIZE
        )

        # ----------------------------------------------------
        # OpenGL widget
        # ----------------------------------------------------

        self.gl_widget = OpenGLOrbWidget(
            self
        )

        self.setCentralWidget(
            self.gl_widget
        )

        # ----------------------------------------------------
        # Center on screen
        # ----------------------------------------------------

        screen = QApplication.primaryScreen()

        geometry = screen.availableGeometry()

        x = (
            geometry.x()
            + (
                geometry.width()
                - WINDOW_SIZE
            ) // 2
        )

        y = (
            geometry.y()
            + (
                geometry.height()
                - WINDOW_SIZE
            ) // 2
        )

        self.move(x, y)

        # ----------------------------------------------------
        # Render timer
        # ----------------------------------------------------

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.gl_widget.update
        )

        self.timer.start(
            int(1000 / FPS)
        )

        # ----------------------------------------------------
        # Mouse dragging
        # ----------------------------------------------------

        self.drag_position = None


    # ========================================================
    # DRAG WINDOW
    # ========================================================

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:

            self.drag_position = (
                event.globalPos()
                - self.frameGeometry().topLeft()
            )

            event.accept()


    def mouseMoveEvent(self, event):

        if (
            event.buttons()
            & Qt.LeftButton
            and self.drag_position
        ):

            self.move(
                event.globalPos()
                - self.drag_position
            )

            event.accept()


    def mouseReleaseEvent(self, event):

        self.drag_position = None


# ============================================================
# APPLICATION
# ============================================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()

    window.show()

    sys.exit(
        app.exec_()
    )
