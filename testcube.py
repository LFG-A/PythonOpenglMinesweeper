import numpy as np
from OpenGL.GL import *


class Transform:

    def __init__(self, position=np.array([0.0, 0.0, 0.0]), euler_rotation=np.array([0.0, 0.0, 0.0]), scale=np.array([1.0, 1.0, 1.0])):
    
        self.position = position
        self.rotation = euler_rotation
        self.scale = scale

        self.update_transformation_matrix()

    def update_transformation_matrix(self) -> np.array:

        t = self.position
        r = self.rotation
        s = self.scale
        tx, ty, tz = t[0], t[1], t[2]
        sx, sy, sz = s[0], s[1], s[2]
        rx, ry, rz = np.radians(r[0]), np.radians(r[1]), np.radians(r[2])

        translation_matrix = np.array([[1, 0, 0, tx],
                                        [0, 1, 0, ty],
                                        [0, 0, 1, tz],
                                        [0, 0, 0, 1]])
        R_x = Transform.rotation_matrix_x(rx)
        R_x = np.vstack([np.hstack([R_x, np.array([[0], [0], [0]])]), np.array([0, 0, 0, 1])])
        R_y = Transform.rotation_matrix_y(ry)
        R_y = np.vstack([np.hstack([R_y, np.array([[0], [0], [0]])]), np.array([0, 0, 0, 1])])
        R_z = Transform.rotation_matrix_z(rz)
        R_z = np.vstack([np.hstack([R_z, np.array([[0], [0], [0]])]), np.array([0, 0, 0, 1])])
        scale_matrix = np.array([[sx, 0, 0, 0],
                                 [0, sy, 0, 0],
                                 [0, 0, sz, 0],
                                 [0, 0, 0, 1]])

        self.transformation_matrix = translation_matrix @ R_z @ R_y @ R_x @ scale_matrix

    def get_transformation_matrix(self) -> np.array:

        return self.transformation_matrix

    @staticmethod
    def to_euler_angles(forward: np.array, left: np.array, up: np.array) -> np.array:

        # Calculate the yaw angle
        yaw = np.arctan2(forward[2], forward[0])

        # Calculate the pitch angle
        pitch = np.arcsin(forward[1])

        # Calculate the roll angle
        roll = np.arctan2(left[1], up[1])

        return np.array([yaw, pitch, roll])

    @staticmethod
    def rotation_matrix_x(phi):

        c = np.cos(phi)
        s = np.sin(phi)

        return np.array([
            [1, 0, 0],
            [0, c, -s],
            [0, s, c]
        ])

    @staticmethod
    def rotation_matrix_y(phi):

        c = np.cos(phi)
        s = np.sin(phi)

        return np.array([
            [c, 0, s],
            [0, 1, 0],
            [-s, 0, c]
        ])

    @staticmethod
    def rotation_matrix_z(phi):

        c = np.cos(phi)
        s = np.sin(phi)

        return np.array([
            [c, -s, 0],
            [s, c, 0],
            [0, 0, 1]
        ])

    def __str__(self):

        return f"Position: {self.position}, Rotation: {self.rotation}, Scale: {self.scale}"

class Mesh:

    @staticmethod
    def get_basic_cube(app, size=1) -> "Mesh":

        a = size/2
        # x, y, z, r, g, b, a
        vertices = [
            # Front
            a, a, a, 1, 0, 0, 1, # 0
            a, a,-a, 1, 0, 0, 1, # 1
            a,-a, a, 1, 0, 0, 1, # 2
            a,-a,-a, 1, 0, 0, 1, # 3
            a,-a, a, 1, 0, 0, 1, # 2
            a, a,-a, 1, 0, 0, 1, # 1
            # Left
            -a, a, a, 0, 1, 0, 1, # 4
            -a, a,-a, 0, 1, 0, 1, # 5
             a, a, a, 0, 1, 0, 1, # 0
             a, a,-a, 0, 1, 0, 1, # 1
             a, a, a, 0, 1, 0, 1, # 0
            -a, a,-a, 0, 1, 0, 1, # 5
            # Top
             a, a, a, 0, 0, 1, 1, # 0
             a,-a, a, 0, 0, 1, 1, # 2
            -a, a, a, 0, 0, 1, 1, # 4
            -a,-a, a, 0, 0, 1, 1, # 6
            -a, a, a, 0, 0, 1, 1, # 4
             a,-a, a, 0, 0, 1, 1, # 2
            # Back
            -a,-a, a, 1, 0, 0, 0.5, # 6
            -a,-a,-a, 1, 0, 0, 0.5, # 7
            -a, a, a, 1, 0, 0, 0.5, # 4
            -a, a,-a, 1, 0, 0, 0.5, # 5
            -a, a, a, 1, 0, 0, 0.5, # 4
            -a,-a,-a, 1, 0, 0, 0.5, # 7
            # Right
             a,-a, a, 0, 1, 0, 0.5, # 2
             a,-a,-a, 0, 1, 0, 0.5, # 3
            -a,-a, a, 0, 1, 0, 0.5, # 6
            -a,-a,-a, 0, 1, 0, 0.5, # 7
            -a,-a, a, 0, 1, 0, 0.5, # 6
             a,-a,-a, 0, 1, 0, 0.5, # 3
            # Bottom
             a,-a,-a, 0, 0, 1, 0.5, # 3
             a, a,-a, 0, 0, 1, 0.5, # 1
            -a,-a,-a, 0, 0, 1, 0.5, # 7
            -a, a,-a, 0, 0, 1, 0.5, # 5
            -a,-a,-a, 0, 0, 1, 0.5, # 7
             a, a,-a, 0, 0, 1, 0.5, # 1
            ]
        vertex_count = len(vertices)//7
        vertices = np.array(vertices, dtype=np.float32)

        if app is None:
            shader = None
        else:
            shader = app.load_shader("shaders/3d_fragColor_vertex_shader.vs", "shaders/3d_fragColor_fragment_shader.fs")
        mesh = Mesh(shader=shader, vertices=vertices, vertex_count=vertex_count)

        return mesh

    @staticmethod
    def create_vao_vbo(vertices: np.array) -> tuple[int]:

        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)

        # Vertices
        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        # position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        # texture
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        # normal
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))

        return vao, vbo

    def __init__(self, shader, vertices = None, vertex_count = None) -> None:

        if vertex_count is None:
            raise ValueError("vertex_count must be provided if vertices is provided")
        self.vertex_count = vertex_count

        if shader is not None:
            self.vao = glGenVertexArrays(1)
            glBindVertexArray(self.vao)

            # Vertices
            self.vbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
            # position
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 28, ctypes.c_void_p(0))
            # color
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 28, ctypes.c_void_p(12))

            # Compile shader
            self.shader = shader
        else:
            self.vao = None
            self.vbo = None
            self.shader = None

    def destroy(self):

        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

    def render(self, model_matrix) -> None:

        # Use shader
        glUseProgram(self.shader)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL) # Normal mode
        # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE) # Wireframe mode

        model_location = glGetUniformLocation(self.shader, "model")
        glUniformMatrix4fv(model_location, 1, GL_FALSE, model_matrix)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        glBindVertexArray(0)

class MeshRenderer:

    def __init__(self,
                 mesh: Mesh,
                 material = None,
                 lighting = None,
                 probes = None) -> None:

        self.mesh = mesh
        self.material = material
        self.lighting = lighting
        self.probes = probes

    def render(self) -> None:

        glBindVertexArray(mesh.vao)
        glDrawArrays(GL_TRIANGLES, 0, mesh.vertex_count)

        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE) # Wireframe mode
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL) # Normal mode

class Object:

    @staticmethod
    def get_basic_cube(app):

        basic_cube_mesh = Mesh.get_basic_cube(app)
        basic_cube = Object(name="Basic Cube", mesh=basic_cube_mesh)

        return basic_cube

    def __init__(self, name: str = "noname", transform: Transform = Transform(), mesh: Mesh = None):

        self.name = name
        self.transform = transform

        self.mesh = mesh
        if mesh is not None:
            self.render_ref = mesh.render
        else:
            self.render_ref = self.pass_fnc

    def render(self):

        self.mesh.render(self.transform.get_transformation_matrix())

    def wants_update(self):

        return False

    def update(self, delta_time: float):

        pass

    def destroy(self):

        if self.mesh is not None:
            self.mesh.destroy()



if __name__ == "__main__":

    cube = Object.get_basic_cube(app=None)

    print(cube.name)
    print(cube.transform)
    print(cube.transform.get_transformation_matrix())
