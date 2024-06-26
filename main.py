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
                 euler_rotation):

        self.shader = shader

        self.fov = fov
        self.screen_size = screen_size
        self.near = near
        self.far = far

        self.position = position
        self.euler_rotation = euler_rotation

        self.projectionMatrixLocation = glGetUniformLocation(self.shader, "projection")
        self.update_projection()

        self.viewMatrixLocation = glGetUniformLocation(self.shader, "view")
        self.update_view()

    def __setattr__(self, name: str, value) -> None:
        # raise AttributeError(f"Attribute '{name}' is read-only")
        super().__setattr__(name, value)

    def get_projection_matrix(self) -> np.ndarray:

        return self.projection_matrix

    def update_projection(self):

        aspect = self.screen_size[0]/self.screen_size[1]
        f = 1.0 / np.tan(self.fov / 2.0)
        a = (self.far + self.near) / (self.near - self.far)
        b = (2.0 * self.far * self.near) / (self.near - self.far)
        self.projection_matrix = np.array([[f / aspect, 0, 0, 0],
                                           [0, f, 0, 0],
                                           [0, 0, a, -1],
                                           [0, 0, b, 0]], dtype=np.float32)

        glUniformMatrix4fv(self.projectionMatrixLocation, 1, GL_FALSE, self.projection_matrix)

    def get_view_matrix(self) -> np.ndarray:

        return self.view_matrix

    def update_view(self):

        self.view_matrix = np.array([[1, 0, 0, self.position[0]],
                                     [0, 1, 0, self.position[1]],
                                     [0, 0, 1, self.position[2]],
                                     [0, 0, 0, 1]], dtype=np.float32)

        glUniformMatrix4fv(self.viewMatrixLocation, 1, GL_TRUE, self.view_matrix)

    def get_ray(self) -> tuple:

        # ray is a vector starting at the camera position and pointing into the direction of the camera
        # the ray is defined by a point and a direction vector

        # the direction is the negative z-axis of the camera
        direction = np.array([0, 0, 1], dtype=np.float32)

        return self.position, direction

    def get_ray_through_screen_pos(self, x, y):

        pos, dir = self.get_ray()

        direction = dir

        return pos, direction

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
        self.cell_size = 1.0
        self.mine_field_quad = FieldQuad(self.minesweeperBoard, self.cell_size)
        self.texture = Texture("textures/atlas.png")

        self.camera = Camera(self.shader, np.radians(90), screen_size, 0.1, 100.0, [-(self.minesweeperBoard.size_x*self.cell_size)/2, -(self.minesweeperBoard.size_y*self.cell_size)/2, -5], [0, 0, 0])

        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")
        model_matrix = np.array([[1, 0, 0, 0],
                                 [0, 1, 0, 0],
                                 [0, 0, 1, 0],
                                 [0, 0, 0, 1]], dtype=np.float32)
        glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_TRUE, model_matrix)

        self.last_time = glfw.get_time()
        self.f1_state_flag = False
        self.mouse_cursor_enabled = True

        self.main_loop()

    def raycasting_xy_plane(self, ray_pos, ray_dir):

        if ray_dir[2] == 0:
            return None

        a = - ray_pos[2] / ray_dir[2]
        if a <= 0:
            return None

        hit_position = ray_pos + a * ray_dir

        return hit_position

    @staticmethod
    def create_shader(vertex_file_path, fragment_file_path):

        with open(vertex_file_path, 'r') as file:
            vertex_src = file.readlines()
        with open(fragment_file_path, 'r') as file:
            fragment_src = file.readlines()

        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))

        return shader

    def mouse_button_callback(self, window, button, action, mods):

        x, y = glfw.get_cursor_pos(window)

        if action == glfw.PRESS:
            self.on_mouse_click(button, int(x), int(y))

    def on_mouse_click(self, button, x, y):

        if button == glfw.MOUSE_BUTTON_LEFT:
            call = self.minesweeperBoard.reveal_cell
        elif button == glfw.MOUSE_BUTTON_RIGHT:
            call = self.minesweeperBoard.flag_cell
        else:
            return

        if self.mouse_cursor_enabled:
            ray_pos, ray_dir = self.camera.get_ray_through_screen_pos(x, y)
            hit_position = self.raycasting_xy_plane(ray_pos, ray_dir)

            ray_pos, ray_dir = self.camera.get_ray()
            hit_position = self.raycasting_xy_plane(ray_pos, ray_dir)
            v = np.array([-1*hit_position[0], -1*hit_position[1], -1*hit_position[2], 1])
            # print(f"{v} -> {v@self.camera.get_projection_matrix()@self.camera.get_view_matrix()}") # TODO: remove
        else:
            ray_pos, ray_dir = self.camera.get_ray()
            hit_position = self.raycasting_xy_plane(ray_pos, ray_dir)
            hit_position = -1 * hit_position

        # TODO: remove
        # print(f"screen pixel: {x}, {y}")
        # print(f"view: {self.camera.get_view_matrix()}")
        # print(f"proj: {self.camera.get_projection_matrix()}")
        # print(f"ray: {ray_pos, ray_dir}")
        # print(f"world coord: {hit_position}")

        # minefield is a rectangle area in the x-y-plane, the z-coordinate is 0
        # x, y coordinates are in [0, size_x*cell_size], [0, size_y*cell_size]

        if hit_position is not None:

            max_x = self.minesweeperBoard.size_x * self.cell_size
            if hit_position[0] < 0 or hit_position[0] > max_x:
                return
            max_y = self.minesweeperBoard.size_y * self.cell_size
            if hit_position[1] < 0 or hit_position[1] > max_y:
                return

            x, y = int(hit_position[0] // self.cell_size), int(hit_position[1] // self.cell_size)

            # print(f"game cell: {x}, {y}") # TODO: remove

            call(self.minesweeperBoard.get_cell(x, y))

            self.update_mine_field_quad()

    def update_mine_field_quad(self):

        self.mine_field_quad.destroy()
        self.mine_field_quad = FieldQuad(self.minesweeperBoard, self.cell_size)

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

        if glfw.get_key(self.window, glfw.KEY_F1) == glfw.PRESS:
            if not self.f1_state_flag:
                self.toggle_mouse_cursor()
                self.f1_state_flag = True
        else:
            self.f1_state_flag = False

        if glfw.get_key(self.window, glfw.KEY_N) == glfw.PRESS:
            self.minesweeperBoard = MinesweeperBoard(10, 10, 10, 0)
            self.update_mine_field_quad()

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
        self.texture.use()

        glBindVertexArray(self.mine_field_quad.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.mine_field_quad.vertex_count)

        glfw.swap_buffers(self.window)

    def quit(self):
        self.mine_field_quad.destroy()
        self.texture.destroy()
        glDeleteProgram(self.shader)
        glfw.terminate()

class FieldQuad:

    def __init__(self, minesweeper, cell_size):

        # vertices = [x, y, z, s, t]
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

        # import matplotlib.pyplot as plt

        # fig = plt.figure()
        # ax = fig.add_subplot(111, projection='3d')

        # vertexes = []
        # for i in range(0, len(vertices), 5):
        #     v = (vertices[i],vertices[i+1],vertices[i+2])
        #     if v in vertexes:
        #         continue
        #     vertexes.append(v)

        # x,y,z = [],[],[]
        # for v in vertexes:
        #     x.append(v[0])
        #     y.append(v[1])
        #     z.append(v[2])
        # ax.scatter(x, y, z)

        # ax.set_xlabel('X')
        # ax.set_ylabel('Y')
        # ax.set_zlabel('Z')

        # ax.axis('equal')

        # plt.show()

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