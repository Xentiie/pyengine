from typing import List, Union
from numbers import Number
from math import cos, sin, tan, pi, sqrt
import numpy as np
import keyboard
from numpy.linalg import norm

def import_obj_file(file: str) -> list:
    verts = []
    tris = []
    with open(file, mode='r') as f:
        for l in f:
            if(l[0] == 'v'):
                l_split = l.split(' ')
                a = [float(l_split[1]), float(l_split[2]), float(l_split[3])]
                verts.append(a)

            elif(l[0] == 'f'):
                l_split = l.split(' ')
                a = [int(l_split[1]), int(l_split[2]), int(l_split[3])]
                tris.append(a)

            else:
                continue

    final_a = []
    for t in tris:
        final_a.append([verts[t[0]-1], verts[t[1]-1], verts[t[2]-1]])
    return final_a

def normalized(a, axis=-1, order=2):
    l2 = np.atleast_1d(np.linalg.norm(a, order, axis))
    l2[l2==0] = 1
    return a / np.expand_dims(l2, axis)[0]

def normalized_old(a):
    lenght = sqrt(np.dot(a,a))
    return np.array([a[0]/lenght, a[1]/lenght, a[2]/lenght])

def make_identity_matrix():
    matrix = np.matrix([
        [1,0,0,0],
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1]
    ], dtype=np.float32)
    return matrix

def make_translation_matrix(v: np.ndarray):
    matrix = make_identity_matrix()
    matrix[3,0] = v[0]
    matrix[3,1] = v[1]
    matrix[3,2] = v[2]
    return matrix

def make_projection_matrix(view_angle: float, height: int, width: int, far: float=1000, near: float=0.1):                                                       
    fov = 1.0 / tan(view_angle*0.5/180*pi)                                 # Angle de vue de la camera          
    aspectRatio = height/width
    matrix = np.matrix([
        [fov * aspectRatio, 0,   0,                        0.0],         
        [0,                 fov, 0,                        0.0],         
        [0,                 0,   far/(far-near),           1.0],         
        [0,                 0,   (-far * near)/(far-near), 0.0]
    ], dtype=np.float32)
    return matrix

def matrix_mult(m1: np.matrix, m2: np.matrix):
    matrix = np.matrix(np.empty((4,4)), dtype=np.float32)
    for c in range(4):
        for r in range(4):
            matrix[r,c] = m1[r,0] * m2[0,c] + m1[r,1] * m2[1,c] + m1[r,2] * m2[2,c] + m1[r,3] * m2[3,c]
    return matrix

def make_look_at_point_matrix(pos, target, up):
    new_forward = target - pos
    new_forward = normalized(new_forward)

    a = new_forward * np.dot(up,new_forward)
    new_up = up - a
    new_up = normalized(new_up)

    new_right = np.cross(new_up, new_forward)

    matrix = np.matrix([
        [new_right[0],   new_right[1],   new_right[2],   0],
        [new_up[0],      new_up[1],      new_up[2],      0],
        [new_forward[0], new_forward[1], new_forward[2], 0],
        [pos[0],         pos[1],         pos[2],         1]
    ], dtype=np.float32)
    return matrix

def make_rotation_matrix(rotation):
    rotation_matrix = np.matrix([
        [cos(rotation[0])*cos(rotation[1]), cos(rotation[0])*sin(rotation[1])*sin(rotation[2]) - sin(rotation[0])*cos(rotation[2]), cos(rotation[0])*sin(rotation[1])*cos(rotation[2])+sin(rotation[0])*sin(rotation[2]),      0],
        [sin(rotation[0])*cos(rotation[1]), sin(rotation[0])*sin(rotation[1])*sin(rotation[2])+cos(rotation[0])*cos(rotation[2]),   sin(rotation[0])*sin(rotation[1])*cos(rotation[2]) - cos(rotation[0])*sin(rotation[2]),    0],
        [-sin(rotation[1]),                 cos(rotation[1]) * sin(rotation[2]),                                                    cos(rotation[1])*cos(rotation[2]),                                                         0],
        [0,0,0,1]
    ], dtype=np.float32)
    return rotation_matrix

#only for translation/rotation
def matrix_inverse(m):
    new_mat = np.matrix([
        [m[0,0], m[1,0], m[2,0], 0.0],
        [m[0,1], m[1,1], m[2,1], 0.0],
        [m[0,2], m[1,2], m[2,2], 0.0],
        [
            -(m[3,0] * m[0,0] + m[3,1] * m[1,0] + m[3,2] * m[2,0]), 
            -(m[3,0] * m[0,1] + m[3,1] * m[1,1] + m[3,2] * m[2,1]), 
            -(m[3,0] * m[0,2] + m[3,1] * m[1,2] + m[3,2] * m[2,2]), 
            1
        ]
    ], dtype=np.float32)
    return new_mat


def matrix_vector_mult(p: list, m: list):
    x = p[0] * m[0,0] + p[1] * m[1,0] + p[2] * m[2,0] + p[3] * m[3,0]
    y = p[0] * m[0,1] + p[1] * m[1,1] + p[2] * m[2,1] + p[3] * m[3,1]
    z = p[0] * m[0,2] + p[1] * m[1,2] + p[2] * m[2,2] + p[3] * m[3,2]
    w = p[0] * m[0,3] + p[1] * m[1,3] + p[2] * m[2,3] + p[3] * m[3,3]
    return np.array([x,y,z,w])

class Module:
    def set_parent_entity(self, entity: 'Entity'):
        self.entity = entity

    def on_delete(self):
        pass

    def start(self):
        pass

    def update(self):
        pass
    def __del__(self):
        if("entity" in locals()):
            self.on_delete()
            self.entity.remove_module(self)

class Transform(Module):

    def __init__(self, position: np.ndarray = None, rotation: np.ndarray = None):
        if(not position):
            self.position = np.zeros(3, dtype=np.float32)
        else:
            self.position = position

        if(not rotation):
            self.rotation = np.zeros(3, dtype=np.float32)
        else:
            self.rotation = rotation

    def world_matrix(self):
        rot_mat = make_rotation_matrix(self.rotation)
        translation_mat = make_translation_matrix(self.position)
        matrix = matrix_mult(rot_mat, translation_mat)
        return matrix

    @property
    def forward(self):
        target = np.array([0,0,1,0])
        rot_mat = make_rotation_matrix(self.rotation)
        look_dir = matrix_vector_mult(target, rot_mat)
        return look_dir

    @property
    def right(self):
        return np.cross([0,1,0], self.forward[:-1])

#class Scene

class Entity:
    entity_list = []
    def __init__(self, name: str=None):
        if(not name):
            name = 'Entity#' + str(len(Entity.entity_list))
        self.name = name
        Entity.entity_list.append(self)
        self.__modules = []
        self.transform = Transform()
        self.add_module(self.transform)
        #Create UI

    def __del__(self):
        for m in self.__modules:
            del(m)
        Entity.entity_list.remove(self)

    def add_module(self, module: Module):
        module.set_parent_entity(self)
        module.start()
        self.__modules.append(module)

    def get_modules(self, module_type: Union[str, type]) -> List[Module]:
        if(module_type == 'all'):
            return [m for m in self.__modules]

        a = [m for m in self.__modules if (type(m)==module_type) or (m.__class__.__name__.lower() == module_type.lower())]
        if(len(a) == 1):
            return a[0]
        return a

    def remove_module(self, m: Module):
        self.__modules.remove(m)

class EnvironmentEntity(Entity):
    def __init__(self, meshes=None, name=''):
        super().__init__(name=name)
        self.meshes = meshes

    def get_meshes(self):
        return self.meshes

    def add_mesh(self, m):
        self.meshes.append(m)

#Hidden w for matrix mult
class Vector:

    def from_list(l):
        assert(len(l) == 3)
        return Vector(l[0], l[1], l[2])

    def __init__(self, x: Number=0, y: Number=0, z: Number=0):
        #self._list = np.array([x,y,z,w])
        self._list = np.array([x,y,z])

    def magnitude(self):
        v = 0
        for i in range(len(self._list)):
            v += self._list[i]**2
        return v

    @property
    def x(self):
        return self._list[0]
    @x.setter
    def x(self, v):
        assert(isinstance(v, Number))
        self._list[0] = v

    @property
    def y(self):
        return self._list[1]
    @y.setter
    def y(self, v):
        assert(isinstance(v, Number))
        self._list[1] = v

    @property
    def z(self):
        return self._list[2]
    @z.setter
    def z(self, v):
        assert(isinstance(v, Number))
        self._list[2] = v

    def __len__(self):
        return len(self._list)

    def __iter__(self) -> dict:
        for i, j in enumerate(self._list):
            yield self._list[i]

    def __getitem__(self, ii):
        return self._list[ii]

    def __add__(self, v):
        if(isinstance(v, Number)):
            self._list[0] += v
            self._list[1] += v
            self._list[2] += v
        elif(isinstance(v, (list, np.ndarray, Vector))):
            assert(len(v) <= 3)
            for i in range(len(v)):
                self._list[i] += v[i]
        else:
            raise(TypeError)
        return Vector.from_list([self.x, self.y, self.z])

    def __radd__(self, v):
        return self.__add__(v)

    def __sub__(self, v):
        if(isinstance(v, Number)):
            self._list[0] -= v
            self._list[1] -= v
            self._list[2] -= v
        elif(isinstance(v, (list, np.ndarray, Vector))):
            assert(len(v) <= 3)
            for i in range(len(v)):
                self._list[i] -= v[i]
        else:
            raise(TypeError)
        return Vector.from_list([self.x, self.y, self.z])

    def __rsub__(self, v):
        return self.__sub__(v)

    def __mul__(self, v):
        if(isinstance(v, Number)):
            self._list[0] *= v
            self._list[1] *= v
            self._list[2] *= v
        elif(isinstance(v, (list, np.ndarray, Vector))):
            assert(len(v) <= 3)
            for i in range(len(v)):
                self._list[i] *= v[i]
        else:
            raise(TypeError)
        return Vector.from_list([self.x, self.y, self.z])

    def __rmul__(self, v):
        return self.__mul__(v)

    def __truediv__(self, v):
        if(isinstance(v, Number)):
            self._list[0] /= v
            self._list[1] /= v
            self._list[2] /= v
        elif(isinstance(v, (list, np.ndarray, Vector))):
            assert(len(v) <= 3)
            for i in range(len(v)):
                self._list[i] /= v[i]
        else:
            raise(TypeError)
        return Vector.from_list([self.x, self.y, self.z])

    def __rtruediv__(self, v):
        return self.__truediv__(v)

    def __lt__(self, v):
        assert(isinstance(v, Vector))
        return self.magnitude() < v.magnitude()

    def __le__(self, v):
        assert(isinstance(v, Vector))
        return self.magnitude() <= v.magnitude()

    def __gt__(self, v):
        assert(isinstance(v, Vector))
        return self.magnitude() > v.magnitude()

    def __ge__(self, v):
        assert(isinstance(v, Vector))
        return self.magnitude() >= v.magnitude()

    def __eq__(self, v):
        assert(isinstance(v, Vector))
        return (self.x == v.x and self.y == v.y and self.z == v.z)

    def __ne__(self, v):
        return not self.__eq__(v)

class Vector4D(Vector):

    def from_list(l):
        assert(len(l) == 4)
        return Vector(l[0], l[1], l[2], l)

    def __init__(self, x: Number=0, y: Number=0, z: Number=0, w: Number=0):
        super().__init__(x,y,z)
        self._list = np.append(self._list, w)

    @property
    def w(self):
        return self._list[3]
    @w.setter
    def w(self, v):
        assert(isinstance(v, Number))
        self._list[3] = v

#class Inputs:
#
#    def __init__(self):
#        self.last_mouse_pos = mouse.get_position()
#        self.mouse_velocity = (0.0,0.0)
#    
#    def update_values(self):
#        new_pos = mouse.get_position()
#        self.mouse_velocity = (new_pos[0] - self.last_mouse_pos[0], new_pos[1] - self.last_mouse_pos[1])
#        self.last_mouse_pos = new_pos