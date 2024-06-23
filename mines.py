import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
from PIL import Image

from minesweeper import *

class Camera:

    def __init__(self,
                 shader,
                 fov,
                 screen_size,
                 near,
                 far,
                 position,
                 rotation):

        self.shader = shader

        self.fov = fov
        self.screen_size = screen_size
        self.near = near
        self.far = far

        self.position = position
        self.rotation = rotation

        self.projectionMatrixLocation = glGetUniformLocation(self.shader, "projection")
        self.update_projection()

        self.viewMatrixLocation = glGetUniformLocation(self.shader, "view")
        self.update_view()

    def __setattr__(self, name: str, value) -> None:
        # raise AttributeError(f"Attribute '{name}' is read-only")
        super().__setattr__(name, value)

    def update_projection(self):
        aspect = self.screen_size[0]/self.screen_size[1]
        f = 1.0 / np.tan(self.fov / 2.0)
        a = (self.far + self.near) / (self.near - self.far)
        b = (2.0 * self.far * self.near) / (self.near - self.far)
        projection_matrix = np.array([[f / aspect, 0, 0, 0],
                                      [0, f, 0, 0],
                                      [0, 0, a, -1],
                                      [0, 0, b, 0]], dtype=np.float32)

        glUniformMatrix4fv(self.projectionMatrixLocation, 1, GL_FALSE, projection_matrix)

    def update_view(self):
        view_matrix = np.array([[1, 0, 0, self.position[0]],
                                [0, 1, 0, self.position[1]],
                                [0, 0, 1, self.position[2]],
                                [0, 0, 0, 1]], dtype=np.float32)
        glUniformMatrix4fv(self.viewMatrixLocation, 1, GL_TRUE, view_matrix)

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

        glClearColor(0.2, 0.2, 0.2, 1.0)
        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.shader = self.create_shader("shaders/vertex_shader.glsl", "shaders/fragment_shader.glsl")
        glUseProgram(self.shader)
        glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)

        self.minesweeperBoard = MinesweeperBoard(10, 10, 10, 0)
        self.minesweeperBoard.reveal_cell(self.minesweeperBoard.get_cell(0, 0))
        self.cube_mesh = FieldQuad(self.minesweeperBoard)
        self.texture = Texture("textures/atlas.png")

        self.camera = Camera(self.shader, np.radians(90), screen_size, 0.1, 100.0, [0, 0, -5], [0, 0, 0])

        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")
        model_matrix = np.array([[1, 0, 0, 0],
                                 [0, 1, 0, 0],
                                 [0, 0, 1, 0],
                                 [0, 0, 0, 1]], dtype=np.float32)
        glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_TRUE, model_matrix)

        self.last_time = glfw.get_time()

        self.main_loop()

    def create_shader(self, vertex_file_path, fragment_file_path):

        with open(vertex_file_path, 'r') as file:
            vertex_src = file.readlines()
        with open(fragment_file_path, 'r') as file:
            fragment_src = file.readlines()

        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))

        return shader

    def mouse_button_callback(self, window, button, action, mods):
        if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
            print("Linksklick erkannt!")
            # Füge hier den Code hinzu, der bei einem Linksklick ausgeführt werden soll

        if button == glfw.MOUSE_BUTTON_RIGHT and action == glfw.PRESS:
            print("Rechtsklick erkannt!")
    
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

        if glfw.get_key(self.window, glfw.KEY_P) == glfw.PRESS:
            self.minesweeperBoard.print()
            print()
        if glfw.get_key(self.window, glfw.KEY_O) == glfw.PRESS:
            print(self.camera.position)

        t = glfw.get_time()
        dt = t - self.last_time
        self.last_time = t

        speed = 2.0
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

        self.camera.update_view()

    def render(self):

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shader)
        self.texture.use()

        glBindVertexArray(self.cube_mesh.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.cube_mesh.vertex_count)

        glfw.swap_buffers(self.window)

    def quit(self):
        self.cube_mesh.destroy()
        self.texture.destroy()
        glDeleteProgram(self.shader)
        glfw.terminate()

class FieldQuad:

    def __init__(self, minesweeper, cell_size=1.0):

        # x, y, z, s, t
        vertices = []
        size_x, size_y = minesweeper.size_x, minesweeper.size_y
        for y in range(size_y):
            y_pos = y*cell_size
            for x in range(size_x):
                x_pos = x*cell_size
                v0 = (x_pos, y_pos, 0)
                v1 = (x_pos, y_pos + cell_size, 0)
                v2 = (x_pos + cell_size, y_pos + cell_size, 0)
                v3 = (x_pos + cell_size, y_pos, 0)
                vts = MinesweeperCell.get_atlas_coords(minesweeper.get_cell(x, y))

                vertices.extend(v0)
                vertices.extend(vts[2])
                vertices.extend(v1)
                vertices.extend(vts[0])
                vertices.extend(v2)
                vertices.extend(vts[1])

                vertices.extend(v2)
                vertices.extend(vts[1])
                vertices.extend(v3)
                vertices.extend(vts[3])
                vertices.extend(v0)
                vertices.extend(vts[2])

        self.vertex_count = len(vertices) // 5
        self.vertices = np.array(vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))

    def destroy(self):

        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

class Texture:

    def __init__(self, file_path):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # Verwende Pillow, um das Bild zu laden
        image = Image.open(file_path).convert("RGBA")
        image_width, image_height = image.size
        image_data = np.array(image.getdata(), np.uint8)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width, image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def destroy(self):

        glDeleteTextures(1, (self.texture,))

if __name__ == '__main__':
    app = App()