import pygame as pg
from OpenGL.GL import *
import numpy as np
from OpenGL.GL.shaders import compileProgram, compileShader

from minesweeper import *

class App:

    def __init__(self):

        pg.init()
        screen_size = (pg.display.Info().current_w, pg.display.Info().current_h)
        pg.display.set_mode(screen_size, pg.DOUBLEBUF | pg.OPENGL | pg.FULLSCREEN)
        self.clock = pg.time.Clock()

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

        fov = np.radians(45)
        aspect = screen_size[0]/screen_size[1]
        near = 0.1
        far = 100.0
        f = 1.0 / np.tan(fov / 2.0)
        a = (far + near) / (near - far)
        b = (2.0 * far * near) / (near - far)
        projection_matrix = np.array([
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, a, -1],
            [0, 0, b, 0]
        ], dtype=np.float32)

        glUniformMatrix4fv(
            glGetUniformLocation(self.shader, "projection"),
            1, GL_FALSE, projection_matrix)

        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")
        model_matrix = np.array([[1, 0, 0, 0],
                                 [0, 1, 0, 0],
                                 [0, 0, 1, 0],
                                 [0, 0, 0, 1]], dtype=np.float32)
        glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_TRUE, model_matrix)

        self.viewMatrixLocation = glGetUniformLocation(self.shader, "view")
        view_matrix = np.array([[1, 0, 0, 0],
                                [0, 1, 0, 0],
                                [0, 0, 1, -3],
                                [0, 0, 0, 1]], dtype=np.float32)
        glUniformMatrix4fv(self.viewMatrixLocation, 1, GL_TRUE, view_matrix)

        self.main_loop()

    def create_shader(self, vertex_file_path, fragment_file_path):

        with open(vertex_file_path, 'r') as file:
            vertex_src = file.readlines()
        with open(fragment_file_path, 'r') as file:
            fragment_src = file.readlines()

        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))

        return shader

    def main_loop(self):

        running = True
        while (running):
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glUseProgram(self.shader)
            self.texture.use()

            glBindVertexArray(self.cube_mesh.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.cube_mesh.vertex_count)

            pg.display.flip()
            # self.clock.tick(60)

        self.quit()

    def quit(self):
        self.cube_mesh.destroy()
        self.texture.destroy()
        glDeleteProgram(self.shader)
        pg.quit()

class FieldQuad:

    def __init__(self, minesweeper, cell_size=1.0):
        # x, y, z, s, t
        vertices = (
            # front
             0.5,  0.5,  0.5, 0.25, 1/3,
             0.5,  0.5, -0.5, 0.25, 2/3,
             0.5, -0.5, -0.5, 0, 2/3,

             0.5, -0.5, -0.5, 0, 2/3,
             0.5, -0.5,  0.5, 0, 1/3,
             0.5,  0.5,  0.5, 0.25, 1/3,

            # back
            -0.5,  0.5,  0.5, 1, 0,
            -0.5,  0.5, -0.5, 1, 1/3,
            -0.5, -0.5, -0.5, 0.75, 1/3,

            -0.5, -0.5, -0.5, 0.75, 1/3,
            -0.5, -0.5,  0.5, 0.75, 0,
            -0.5,  0.5,  0.5, 1, 0,

            # bottom
            -0.5, -0.5, -0.5, 0.25, 0,
             0.5, -0.5, -0.5, 0.5, 0,
             0.5,  0.5, -0.5, 0.5, 1/3,

             0.5,  0.5, -0.5, 0.5, 1/3,
            -0.5,  0.5, -0.5, 0.25, 1/3,
            -0.5, -0.5, -0.5, 0.25, 0,

            # top
            -0.5, -0.5,  0.5, 0.5, 0,
             0.5, -0.5,  0.5, 0.75, 0,
             0.5,  0.5,  0.5, 0.75, 1/3,

             0.5,  0.5,  0.5, 0.75, 1/3,
            -0.5,  0.5,  0.5, 0.5, 1/3,
            -0.5, -0.5,  0.5, 0.5, 0,

            # left
            -0.5, -0.5, -0.5, 0.25, 2/3,
             0.5, -0.5, -0.5, 0.5, 2/3,
             0.5, -0.5,  0.5, 0.5, 1/3,

             0.5, -0.5,  0.5, 0.5, 1/3,
            -0.5, -0.5,  0.5, 0.25, 1/3,
            -0.5, -0.5, -0.5, 0.25, 2/3,

            # right
            -0.5,  0.5, -0.5, 0.5, 2/3,
             0.5,  0.5, -0.5, 0.75, 2/3,
             0.5,  0.5,  0.5, 0.75, 1/3,

             0.5,  0.5,  0.5, 0.75, 1/3,
            -0.5,  0.5,  0.5, 0.5, 1/3,
            -0.5,  0.5, -0.5, 0.5, 2/3
        )

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

        image = pg.image.load(file_path).convert_alpha()
        image_width, image_height = image.get_rect().size
        image_data = pg.image.tostring(image, "RGBA")
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width, image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def destroy(self):

        glDeleteTextures(1, (self.texture,))

if __name__ == '__main__':
    app = App()