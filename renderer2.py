# TODO:: shaders

from py3dUtility import *
from functools import cmp_to_key
import tkinter as tk
import numpy as np
import time

class MainRenderer:
    def __init__(self, root: tk.Tk, HEIGHT: int, WIDTH: int):
        self.HEIGHT = HEIGHT
        self.WIDTH = WIDTH
        self.canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH)
        self.canvas.pack()
        self.world_up = [0,1,0]
        self.lines = (0,0,0,0)

        self.projection_matrix = make_projection_matrix(90, HEIGHT, WIDTH)
        MainRenderer.INSTANCE = self

    def set_current_camera(self, camera):
        self.camera = camera

    def resize_window(self, new_height: int, new_width: int):
        self.HEIGHT = new_height
        self.WIDTH = new_width
        self.canvas["height"] = new_height
        self.canvas["width"] = new_width


    def world_to_screen(self, p: list):
        p = matrix_vector_mult(p,self.projection_matrix)

        if(p[3] != 0):
            p[0] /= p[3]
            p[1] /= p[3]
            p[2] /= p[3]

        p[0] *= self.WIDTH/2
        p[1] *= self.HEIGHT/2
        return p

    def _is_triangle_rendered(self, p1, p2, p3):
        l1 = p2-p1
        l2 = p3-p1

        normal = np.cross(l1[:-1],l2[:-1])
        normal = normalized_old(normal)

        p_cam = p1[:-1]-self.camera.transform.position
        if(np.dot(normal, p_cam) < 0):
            return True
        else:
            return False

    def _draw_triangle(self, p1, p2, p3, fill="black", outline="white"):

        #remap coords from [0;height, 0;width] to [-(height/2);height/2, -(width/2);width/2]
        p1_interp = [
            np.interp(p1[0], [-(self.WIDTH)/2, self.WIDTH/2], [0,self.WIDTH]),
            np.interp(p1[1], [-(self.HEIGHT)/2, self.HEIGHT/2], [0,self.HEIGHT])
        ]
        p2_interp = [
            np.interp(p2[0], [-(self.WIDTH)/2, self.WIDTH/2], [0,self.WIDTH]),
            np.interp(p2[1], [-(self.HEIGHT)/2, self.HEIGHT/2], [0,self.HEIGHT])
        ]
        p3_interp = [
            np.interp(p3[0], [-(self.WIDTH)/2, self.WIDTH/2], [0,self.WIDTH]),
            np.interp(p3[1], [-(self.HEIGHT)/2, self.HEIGHT/2], [0,self.HEIGHT])
        ]

        a = self.canvas.create_polygon(p1_interp[0], p1_interp[1], p2_interp[0], p2_interp[1], p3_interp[0], p3_interp[1], fill=fill, outline=outline)
        #a = self.canvas.create_polygon(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], fill=fill, outline=outline)

    @property
    def screen_center(self):
        return (self.WIDTH/2, self.HEIGHT/2)

    def UI_draw_line(self, lines):
        self.lines

    def draw_frame(self, entities: EnvironmentEntity):
        self.canvas.delete("all")

        triangles_to_draw = []

        up = np.array([0,1,0])
        look_dir = self.camera.transform.forward
        target = self.camera.transform.position + look_dir[:-1]
        camera_matrix = make_look_at_point_matrix(self.camera.transform.position, target, up)

        view_matrix = matrix_inverse(camera_matrix)

        for e in entities:
            for m in e.get_meshes():
                for t in m:
                    
                    mat_world = e.transform.world_matrix()
#
                    #p1_transformed = matrix_vector_mult(t[0], mat_world)
                    #p2_transformed = matrix_vector_mult(t[1], mat_world)
                    #p3_transformed = matrix_vector_mult(t[2], mat_world)
                    #t[0] = np.append(t[0], 1)
                    #t[1] = np.append(t[1], 1)
                    #t[2] = np.append(t[2], 1)

                    rot_mat = make_rotation_matrix(e.transform.rotation)
                    p1_rotated = matrix_vector_mult(np.append(t[0], 1), rot_mat)
                    p2_rotated = matrix_vector_mult(np.append(t[1], 1), rot_mat)
                    p3_rotated = matrix_vector_mult(np.append(t[2], 1), rot_mat)

                    
                    p1_transformed = p1_rotated + np.append(e.transform.position, 1)
                    p2_transformed = p2_rotated + np.append(e.transform.position, 1)
                    p3_transformed = p3_rotated + np.append(e.transform.position, 1)


                    if(not self._is_triangle_rendered(p1_transformed, p2_transformed, p3_transformed)):
                        continue

                    p1_viewed = matrix_vector_mult(p1_transformed, view_matrix)
                    p2_viewed = matrix_vector_mult(p2_transformed, view_matrix)
                    p3_viewed = matrix_vector_mult(p3_transformed, view_matrix)

                    #revert z axis

                    p1_p = self.world_to_screen(p1_viewed)
                    p2_p = self.world_to_screen(p2_viewed)
                    p3_p = self.world_to_screen(p3_viewed)

                    triangles_to_draw.append([p1_p, p2_p, p3_p])

        def sort_triangles(t1, t2):
            z1 = (t1[0][2]+t1[1][2]+t1[2][2])/3    
            z2 = (t2[0][2]+t2[1][2]+t2[2][2])/3
            result = z1 > z2
            if(result):
                return 1
            elif(not result):
                return -1
            else:
                return 0
            
        triangles_to_draw = sorted(triangles_to_draw, key=cmp_to_key(sort_triangles))

        for t in triangles_to_draw:
            self._draw_triangle(t[0], t[1], t[2])
        