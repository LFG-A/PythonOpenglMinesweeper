import numpy as np
from OpenGL.GL import *

class Camera:

    def __init__(self,
                 shader,
                 fov,
                 screen_size,
                 near,
                 far,
                 position,
                 euler_rotation):

        self.shader = shader

        self.fov = fov
        self.screen_size = screen_size
        self.near = near
        self.far = far

        self.position = position
        self.euler_rotation = euler_rotation

        if self.shader is not None:
            self.projectionMatrixLocation = glGetUniformLocation(self.shader, "projection")
            self.update_projection()

            self.viewMatrixLocation = glGetUniformLocation(self.shader, "view")
            self.update_view()
        else:
            self.recalculate_projection_matrix()
            self.recalculate_view_matrix()

    def __setattr__(self, name: str, value) -> None:
        # raise AttributeError(f"Attribute '{name}' is read-only")
        super().__setattr__(name, value)

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

    def update_projection(self):

        self.recalculate_projection_matrix()

        glUniformMatrix4fv(self.projectionMatrixLocation, 1, GL_FALSE, self.projection_matrix)

    def get_view_matrix(self) -> np.ndarray:

        return self.view_matrix

    def recalculate_view_matrix(self):

        self.view_matrix = np.array([[1, 0, 0, self.position[0]],
                                     [0, 1, 0, self.position[1]],
                                     [0, 0, 1, self.position[2]],
                                     [0, 0, 0, 1]], dtype=np.float32)

    def update_view(self):

        self.recalculate_view_matrix()

        glUniformMatrix4fv(self.viewMatrixLocation, 1, GL_TRUE, self.view_matrix)

    def get_ray(self) -> tuple:

        # ray is a vector starting at the camera position and pointing into the direction of the camera
        # the ray is defined by a point and a direction vector

        # the direction is the negative z-axis of the camera
        direction = np.array([0, 0, 1], dtype=np.float32)

        return self.position, direction

    def get_ray_through_screen_pos(self, x, y):
        # Convert screen coordinates to NDC
        ndc_x = (2.0 * x) / self.screen_size[0] - 1.0
        ndc_y = 1.0 - (2.0 * y) / self.screen_size[1]

        # Create the NDC coordinates
        ndc_near = np.array([ndc_x, ndc_y, -1.0, 1.0])
        ndc_far = np.array([ndc_x, ndc_y, 1.0, 1.0])

        # Inverse view matrix to get camera coordinates
        inv_view_matrix = np.linalg.inv(self.view_matrix)
        camera_near = np.dot(inv_view_matrix, ndc_near)
        camera_far = np.dot(inv_view_matrix, ndc_far)

        camera_near /= camera_near[3]  # Perspective divide
        camera_far /= camera_far[3]    # Perspective divide

        # Inverse projection matrix to get world coordinates
        inv_proj_matrix = np.linalg.inv(self.projection_matrix)
        world_near = np.dot(inv_proj_matrix, camera_near)
        world_far = np.dot(inv_proj_matrix, camera_far)

        world_near /= world_near[3]  # Perspective divide
        world_far /= world_far[3]    # Perspective divide

        # Calculate ray direction
        ray_dir = world_far[:3] - world_near[:3]
        ray_dir /= np.linalg.norm(ray_dir)  # Normalize direction

        return self.position, ray_dir

if __name__ == "__main__":

    screen_size = (1920, 1080)
    pos = np.array([-5, -5, -5], dtype=np.float32)
    rot = np.array([0, 0, 0], dtype=np.float32)
    camera = Camera(None, np.radians(90), screen_size, 0.1, 100.0, pos, rot)

    import matplotlib.pyplot as plt

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    x,y,z = [],[],[]
    for iy in range(11):
        for ix in range(11):
            x.append(ix)
            y.append(iy)
            z.append(0)
    ax.scatter(x, y, z)

    pos, dir = camera.get_ray()
    ax.quiver(pos[0], pos[1], pos[2], dir[0], dir[1], dir[2], color='b')
    pos, dir = camera.get_ray_through_screen_pos(0, 0)
    ax.quiver(pos[0], pos[1], pos[2], dir[0], dir[1], dir[2], color='r')

    camera.position = np.array([0, 0, 0], dtype=np.float32)

    pos, dir = camera.get_ray()
    ax.quiver(pos[0], pos[1], pos[2], dir[0], dir[1], dir[2], color='b')
    pos, dir = camera.get_ray_through_screen_pos(0, 0)
    ax.quiver(pos[0], pos[1], pos[2], dir[0], dir[1], dir[2], color='r')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    ax.axis('equal')

    plt.show()
