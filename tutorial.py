import pygame as pg
from OpenGL.GL import *
import numpy as np
import ctypes
from OpenGL.GL.shaders import compileProgram, compileShader
import pyrr

class Object:

    def __init__(self, position, euler_angles):
        self.position = np.array(position, dtype=np.float32)
        self.euler_angles = np.array(euler_angles, dtype=np.float32)

class App:

    def __init__(self):

        pg.init()
        pg.display.set_mode((800, 600), pg.DOUBLEBUF | pg.OPENGL)
        self.clock = pg.time.Clock()

        glClearColor(0.2, 0.2, 0.2, 1.0)
        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.shader = self.create_shader("shaders/vertex_shader.glsl", "shaders/fragment_shader.glsl")
        glUseProgram(self.shader)
        glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)

        self.cube = Object(position=(0, 0, -3),
                           euler_angles=(0, 0, 45))

        self.cube_mesh = Mesh()

        self.material = Material("textures/atlas.png")

        projection_matrix = pyrr.matrix44.create_perspective_projection_matrix(
            fovy=45, aspect=800/600,
            near=0.1, far=10, dtype=np.float32)

        glUniformMatrix4fv(
            glGetUniformLocation(self.shader, "projection"),
            1, GL_FALSE, projection_matrix)

        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")

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

            self.cube.euler_angles[0] += 0.5
            if self.cube.euler_angles[0] >= 360:
                self.cube.euler_angles[0] -= 360

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glUseProgram(self.shader)
            self.material.use()
            
            model_matrix = pyrr.matrix44.create_identity(dtype=np.float32)
            model_matrix = pyrr.matrix44.multiply(
                m1=model_matrix,
                m2=pyrr.matrix44.create_from_eulers(
                    eulers=np.radians(self.cube.euler_angles),
                    dtype=np.float32))

            model_matrix = pyrr.matrix44.multiply(
                m1=model_matrix,
                m2=pyrr.matrix44.create_from_translation(
                    vec=self.cube.position,
                    dtype=np.float32))

            glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, model_matrix)

            glBindVertexArray(self.cube_mesh.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.cube_mesh.vertex_count)

            pg.display.flip()
            self.clock.tick(60)

        self.quit()

    def quit(self):
        self.cube_mesh.destroy()
        self.material.destroy()
        glDeleteProgram(self.shader)
        pg.quit()

class Mesh:

    def __init__(self):
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

class Material:

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