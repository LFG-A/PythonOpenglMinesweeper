import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import glfw
from PIL import Image

from minesweeper import *

VERTEX_SHADER = """
#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec2 texCoords;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec2 TexCoords;

void main()
{
    vec4 worldPosition = vec4(position, 1.0) * model;
    gl_Position = projection * view * worldPosition;
    TexCoords = texCoords;
}

"""

VERTEX_SHADER = """
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

FRAGMENT_SHADER = """
#version 330 core
out vec4 FragColor;

in vec2 texCoords;

uniform sampler2D texture1;

void main()
{
    FragColor = texture(texture1, texCoords);
}
"""

FRAGMENT_SHADER = """
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
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1.0)

        self.last_time = glfw.get_time()
        self.view = np.array([[0.0, 0.0, 1.0, -5.0],
                              [-1.0, 0.0, 0.0, 0.0],
                              [0.0, 1.0, 0.0, 0.0],
                              [0.0, 0.0, 0.0, 1.0]], dtype=np.float32)

        self.minesweeper = MinesweeperBoard(10, 10, 10, 0)

        self.texture_atlas = self.load_texture("textures/atlas.png")

        cell_size = 0.1 # size of a cell side in meters
        self.field_quad = FieldQuad(cell_size=cell_size, minesweeper=self.minesweeper)

        vertex_shader = compileShader(VERTEX_SHADER, GL_VERTEX_SHADER)
        fragment_shader = compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
        self.shader_program = compileProgram(vertex_shader, fragment_shader)
        glUseProgram(self.shader_program)

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

    def mainloop(self):
        fov = np.radians(45)
        aspect = self.pixel_x / self.pixel_y
        near = 0.1
        far = 100.0

        f = 1.0 / np.tan(fov / 2.0)
        a = (far + near) / (near - far)
        b = (2.0 * far * near) / (near - far)

        projection = np.array([[f / aspect, 0, 0, 0],
                               [0, f, 0, 0],
                               [0, 0, a, -1],
                               [0, 0, b, 0]], dtype=np.float32)

        proj_loc = glGetUniformLocation(self.shader_program, "projection")
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)

        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            self.manage_input()
            self.render()
        glfw.terminate()

    def manage_input(self):
        if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(self.window, True)
            return

        if glfw.get_key(self.window, glfw.KEY_P) == glfw.PRESS:
            self.minesweeper.print()
            print()

        if glfw.get_key(self.window, glfw.KEY_O) == glfw.PRESS:
            print(self.view)
            print()

        t = glfw.get_time()
        dt = t - self.last_time
        self.last_time = t

        speed = 5.0
        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS:
            self.view[0][3] += speed * dt
        elif glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS:
            self.view[0][3] -= speed * dt

        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS:
            self.view[1][3] += speed * dt
        elif glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS:
            self.view[1][3] -= speed * dt

        if glfw.get_key(self.window, glfw.KEY_SPACE) == glfw.PRESS:
            self.view[2][3] += speed * dt
        elif glfw.get_key(self.window, glfw.KEY_C) == glfw.PRESS:
            self.view[2][3] -= speed * dt

        view_loc = glGetUniformLocation(self.shader_program, "view")
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, self.view)

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.field_quad.render(self.shader_program)

        glfw.swap_buffers(self.window)

class FieldQuad:
    def __init__(self, cell_size, minesweeper):
        self.model = np.array([[1.0, 0.0, 0.0, 0.0],
                               [0.0, 1.0, 0.0, 0.0],
                               [0.0, 0.0, 1.0, 0.0],
                               [0.0, 0.0, 0.0, 1.0]], dtype=np.float32)

        self.create_buffer(cell_size=cell_size, minesweeper=minesweeper)

    def create_buffer(self, cell_size, minesweeper):
        vertices = [
            # positions      # texture coords
            -1.0,  1.0, 0.0, 0.0, 0.4,
            -1.0, -1.0, 0.0, 0.0, 0.6,
             1.0, -1.0, 0.0, 0.2, 0.6,
             1.0,  1.0, 0.0, 0.2, 0.4]
        indices = [0, 1, 2, 0, 2, 3]

        size_x, size_y = minesweeper.size_x, minesweeper.size_y
        for y in range(size_y):
            y_pos = y*cell_size
            for x in range(size_x):
                v0 = (x*cell_size, y_pos, 0)
                v1 = (x*cell_size, y_pos + cell_size, 0)
                v2 = (x*cell_size + cell_size, y_pos, 0)
                v3 = (x*cell_size + cell_size, y_pos + cell_size, 0)
                vts = MinesweeperCell.get_atlas_coords(minesweeper.get_cell(x, y))

                vertices.extend(v0)
                vertices.extend(vts[0])
                vertices.extend(v1)
                vertices.extend(vts[1])
                vertices.extend(v2)
                vertices.extend(vts[2])
                vertices.extend(v3)
                vertices.extend(vts[3])

                offset = y * size_x + x * 20
                indices.extend([offset, offset+1, offset+2, offset+1, offset+2, offset+3])
                # print(x, y)
                # print(vertices)
                # print(indices)
                # return

        vertices = np.array(vertices, dtype=np.float32)
        indices = np.array(indices, dtype=np.uint32)

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)

        glBindVertexArray(self.vao)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * vertices.itemsize, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * vertices.itemsize, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def set_model_transformation(self, model):
        self.model = model

    def render(self, shader_program):
        model_loc = glGetUniformLocation(shader_program, "model")
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, self.model)

        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
    
    # def __del__(self):
    #     glDeleteVertexArrays(1, self.vao)
    #     glDeleteBuffers(1, self.vbo)
    #     glDeleteBuffers(1, self.ebo)

if __name__ == "__main__":
    app = App()
    app.mainloop()