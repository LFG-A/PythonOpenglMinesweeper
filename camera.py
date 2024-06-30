import numpy as np
from OpenGL.GL import *

class Camera:

    def __init__(self,
                 shader,
                 fov: float = np.radians(110),
                 screen_size: tuple = (1920, 1080),
                 near: float = 0.1,
                 far: float = 100.0,
                 position=np.array([-5, 0, 0], dtype=np.float32),
                 view_direction=np.array([1, 0, 0], dtype=np.float32),
                 left_direction=np.array([0, 1, 0], dtype=np.float32),
                 up_direction=np.array([0, 0, 1], dtype=np.float32)):

        self.shader = shader

        self.fov = fov
        self.screen_size = screen_size
        self.near = near
        self.far = far

        self.position = position
        self.view_direction = view_direction
        self.left_direction = left_direction
        self.up_direction = up_direction

        self.recalculate_projection_matrix()
        self.recalculate_view_matrix()

        if self.shader is not None:
            self.projectionMatrixLocation = glGetUniformLocation(self.shader, "projection")
            self.update_projection_matrix()

            self.viewMatrixLocation = glGetUniformLocation(self.shader, "view")
            self.update_view_matrix()

    def get_projection_matrix(self) -> np.ndarray:

        return self.projection_matrix

    def recalculate_projection_matrix(self):

        aspect = self.screen_size[0]/self.screen_size[1]
        f = 1.0 / np.tan(self.fov / 2.0)
        a = (self.far + self.near) / (self.near - self.far)
        b = (2.0 * self.far * self.near) / (self.near - self.far)
        self.projection_matrix = np.array([[f / aspect, 0, 0, 0],
                                           [0, f, 0, 0],
                                           [0, 0, a, -1],
                                           [0, 0, b, 0]], dtype=np.float32)

    def update_projection_matrix(self):

        glUniformMatrix4fv(self.projectionMatrixLocation, 1, GL_FALSE, self.projection_matrix)

    def get_view_matrix(self) -> np.ndarray:

        return self.view_matrix

    def recalculate_view_matrix(self):

        self.view_matrix = np.array([[self.view_direction[0], self.left_direction[0], self.up_direction[0], -self.position[0]],
                                     [self.view_direction[1], self.left_direction[1], self.up_direction[1], -self.position[1]],
                                     [self.view_direction[2], self.left_direction[2], self.up_direction[2], -self.position[2]],
                                     [0, 0, 0, 1]], dtype=np.float32)

    def update_view_matrix(self):

        glUniformMatrix4fv(self.viewMatrixLocation, 1, GL_TRUE, self.view_matrix)

    def translate_forward(self, distance: float):

        self.position += distance * self.view_direction

    def translate_left(self, distance: float):

        self.position += distance * self.left_direction

    def translate_up(self, distance: float):

        self.position += distance * self.up_direction

    def rotate_roll(self, angle: float):

        self.apply_rotation_matrix(self.rotation_matrix(self.view_direction, angle))

    def rotate_pitch(self, angle: float):

        self.apply_rotation_matrix(self.rotation_matrix(self.left_direction, angle))

    def rotate_yaw(self, angle: float):

        self.apply_rotation_matrix(self.rotation_matrix(self.up_direction, angle))

    def apply_rotation_matrix(self, rotation_matrix: np.array):

        self.view_direction = rotation_matrix.dot(self.view_direction)
        self.left_direction = rotation_matrix.dot(self.left_direction)
        self.up_direction = rotation_matrix.dot(self.up_direction)

    def get_ray(self) -> tuple:

        # ray is a vector starting at the camera position and pointing into the direction of the camera
        # the ray is defined by a point and a direction vector

        return self.position, self.view_direction

    def get_ray_through_screen_pos(self, x, y):
        # Convert screen coordinates to NDC
        ndc_x = (2.0 * x) / self.screen_size[0] - 1.0
        ndc_y = 1.0 - (2.0 * y) / self.screen_size[1]

        # Create the NDC coordinates
        ndc_near = np.array([ndc_x, ndc_y, -1.0, 1.0])
        ndc_far = np.array([ndc_x, ndc_y, 1.0, 1.0])

        # Inverse view matrix to get camera coordinates
        inv_view_matrix = np.linalg.inv(self.view_matrix)
        camera_near = inv_view_matrix.dot(ndc_near)
        camera_far = inv_view_matrix.dot(ndc_far)

        camera_near /= camera_near[3]  # Perspective divide
        camera_far /= camera_far[3]    # Perspective divide

        # Inverse projection matrix to get WCS coordinates
        inv_proj_matrix = np.linalg.inv(self.projection_matrix)
        WCS_near = inv_proj_matrix.dot(camera_near)
        WCS_far = inv_proj_matrix.dot(camera_far)

        WCS_near /= WCS_near[3]  # Perspective divide
        WCS_far /= WCS_far[3]    # Perspective divide

        # Calculate ray direction
        ray_dir = WCS_far[:3] - WCS_near[:3]
        ray_dir /= np.linalg.norm(ray_dir)  # Normalize direction

        return self.position, ray_dir

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
        a = np.deg2rad(angle)
        cos_a = np.cos(a)
        sin_a = np.sin(a)

        # Berechne die Rotationsmatrix unter Verwendung der Rodrigues-Formel
        R = np.array([
            [cos_a + x*x*(1 - cos_a), x*y*(1 - cos_a) - z*sin_a, x*z*(1 - cos_a) + y*sin_a],
            [y*x*(1 - cos_a) + z*sin_a, cos_a + y*y*(1 - cos_a), y*z*(1 - cos_a) - x*sin_a],
            [z*x*(1 - cos_a) - y*sin_a, z*y*(1 - cos_a) + x*sin_a, cos_a + z*z*(1 - cos_a)]
        ])

        return R

    def get_screen_corners(self):

        f = self.near
        fov = self.fov
        aspect_ratio = self.screen_size[0] / self.screen_size[1]
        corners = [[f, f * np.tan(np.radians(fov / 2)), f * np.tan(np.radians(fov / 2)) / aspect_ratio],
                    [f, -f * np.tan(np.radians(fov / 2)), f * np.tan(np.radians(fov / 2)) / aspect_ratio],
                    [f, -f * np.tan(np.radians(fov / 2)), -f * np.tan(np.radians(fov / 2)) / aspect_ratio],
                    [f, f * np.tan(np.radians(fov / 2)), -f * np.tan(np.radians(fov / 2)) / aspect_ratio]]
        return corners






















def debug_plot_camera(camera):

    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(15, 5))

    # world coordinate system
    WCS = fig.add_subplot(131, projection="3d")  # 1 row, 3 columns, first plot
    WCS.set_title("World Coordinate System")

    WCS.scatter(0, 0, 0, marker='o', c="black", alpha=0.2, s=500)

    # vertices
    v_x,v_y,v_z = [],[],[]
    wcs_vertices = []
    for iy in range(11):
        for ix in range(11):
            v_x.append(ix)
            v_y.append(iy)
            v_z.append(0)
            wcs_vertices.append(np.array([ix, iy, 0]))
    WCS.scatter(v_x, v_y, v_z)

    # camera
    p_x, p_y = camera.screen_size[0], camera.screen_size[1]
    pos, forward_through_screen_pos = camera.get_ray_through_screen_pos(p_x/2, p_y/2)
    pos, forward = camera.get_ray()
    left, up = camera.left_direction, camera.up_direction
    if np.all(forward_through_screen_pos == forward):
        forward = forward_through_screen_pos
    else:
        print("TODO: fix get_ray_through_screen_pos")
    WCS.quiver(pos[0], pos[1], pos[2], forward[0], forward[1], forward[2], color='r')
    WCS.quiver(pos[0], pos[1], pos[2], left[0], left[1], left[2], color='g')
    WCS.quiver(pos[0], pos[1], pos[2], up[0], up[1], up[2], color='b')

    WCS.set_xlabel('X')
    WCS.set_ylabel('Y')
    WCS.set_zlabel('Z')

    WCS.axis('equal')

    # camera coordinate system
    CCS = fig.add_subplot(132, projection="3d")  # 1 row, 3 columns, second plot
    CCS.set_title("Camera Coordinate System")

    # vertices
    view_matrix = camera.get_view_matrix()
    ccs_vertices = []
    for vertex in wcs_vertices:
        vertex = np.append(vertex, 1)
        ccs_vertices.append(view_matrix.dot(vertex)) # TODO: fix this, it is not correct
    ccs_vertices = np.array(ccs_vertices)
    CCS.scatter(ccs_vertices[:, 0], ccs_vertices[:, 1], ccs_vertices[:, 2])

    # near and far plane
    fov_half = camera.fov/2
    ratio = camera.screen_size[0]/camera.screen_size[1]
    for distance in [camera.near, 1]:
        frame_x = distance
        frame_y = distance * np.tan(fov_half)
        frame_z = frame_y/ratio
        CCS.plot([frame_x, frame_x, frame_x, frame_x, frame_x], [-frame_y, -frame_y, frame_y, frame_y, -frame_y], [-frame_z, frame_z, frame_z, -frame_z, -frame_z], 'k-')

    # camera
    CCS.quiver(0, 0, 0, 1, 0, 0, color='r')
    CCS.quiver(0, 0, 0, 0, 1, 0, color='g')
    CCS.quiver(0, 0, 0, 0, 0, 1, color='b')

    CCS.set_xlabel('X')
    CCS.set_ylabel('Y')
    CCS.set_zlabel('Z')

    CCS.axis('equal')

    # screen coordinate system
    SCS = fig.add_subplot(133)  # 1 row, 3 columns, third plot
    SCS.set_title("Screen Coordinate System")

    SCS.plot([0, p_x, p_x, 0, 0], [0, 0, p_y, p_y, 0], 'k-')

    SCS.set_xlabel('X')
    SCS.set_xlim(0, p_x)
    SCS.set_ylabel('Y')
    SCS.set_ylim(0, p_y)
    SCS.set_aspect(aspect=16/9, adjustable='box')

    SCS.axis('equal')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":

    screen_size = (1920, 1080)
    pos = np.array([5, 5, 5], dtype=np.float32)
    v = np.array([0, 0, -1], dtype=np.float32)
    l = np.array([0, 1, 0], dtype=np.float32)
    u = np.array([1, 0, 0], dtype=np.float32)
    camera = Camera(None, np.radians(110), screen_size, 0.1, 100.0, pos, v, l, u)

    debug_plot_camera(camera)
