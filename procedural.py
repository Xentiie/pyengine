from tkinter.constants import CURRENT
from py3dEngine import py3DEngine
from py3dUtility import *
from renderer2 import MainRenderer
import numpy as np
from noise import snoise2

class EController(Module):
	def update(self):
		self.entity.transform.rotation[0] += py3DEngine.delta_time * 10

mesh_cube = [                                                            # Mesh d'un cube
        # SOUTH
		[[0, 0, 0],    [0, 1, 0],    [1, 1, 0]],
		[[0, 0, 0],    [1, 1, 0],    [1, 0, 0]],

		# EAST                                                      
		[[1, 0, 0],    [1, 1, 0],    [1, 1, 1]],
		[[1, 0, 0],    [1, 1, 1],    [1, 0, 1]],

		# NORTH                                                     
		[[1, 0, 1],    [1, 1, 1],    [0, 1, 1]],
		[[1, 0, 1],    [0, 1, 1],    [0, 0, 1]],

		# WEST                                                      
		[[0, 0, 1],    [0, 1, 1],    [0, 1, 0]],
		[[0, 0, 1],    [0, 1, 0],    [0, 0, 0]],

		# TOP                                                       
		[[0, 1, 0],    [0, 1, 1],    [1, 1, 1]],
		[[0, 1, 0],    [1, 1, 1],    [1, 1, 0]],

		# BOTTOM                                                    
		[[1, 0, 1],    [0, 0, 1],    [0, 0, 0]],
		[[1, 0, 1],    [0, 0, 0],    [1, 0, 0]]

]

dims = (100,100)
points = np.empty((dims[0] + 1) * (dims[1] + 1), dtype=object)
mesh = []

i = 0
for z in range(dims[1] + 1):
	for x in range(dims[0] + 1):
		points[i] = [x, snoise2(x,z) / 2, z]
		i += 1

triangles = np.empty(dims[0] * dims[1] * 6, dtype=int)
ti = 0
vi = 0
for y in range(dims[1]):
	for x in range(dims[0]):
		triangles[ti] = vi
		triangles[ti + 1] = vi + dims[0] + 1
		triangles[ti + 2] = vi + 1
		triangles[ti + 3] = vi + 1
		triangles[ti + 4] = vi + dims[0] + 1
		triangles[ti + 5] = vi + dims[0] + 2
		vi += 1
		ti += 6

mesh = []
i = 0
while i < len(triangles):
	mesh.append([points[triangles[i]], points[triangles[i + 1]], points[triangles[i + 2]]])
	i += 3

entity = EnvironmentEntity(meshes=[mesh], name='Procedural')
entity.transform.position = np.array([-5,-5,20])
#entity.add_module(EController())


cube_entity1 = EnvironmentEntity(meshes=[mesh_cube], name='cube1')
cube_entity1.transform.position = np.array([10,10,20], dtype=np.float32)
cube_entity1.transform.rotation = np.array([100.0,0.0,50.0])
cube_entity1.add_module(EController())

camera_entity = Entity(name='camera')
camera_entity.transform.position = np.array([0.0,0.0,0.0])
engine = py3DEngine(800, 800)
engine.main_renderer.set_current_camera(camera_entity)
engine.start_game()