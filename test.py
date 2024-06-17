import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import freetype


VERTEX_SHADER = """
#version 330 core
layout(location = 0) in vec2 position;
void main()
{
    gl_Position = vec4(position, 0.0, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 330 core
out vec4 FragColor;
uniform vec3 color;
void main()
{
    FragColor = vec4(color, 1.0);
}
"""


class GUIElement:
    def __init__(self, x, y, width, height, color, text, font_size=24):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text = text
        self.font_size = font_size
        self.font = freetype.Face("Montserrat-Regular.otf")
        self.font.set_char_size(self.font_size * 64)

        self.vertices = np.array([
            [self.x, self.y],
            [self.x + self.width, self.y],
            [self.x + self.width, self.y + self.height],
            [self.x, self.y + self.height]
        ], dtype=np.float32)

        self.indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)

        glBindVertexArray(self.vao)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * self.vertices.itemsize, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def render(self, shader_program, color_location):
        glUseProgram(shader_program)

        glUniform3fv(color_location, 1, self.color)

        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

        glUseProgram(0)

        self.render_text()

    def render_text(self):
        glPushAttrib(GL_TRANSFORM_BIT | GL_VIEWPORT_BIT)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, glfw.get_window_size(self.window)[0], 0, glfw.get_window_size(self.window)[1], -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        x, y = self.x, glfw.get_window_size(self.window)[1] - self.y - self.font_size
        glRasterPos2f(x, y)

        for c in self.text:
            self.font.load_char(c)
            bitmap = self.font.glyph.bitmap
            w, h = bitmap.width, bitmap.rows

            glDrawPixels(w, h, GL_LUMINANCE, GL_UNSIGNED_BYTE, bitmap.buffer)
            glBitmap(0, 0, 0, 0, self.font.glyph.advance.x >> 6, 0, None)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glPopAttrib()


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

        self.gui_elements = [
            GUIElement(100, 100, 200, 100, (1.0, 0.0, 0.0), "Hello World")
        ]

        self.shader_program = self.create_shader_program()
        self.color_location = glGetUniformLocation(self.shader_program, "color")

    def create_shader_program(self):
        vertex_shader = compileShader(VERTEX_SHADER, GL_VERTEX_SHADER)
        fragment_shader = compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
        shader_program = compileProgram(vertex_shader, fragment_shader)
        return shader_program

    def mainloop(self):
        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            self.manage_input()
            self.render()
        glfw.terminate()

    def manage_input(self):
        pass

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for element in self.gui_elements:
            element.window = self.window
            element.render(self.shader_program, self.color_location)

        glfw.swap_buffers(self.window)


if __name__ == "__main__":
    app = App()
    app.mainloop()
