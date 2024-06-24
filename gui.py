import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np

from camera import Camera

def CREATE_SHADER(vertex_file_path, fragment_file_path):

    with open(vertex_file_path, 'r') as file:
        vertex_src = file.readlines()
    with open(fragment_file_path, 'r') as file:
        fragment_src = file.readlines()

    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                            compileShader(fragment_src, GL_FRAGMENT_SHADER))

    return shader

GUI_FRAGCOLOR_SHADER = CREATE_SHADER("shaders/2d_fragColor__vertex_shader.glsl", "shaders/2d_fragColor__fragment_shader.glsl")

class GuiFrame:

    def __init__(self, type="quad",
                 size_type="pixel", size=(100, 50),
                 pos_type="pixel", pos=(100, 100),
                 background_type="color", background=(0.2, 0.2, 0.2),
                 oppacity=0.5) -> None:

        vertices = self.create_vertices(size_type, size, pos_type, pos, background_type, background, oppacity)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))

    def render(self) -> None:

        glUseProgram(self.shader)
        self.texture.use()

        glBindVertexArray(self.mine_field_quad.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.mine_field_quad.vertex_count)

    def destroy(self) -> None:

        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

    @staticmethod
    def create_vertices(size_type, size, pos_type, pos, background_type, background, oppacity) -> np.array:

        if size_type == "pixel":
            pixel_size = size
        else:
            raise ValueError("size_type must be 'pixel', other types are not implemented.")

        if pos_type == "pixel":
            pixel_pos = pos
        else:
            raise ValueError("pos_type must be 'pixel', other types are not implemented.")

        if background_type == "color":
            color = background
        else:
            raise ValueError("background_type must be 'color', other types are not implemented.")

        v0 = (pixel_pos[0]                , pixel_pos[1] + pixel_size[1])
        v1 = (pixel_pos[0]                , pixel_pos[1])
        v2 = (pixel_pos[0] + pixel_size[0], pixel_pos[1])
        v3 = (pixel_pos[0] + pixel_size[0], pixel_pos[1] + pixel_size[1])

        # vertices = [x, y, z, r, g, b, a]
        vertices = []
        vertices.extend(v0)
        vertices.extend(color)
        vertices.append(oppacity)
        vertices.extend(v1)
        vertices.extend(color)
        vertices.append(oppacity)
        vertices.extend(v2)
        vertices.extend(color)
        vertices.append(oppacity)
        vertices.extend(v0)
        vertices.extend(color)
        vertices.append(oppacity)
        vertices.extend(v2)
        vertices.extend(color)
        vertices.append(oppacity)
        vertices.extend(v3)
        vertices.extend(color)
        vertices.append(oppacity)

        vertices = np.array(vertices, dtype=np.float32)

        print(vertices)

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
        pos = np.array([0, 0, 5], dtype=np.float32)
        f = np.array([0, 0, -1], dtype=np.float32)
        l = np.array([0, 1, 0], dtype=np.float32)
        u = np.array([1, 0, 0], dtype=np.float32)
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
            print(f"camera pos,view,up: {self.camera.position}, {self.camera.view}, {self.camera.up}")

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
