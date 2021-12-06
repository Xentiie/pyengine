cimport cython
from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free
from libc.math cimport sqrt, tan, sin, cos, M_PI

cdef double* vsub(double *v1, double *v2):
	cdef double *result = <double *>PyMem_Malloc(4*sizeof(double))
	result[0] = v1[0] - v2[0]
	result[1] = v1[1] - v2[1]
	result[2] = v1[2] - v2[2]
	return result

cdef double dot(double *v1, double *v2):
	return (v1[0] * v2[0] + v1[1] * v2[1] + v1[2] + v2[2])

cdef double *cross(double *v1, double *v2):
	cdef double *c = <double *>PyMem_Malloc(4*sizeof(double))
	c[0] = v1[1]*v2[2] - v1[2]*v2[1]
	c[1] = v1[2]*v2[0] - v1[0]*v2[2]
	c[2] = v1[0]*v2[1] - v1[1]*v2[0]
	return c

@cython.cdivision(True)
cdef double* normalize(double* v):
	cdef double length = sqrt(dot(v,v))
	v[0] /= length
	v[1] /= length
	v[2] /= length
	return v

cdef double** make_identity_matrix():
	cdef double **matrix = <double **>PyMem_Malloc(4*sizeof(double*))
	cdef:
		int i = 0
		int j = 0
	for i in range(4):
		matrix[i] =  <double *>PyMem_Malloc(4*sizeof(double))
		matrix[i] = [0,0,0]
		matrix[i][i] = 1
	return matrix

cdef double** make_translation_matrix(double *v):
	cdef double **matrix = make_identity_matrix()
	matrix[3][0] = v[0]
	matrix[3][1] = v[1]
	matrix[3][2] = v[2]
	return matrix

@cython.cdivision(True)
cdef double** make_projection_matrix(double view_angle, int height, int width, double far, double near):                                                       
	cdef:
		double fov = 1.0 / tan(view_angle*0.5/180*M_PI)
		double aspectRatio = height/width
		double **matrix = make_identity_matrix()
	matrix[0][0] = fov * aspectRatio
	matrix[1][1] = fov
	matrix[2][2] = far/(far-near)
	matrix[2][3] = 1
	matrix[3][2] = (-far * near)/(far-near)
	matrix[3][3] = 0
	return matrix

cdef double** matrix_mult(double **m1, double **m2):
	cdef double **matrix = make_identity_matrix()
	for c in range(4):
		for r in range(4):
			matrix[r][c] = m1[r][0] * m2[0][c] + m1[r][1] * m2[1][c] + m1[r][2] * m2[2][c] + m1[r][3] * m2[3][c]
	return matrix

cdef double** make_look_at_point_matrix(double *pos, double *target, double *up):
	cdef:
		double *new_forward = <double *>PyMem_Malloc(4*sizeof(double))
		double *a           = <double *>PyMem_Malloc(4*sizeof(double))
		double *new_up      = <double *>PyMem_Malloc(4*sizeof(double))
		double **matrix     = make_identity_matrix()

	new_forward = vsub(target, pos)
	new_forward = normalize(new_forward)

	a[0] = new_forward[0] * dot(up,new_forward)
	a[1] = new_forward[1] * dot(up,new_forward)
	a[2] = new_forward[2] * dot(up,new_forward)
	new_up = vsub(up, a)
	new_up = normalize(new_up)

	new_right = cross(new_up, new_forward)

	matrix[0][0] = new_right[0]
	matrix[0][1] = new_right[1]
	matrix[0][2] = new_right[2]
	matrix[1][0] = new_up[0]
	matrix[1][1] = new_up[1]
	matrix[1][2] = new_up[2]
	matrix[2][0] = new_forward[0]
	matrix[2][1] = new_forward[1]
	matrix[2][2] = new_forward[2]
	matrix[3][0] = pos[0]
	matrix[3][1] = pos[1]
	matrix[3][2] = pos[2]
	PyMem_Free(new_right)
	PyMem_Free(new_forward)
	PyMem_Free(new_up)
	return matrix

cdef double **make_rotation_matrix(double *rotation):
	cdef double **rotation_matrix = make_identity_matrix()
	rotation_matrix[0] = [cos(rotation[0])*cos(rotation[1]), cos(rotation[0])*sin(rotation[1])*sin(rotation[2]) - sin(rotation[0])*cos(rotation[2]), cos(rotation[0])*sin(rotation[1])*cos(rotation[2])+sin(rotation[0])*sin(rotation[2])  ]
	rotation_matrix[1] = [sin(rotation[0])*cos(rotation[1]), sin(rotation[0])*sin(rotation[1])*sin(rotation[2])+cos(rotation[0])*cos(rotation[2]),   sin(rotation[0])*sin(rotation[1])*cos(rotation[2]) - cos(rotation[0])*sin(rotation[2])]
	rotation_matrix[2] = [-sin(rotation[1]),                 cos(rotation[1]) * sin(rotation[2]),                                                    cos(rotation[1])*cos(rotation[2])                                                     ]
	return rotation_matrix

cdef double** matrix_inverse(double **m):
	cdef double **new_mat = make_identity_matrix()
	new_mat[0] = [m[0][0], m[1][0], m[2][0]]
	new_mat[1] = [m[0][1], m[1][1], m[2][1]]
	new_mat[2] = [m[0][2], m[1][2], m[2][2]]
	new_mat[3] = [
			-(m[3][0] * m[0][0] + m[3][1] * m[1][0] + m[3][2] * m[2][0]),
			-(m[3][0] * m[0][1] + m[3][1] * m[1][1] + m[3][2] * m[2][1]),
			-(m[3][0] * m[0][2] + m[3][1] * m[1][2] + m[3][2] * m[2][2]),
			1
		]
	return new_mat


cdef double* matrix_vector_mult(double *p, double **m):
	cdef double *output = <double *>PyMem_Malloc(4*sizeof(double))
	output[0] = p[0] * m[0][0] + p[1] * m[1][0] + p[2] * m[2][0] + p[3] * m[3][0]
	output[1] = p[0] * m[0][1] + p[1] * m[1][1] + p[2] * m[2][1] + p[3] * m[3][1]
	output[2] = p[0] * m[0][2] + p[1] * m[1][2] + p[2] * m[2][2] + p[3] * m[3][2]
	output[3] = p[0] * m[0][3] + p[1] * m[1][3] + p[2] * m[2][3] + p[3] * m[3][3]
	return output