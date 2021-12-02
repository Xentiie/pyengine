from os import name
from py3dEngine import py3DEngine
from py3dUtility import *
import numpy as np
import keyboard
from renderer2 import MainRenderer

class CameraController(Module):

	def __init__(self):
		self.speed = 20

	def update(self):
		pass
		#self.entity.transform.rotation[2] += py3DEngine.delta_time
#		if(keyboard.is_pressed("z")):
#			self.entity.transform.position -= self.entity.transform.forward[:-1]*py3DEngine.delta_time*self.speed
#		if(keyboard.is_pressed("s")):
#			self.entity.transform.position += self.entity.transform.forward[:-1]*py3DEngine.delta_time*self.speed
#		if(keyboard.is_pressed("q")):
#			self.entity.transform.position[0] += py3DEngine.delta_time*self.speed
#		if(keyboard.is_pressed("d")):
#			self.entity.transform.position[0] -= py3DEngine.delta_time*self.speed
#		if(keyboard.is_pressed("shift")):
#			self.entity.transform.position[1] -= py3DEngine.delta_time*self.speed
#		if(keyboard.is_pressed("space")):
#			self.entity.transform.position[1] += py3DEngine.delta_time*self.speed
#		if(keyboard.is_pressed("c")):
#			self.entity.transform.rotation[1] += py3DEngine.delta_time * 10
#		if(keyboard.is_pressed("x")):
#			self.entity.transform.rotation[1] -= py3DEngine.delta_time * 10
        
HEIGHT, WIDTH = 800,900

#ship_mesh = import_obj_file("C:/Users/Remi/Desktop/ship.obj")
teapot_mesh = import_obj_file("/Users/reclaire/Desktop/pyengine/teapot.obj")
mesh = [                                                            # Mesh d'un cube
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
#ship_entity = EnvironmentEntity(meshes=[ship_mesh], name='ship')
#ship_entity.transform.position = np.array([0,0,30])

cube_entity1 = EnvironmentEntity(meshes=[mesh], name='cube1')
cube_entity1.transform.position = np.array([0,0,-5], dtype=np.float32)
cube_entity1.transform.rotation = np.array([100.0,0.0,50.0])

cube_entity2 = EnvironmentEntity(meshes=[mesh], name='cube2')
cube_entity2.transform.position = np.array([0,0,5], dtype=np.float32)
cube_entity2.transform.rotation = np.array([0.0,0.0,50.0])


camera_entity = Entity(name='camera')
camera_entity.transform.position = np.array([0.0,0.0,0.0])

camera_controller = CameraController()
camera_entity.add_module(camera_controller)

#teapot_entity.add_module(camera_controller)

engine = py3DEngine(HEIGHT, WIDTH)
engine.main_renderer.set_current_camera(camera_entity)
engine.start_game()

