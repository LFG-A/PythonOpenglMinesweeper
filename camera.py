import numpy as np
from OpenGL.GL import *



class Camera:

    @staticmethod
    def rotation_matrix(axis: np.array, angle: float) -> np.array:
        """
        Berechnet die Rotationsmatrix für die Rotation um eine gegebene Achse um ein gegebenen Winkel.

        :param angle: Der Rotationswinkel in Grad
        :param axis: Ein 3D-Vektor (NumPy-Array), der die Rotationsachse definiert
        :return: Eine 3x3-Rotationsmatrix
        """
        # Normiere die Achse
        axis = axis / np.linalg.norm(axis)

        # Extrahiere die Komponenten des normierten Achsenvektors
        x, y, z = axis

        # Berechne die Sinus- und Kosinuswerte des Winkels
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)

        # Berechne die Rotationsmatrix unter Verwendung der Rodrigues-Formel
        R = np.array([
            [cos_a + x*x*(1 - cos_a), x*y*(1 - cos_a) - z*sin_a, x*z*(1 - cos_a) + y*sin_a],
            [y*x*(1 - cos_a) + z*sin_a, cos_a + y*y*(1 - cos_a), y*z*(1 - cos_a) - x*sin_a],
            [z*x*(1 - cos_a) - y*sin_a, z*y*(1 - cos_a) + x*sin_a, cos_a + z*z*(1 - cos_a)]
        ])

        return R

    def __init__(self,
                 shader =None,
                 fov: float =np.radians(90),
                 screen_size: tuple =(1920, 1080),
                 near: float =0.1,
                 far: float =100.0,
                 position:np.array =np.array([0, 0, 0], dtype=np.float32),
                 view_direction:np.array =np.array([1, 0, 0], dtype=np.float32),
                 left_direction:np.array =np.array([0, 1, 0], dtype=np.float32),
                 up_direction:np.array =np.array([0, 0, 1], dtype=np.float32)):

        self.shader = shader

        self.fov = fov
        self.screen_size = screen_size
        self.aspect = screen_size[0] / screen_size[1]
        self.near = near
        self.far = far

        self.position = position
        self.view_direction = view_direction
        self.left_direction = left_direction
        self.up_direction = up_direction

        self.recalculate_projection_matrix()
        self.recalculate_view_matrix()

        if self.shader is not None:
            self.projectionMatrixLocation = glGetUniformLocation(shader, "projection")
            self.update_projection_matrix()

            self.viewMatrixLocation = glGetUniformLocation(shader, "view")
            self.update_view_matrix()

    def recalculate_projection_matrix(self):

        near, far = self.near, self.far
        denominator = near - far
        f = 1.0 / np.tan(self.fov / 2.0)
        a = (far + near) / denominator
        b = (2.0 * far * near) / denominator
        self.projection_matrix = np.array([[f / self.aspect, 0, 0, 0],
                                           [0, f, 0, 0],
                                           [0, 0, a, -1],
                                           [0, 0, b, 0]], dtype=np.float32)

    def update_projection_matrix(self):

        glUniformMatrix4fv(self.projectionMatrixLocation, 1, GL_FALSE, self.projection_matrix)

    def recalculate_view_matrix(self):

        self.view_matrix = np.array([
            [-self.left_direction[0], self.up_direction[0], -self.view_direction[0], -self.position[0]],
            [-self.left_direction[1], self.up_direction[1], -self.view_direction[1], -self.position[1]],
            [-self.left_direction[2], self.up_direction[2], -self.view_direction[2], -self.position[2]],
            [0, 0, 0, 1]
        ], dtype=np.float32)

    def update_view_matrix(self):

        glUniformMatrix4fv(self.viewMatrixLocation, 1, GL_TRUE, self.view_matrix)

    def get_ray(self) -> tuple:

        return self.position, self.view_direction

    def get_ray_through_screen_pos(self, x, y):

        width, height = self.screen_size
        x_norm = (x/(width-1))*2-1
        y_norm = 1-(y/(height-1))*2

        fov_y = self.fov
        aspect = self.aspect

        yaw_angle = -np.arctan(x_norm * np.tan(fov_y / 2) * aspect)
        pitch_angle = np.arctan(y_norm * np.tan(fov_y / 2))

        direction = np.array([
            np.tan(yaw_angle),
            np.tan(pitch_angle),
            -1.0
        ])
        direction = direction / np.linalg.norm(direction)

        # Transform the direction from camera space to world space
        camera_rotation = np.column_stack((self.left_direction, self.up_direction, -self.view_direction))
        world_direction = camera_rotation.dot(direction)

        return self.position, world_direction

    def translate_forward(self, distance: float):

        self.position += distance * self.view_direction

    def translate_left(self, distance: float):

        self.position += distance * self.left_direction

    def translate_up(self, distance: float):

        self.position += distance * self.up_direction

    def rotate_roll(self, angle: float):

        rotation_matrix = self.rotation_matrix(self.view_direction, angle)

        self.left_direction = rotation_matrix.dot(self.left_direction)
        self.up_direction = rotation_matrix.dot(self.up_direction)

    def rotate_pitch(self, angle: float):

        rotation_matrix = self.rotation_matrix(self.left_direction, angle)

        self.view_direction = rotation_matrix.dot(self.view_direction)
        self.up_direction = rotation_matrix.dot(self.up_direction)

    def rotate_yaw(self, angle: float):

        rotation_matrix = self.rotation_matrix(self.up_direction, angle)

        self.view_direction = rotation_matrix.dot(self.view_direction)
        self.left_direction = rotation_matrix.dot(self.left_direction)

    def get_screen_corners(self):

        f = self.near
        fov = self.fov
        aspect_ratio = self.screen_size[0] / self.screen_size[1]
        corners = [[f, f * np.tan(np.radians(fov / 2)), f * np.tan(np.radians(fov / 2)) / aspect_ratio],
                    [f, -f * np.tan(np.radians(fov / 2)), f * np.tan(np.radians(fov / 2)) / aspect_ratio],
                    [f, -f * np.tan(np.radians(fov / 2)), -f * np.tan(np.radians(fov / 2)) / aspect_ratio],
                    [f, f * np.tan(np.radians(fov / 2)), -f * np.tan(np.radians(fov / 2)) / aspect_ratio]]
        return corners



if __name__ == "__main__":

    screen_size = (1920, 1080)
    camera_position = np.array([5, 5, 5], dtype=np.float32)
    camera_view_direction = np.array([0, 0, -1], dtype=np.float32)
    camera_left_direction = np.array([-1, 0, 0], dtype=np.float32)
    camera_up_direction = np.array([0, 1, 0], dtype=np.float32)
    camera = Camera(screen_size=screen_size, position=camera_position, view_direction=camera_view_direction, left_direction=camera_left_direction, up_direction=camera_up_direction)

    np.set_printoptions(precision=3, suppress=True)

    print(camera.projection_matrix)
    print(camera.view_matrix)

    print(camera.get_ray())
    print(camera.get_ray_through_screen_pos(960, 540))
    print(camera.get_ray_through_screen_pos(0, 0))
    print(camera.get_ray_through_screen_pos(1919, 1079))

    print("\nCamera movement:")
    camera.translate_forward(5)
    camera.rotate_roll(45)
    camera.recalculate_projection_matrix()
    camera.recalculate_view_matrix()

    print(camera.projection_matrix)
    print(camera.view_matrix)

    print(camera.get_ray())
    print(camera.get_ray_through_screen_pos(960, 540))
    print(camera.get_ray_through_screen_pos(0, 0))
    print(camera.get_ray_through_screen_pos(1919, 1079))
