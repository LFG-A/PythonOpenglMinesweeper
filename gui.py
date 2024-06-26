import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np

from camera import Camera

class Gui:

    @staticmethod
    def create_shader(vertex_file_path, fragment_file_path):

        with open(vertex_file_path, 'r') as file:
            vertex_src = file.readlines()
        with open(fragment_file_path, 'r') as file:
            fragment_src = file.readlines()

        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))

        return shader

class GuiFrame:
    """
    A class used to manage and render a frame as GUI on the screen.

    Attributes
    ----------
    not documented

    Methods
    -------
    not documented
    """

    def __init__(self, type="quad",
                 size_type="screenspace", size=(0.2, 0.2),
                 pos_type="screenspace", pos=(0.25, 0.5),
                 background_type="rgb", background=(0.2, 0.2, 0.2),
                 oppacity=0.5) -> None:

        vertices = self.create_vertices(size_type, size, pos_type, pos, background_type, background, oppacity)
        self.vertex_count = len(vertices[0])
        print(self.vertex_count)
        vertices = [vertex for vertices in vertices for vertex in vertices]
        print(vertices)
        vertices = np.array(vertices, dtype=np.float32)
        print(vertices)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))

    def render(self) -> None:

        glUseProgram(self.shader)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def destroy(self) -> None:

        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

        glDeleteProgram(self.shader)

    def create_vertices(self, size_type, size, pos_type, pos, background_type, background, oppacity) -> np.array:

        # vertices = [x, y, z, r, g, b, a] for background_type == "rgb" && oppacity != None

        if size_type == "screenspace":
            pixel_size = size
        else:
            raise ValueError("size_type must be 'screenspace', other types are not implemented.")

        if pos_type == "screenspace":
            pixel_pos = pos
        else:
            raise ValueError("pos_type must be 'screenspace', other types are not implemented.")

        v0 = [pixel_pos[0]                , pixel_pos[1] + pixel_size[1]]
        v1 = [pixel_pos[0]                , pixel_pos[1]]
        v2 = [pixel_pos[0] + pixel_size[0], pixel_pos[1]]
        v3 = [pixel_pos[0] + pixel_size[0], pixel_pos[1] + pixel_size[1]]

        if background_type == "rgb":
            for value in background:
                if value < 0.0:
                    value = 0.0
                elif value > 1.0:
                    value = 1.0
            self.shader = Gui.create_shader("shaders/2d_fragColor_vertex_shader.glsl", "shaders/2d_fragColor_fragment_shader.glsl")
            v0.extend(background)
            v1.extend(background)
            v2.extend(background)
            v3.extend(background)
        else:
            raise ValueError("background_type must be 'rgba', other types are not implemented.")

        if oppacity is not None:
            if oppacity < 0.0:
                oppacity = 0.0
            elif oppacity > 1.0:
                oppacity = 1.0
            v0.append(oppacity)
            v1.append(oppacity)
            v2.append(oppacity)
            v3.append(oppacity)

        vertices = [v0, v1, v2, v0, v2, v3]

        return vertices

class App:

    def __init__(self):

        if not glfw.init():
            return

        monitor = glfw.get_primary_monitor()
        screen_size = glfw.get_video_mode(monitor).size

        title = "Minesweeper"
        self.window = glfw.create_window(screen_size[0], screen_size[1], title, monitor, None)
        if not self.window:
            glfw.terminate()
            return

        glfw.make_context_current(self.window)

        glfw.set_mouse_button_callback(self.window, self.mouse_button_callback)

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.shader = self.create_shader("shaders/vertex_shader.glsl", "shaders/fragment_shader.glsl")
        glUseProgram(self.shader)
        glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)

        fov = 110
        pos = np.array([0, 0, 0], dtype=np.float32)
        f = np.array([1, 0, 0], dtype=np.float32)
        l = np.array([0, 1, 0], dtype=np.float32)
        u = np.array([0, 0, 1], dtype=np.float32)
        self.camera = Camera(self.shader, np.radians(fov), screen_size, 0.1, 100.0, pos, f, l, u)

        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")
        model_matrix = np.array([[1, 0, 0, 0],
                                 [0, 1, 0, 0],
                                 [0, 0, 1, 0],
                                 [0, 0, 0, 1]], dtype=np.float32)
        glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_TRUE, model_matrix)

        self.last_time = glfw.get_time()
        self.f1_state_flag = False
        self.mouse_cursor_enabled = True

        self.gui_elemets = [GuiFrame()]

        self.main_loop()

    def mouse_button_callback(self, window, button, action, mods):

        x, y = glfw.get_cursor_pos(window)

        if action == glfw.PRESS:
            self.on_mouse_click(button, int(x), int(y))

    def create_shader(self, vertex_file_path, fragment_file_path):

        with open(vertex_file_path, 'r') as file:
            vertex_src = file.readlines()
        with open(fragment_file_path, 'r') as file:
            fragment_src = file.readlines()

        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))

        return shader

    def main_loop(self):

        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            self.manage_input()
            self.render()

        self.quit()

    def manage_input(self):
        if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(self.window, True)
            return

        if glfw.get_key(self.window, glfw.KEY_O) == glfw.PRESS:
            print(f"camera pos,view_direction,up: {self.camera.position}, {self.camera.view_direction}, {self.camera.up_direction}")

        t = glfw.get_time()
        dt = t - self.last_time
        self.last_time = t

        speed = 1.0
        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS:
            self.camera.position[2] += speed * dt
        elif glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS:
            self.camera.position[2] -= speed * dt

        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS:
            self.camera.position[0] += speed * dt
        elif glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS:
            self.camera.position[0] -= speed * dt

        if glfw.get_key(self.window, glfw.KEY_SPACE) == glfw.PRESS:
            self.camera.position[1] -= speed * dt
        elif glfw.get_key(self.window, glfw.KEY_C) == glfw.PRESS:
            self.camera.position[1] += speed * dt

        if glfw.get_key(self.window, glfw.KEY_F1) == glfw.PRESS:
            if not self.f1_state_flag:
                self.toggle_mouse_cursor()
                self.f1_state_flag = True
        else:
            self.f1_state_flag = False

        self.camera.update_view()

    def toggle_mouse_cursor(self) -> None:

        self.mouse_cursor_enabled = not self.mouse_cursor_enabled
        if glfw.get_input_mode(self.window, glfw.CURSOR) == glfw.CURSOR_DISABLED:
            glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_NORMAL)
        else:
            glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    def render(self):

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shader)

        glfw.swap_buffers(self.window)

    def quit(self):
        glDeleteProgram(self.shader)
        glfw.terminate()

def test():
    app = App()

if __name__ == "__main__":
    test()
