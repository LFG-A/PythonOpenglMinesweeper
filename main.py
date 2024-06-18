import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import glfw

from minesweeper import *

vertex_shader_source = """
#version 330 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 texCoords;

out vec2 TexCoords;

void main()
{
    gl_Position = vec4(position, 1.0);
    TexCoords = texCoords;
}
"""

fragment_shader_source = """
#version 330 core
out vec4 FragColor;

in vec2 TexCoords;

uniform sampler2D texture1;

void main()
{
    FragColor = texture(texture1, TexCoords);
}
"""

class App:
    def __init__(self):
        self.title = "Menu"

        if not glfw.init():
            return

        self.monitor = glfw.get_primary_monitor()
        self.pixel_x, self.pixel_y = glfw.get_video_mode(self.monitor).size

        self.window = glfw.create_window(self.pixel_x, self.pixel_y, self.title, self.monitor, None)
        if not self.window:
            glfw.terminate()
            return

        glfw.make_context_current(self.window)

        self.board = MinesweeperBoard(10, 10, 10, 0)

    def mainloop(self):
        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            self.manage_input()
            self.render()
        glfw.terminate()

    def manage_input(self):
        pass

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT)

        # TODO: render all

        glfw.swap_buffers(self.window)

from PIL import Image

class Quad:
    def __init__(self, width, height, x, y, texture_path):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.texture_path = texture_path
        self.texture = self.load_texture(texture_path)
        self.shader_program = self.create_shader_program()
        self.vao = self.create_vao()

    def load_texture(self, texture_path):
        image = Image.open(texture_path)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = np.array(image).astype(np.uint8)

        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        return texture

    def create_shader_program(self):
        vertex_shader = compileShader(vertex_shader_source, GL_VERTEX_SHADER)
        fragment_shader = compileShader(fragment_shader_source, GL_FRAGMENT_SHADER)
        shader_program = compileProgram(vertex_shader, fragment_shader)
        return shader_program

    def create_vao(self):
        vertices = [
            # positions         # texture coords
            0.5,  0.5, 0.0,    1.0, 1.0,
            0.5, -0.5, 0.0,    1.0, 0.0,
           -0.5, -0.5, 0.0,    0.0, 0.0,
           -0.5,  0.5, 0.0,    0.0, 1.0
        ]
        indices = [
            0, 1, 3,
            1, 2, 3
        ]
        vertices = np.array(vertices, dtype=np.float32)
        indices = np.array(indices, dtype=np.uint32)

        vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)
        ebo = glGenBuffers(1)

        glBindVertexArray(vao)

        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * vertices.itemsize, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * vertices.itemsize, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        return vao

    def render(self):
        glUseProgram(self.shader_program)
        glBindVertexArray(self.vao)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        glUseProgram(0)

if __name__ == "__main__":
    app = App()
    app.mainloop()