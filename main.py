import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import glfw

from minesweeper import *

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

        board = MinesweeperBoard(10, 10, 10, 0)

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
        glfw.swap_buffers(self.window)

if __name__ == "__main__":
    app = App()
    app.mainloop()