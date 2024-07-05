import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np



from camera import Camera



class App:

    def __init__(self, title="OpenGL App", gl_clear_color=(0.2, 0.2, 0.2, 1.0)):

        if not glfw.init():
            return

        monitor = glfw.get_primary_monitor()
        screen_size = glfw.get_video_mode(monitor).size

        self.window = glfw.create_window(screen_size[0], screen_size[1], title, monitor, None)
        if not self.window:
            glfw.terminate()
            return
        glfw.make_context_current(self.window)

        glfw.set_mouse_button_callback(self.window, self.mouse_button_callback)

        glClearColor(gl_clear_color)
        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.shader = {}
        self.textures = []
        self.static_objects = []
        self.dynamic_objects = []
        self.camera = Camera(self.shader, screen_size=screen_size)

        self.f1_state_flag = False
        self.mouse_cursor_enabled = True

    def load_shader(self, vertex_file_path, fragment_file_path):

        shader_key = (vertex_file_path, fragment_file_path)

        if shader_key in self.shader:
            return self.shader_dict[vertex_file_path]

        else:
            with open(vertex_file_path, "r") as file:
                vertex_src = file.readlines()
            with open(fragment_file_path, "r") as file:
                fragment_src = file.readlines()

            shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                    compileShader(fragment_src, GL_FRAGMENT_SHADER))

            self.shader_dict[shader_key] = shader

            return shader

    def load_texture(self, texture_file_path):

        texture_key = texture_file_path

        if texture_key in self.textures:
            return self.textures[texture_key]

        else:
            texture = Texture(texture_file_path)
            self.textures[texture_key] = texture
            return texture

    def mouse_button_callback(self, window, button, action, mods):

        if action == glfw.PRESS:

            x, y = glfw.get_cursor_pos(window)
            print(f"Mouse button {button} pressed at {x}, {y}")

    def main_loop(self):

        dt = 0
        last_time = glfw.get_time()

        while not glfw.window_should_close(self.window):

            dt = last_time - self.last_time
            last_time = glfw.get_time()

            glfw.poll_events()
            self.manage_input(dt)

            for object in self.dynamic_objects:
                object.update(dt)
            self.render()

        self.quit()

    def manage_input(self, dt: float):

        if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(self.window, True)
            return

        speed = 2.0
        distance = speed * dt
        roll_speed = np.pi / 2
        roll_angle = roll_speed * dt
        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS:
            self.camera.translate_forward(distance)
        elif glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS:
            self.camera.translate_forward(-distance)

        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS:
            self.camera.translate_left(distance)
        elif glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS:
            self.camera.translate_left(-distance)

        if glfw.get_key(self.window, glfw.KEY_SPACE) == glfw.PRESS:
            self.camera.translate_up(distance)
        elif glfw.get_key(self.window, glfw.KEY_C) == glfw.PRESS:
            self.camera.translate_up(-distance)

        if glfw.get_key(self.window, glfw.KEY_Q) == glfw.PRESS:
            self.camera.rotate_roll(roll_angle)
        elif glfw.get_key(self.window, glfw.KEY_E) == glfw.PRESS:
            self.camera.rotate_roll(-roll_angle)

        if glfw.get_key(self.window, glfw.KEY_F1) == glfw.PRESS:
            if not self.f1_state_flag:
                self.toggle_mouse_cursor()
                self.f1_state_flag = True
        else:
            self.f1_state_flag = False

        self.camera.recalculate_view_matrix()
        self.camera.update_view_matrix()

        if glfw.get_key(self.window, glfw.KEY_P) == glfw.PRESS:
            print(f"pos:  {self.camera.position}")
            print(f"view: {self.camera.view_direction}")
            print(f"left: {self.camera.left_direction}")
            print(f"up:   {self.camera.up_direction}")
            print(f"view matrix:\n{self.camera.view_matrix}\n")

    def toggle_mouse_cursor(self) -> None:

        self.mouse_cursor_enabled = not self.mouse_cursor_enabled
        if glfw.get_input_mode(self.window, glfw.CURSOR) == glfw.CURSOR_DISABLED:
            glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_NORMAL)
        else:
            glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    def render(self):

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for object in self.static_objects:
            object.render()
        for object in self.dynamic_objects:
            object.render()

        glfw.swap_buffers(self.window)

    def quit(self):

        for object in self.static_objects:
            object.destroy()
        for object in self.dynamic_objects:
            object.destroy()

        for texture in self.textures:
            texture.destroy()

        for shader in self.shaders:
            shader.destroy()

        glfw.terminate()



if __name__ == "__main__":

    app = App()
    app.main_loop()
