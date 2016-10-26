import sys
import math
import numpy
from parse import *
from stl import mesh
from mpl_toolkits import mplot3d
from matplotlib import pyplot

def new_3d_figure():
	figure = pyplot.figure(figsize=(12, 10))
	axes = mplot3d.Axes3D(figure)
	return figure, axes

def axes_add_stl_file(axes, path, color=None):
	surface = mesh.Mesh.from_file(path)
	axes_add_surface(axes, surface, color)
	return surface

def axes_add_surface(axes, surface, color=None):
	axes_add_polygons(axes, surface.vectors, color)
	pyplot.draw()

def axes_add_polygons(axes, vertex_array, color=None):
	polygons = mplot3d.art3d.Poly3DCollection(
		vertex_array,
		facecolors = color if color != None else 'white',
		linewidths = 0.2,
		alpha=  0.5
	)
	axes.add_collection3d(polygons)
	pyplot.draw()

def scale_axes_to_surface(axes, surface):
	axes.auto_scale_xyz(
		[surface.x.min(), surface.x.max()],
		[surface.y.min(), surface.y.max()],
		[surface.z.min(), surface.z.max()]
	)
	pyplot.draw()

def guess_clicked_point(event):
	as_string = axes.format_coord(event.xdata, event.ydata)
	parsed = parse('x={x}, y={y}, z={z}', as_string)
	return numpy.array([float(parsed['x']), float(parsed['y']), float(parsed['z'])])

def closest_vertex_to_click(axes, surface, event):
	click_vector = numpy.array([event.xdata, event.ydata])
	vertices_by_distance = []
	for facet in surface.vectors:
		for vertex in facet:
			vertex_click_coordinates_with_depth = mesh_to_click_coordinates_with_depth(
				vertex[0], vertex[1], vertex[2],
				axes
			)
			lateral_distance_from_click = numpy.linalg.norm(
				numpy.array(
						[
							vertex_click_coordinates_with_depth[0],
							vertex_click_coordinates_with_depth[1]
						]
					)
					- click_vector)
			depth = vertex_click_coordinates_with_depth[2]
			vertices_by_distance.append(
				(lateral_distance_from_click, vertex, depth)
			)
	vertices_by_distance.sort(key = lambda tuple: tuple[0]) # Sort by lateral distance
	some_close_vertices = vertices_by_distance[:24] # Take some close points by lateral distance
	some_close_vertices.sort(key = lambda tuple: tuple[2]) # Now sort by depth
	return some_close_vertices[0][1] # Take the vertex closest to the viewer

def mesh_to_click_coordinates_with_depth(x, y, z, axes):
	click_x, click_y, click_z = mplot3d.proj3d.proj_transform(x, y, z, axes.get_proj())
	return numpy.array([click_x, click_y, click_z])

def align_surface_to_ground(axes, surface, ground_vertices, apex_vertex, illustrate=False):
	if illustrate:
		axes_add_polygons(axes, [ ground_vertices ], 'blue')
	ground_zero = (ground_vertices[0] + ground_vertices[1] + ground_vertices[2]) / 3
	apex_distance = numpy.linalg.norm(apex_vertex - ground_zero)
	ground_radius = max(
		[
			numpy.linalg.norm(ground_vertices[0] - ground_zero),
			numpy.linalg.norm(ground_vertices[1] - ground_zero),
			numpy.linalg.norm(ground_vertices[2] - ground_zero)
		]
	)
	translation_vector = -ground_zero
	surface.translate(translation_vector)
	if illustrate:
		axes_add_surface(axes, surface, 'yellow')
	plane_vector_0 = ground_vertices[1] - ground_vertices[0]
	plane_vector_1 = ground_vertices[2] - ground_vertices[0]
	perpendicular = numpy.cross(plane_vector_0, plane_vector_1)
	plane_normal = perpendicular / numpy.linalg.norm(perpendicular)
	stage_normal = numpy.array([0, 0, 1])
	rotation_vector = numpy.cross(stage_normal, plane_normal)
	inner_normals = numpy.inner(stage_normal, plane_normal)
	rotation_axis = rotation_vector / numpy.linalg.norm(rotation_vector)
	rotation_radians = math.atan2(numpy.linalg.norm(rotation_vector), inner_normals)
	surface.rotate(rotation_axis, rotation_radians)
	if illustrate:
		axes_add_surface(axes, surface, 'green')
	return apex_distance, ground_radius, translation_vector, rotation_axis, rotation_radians

def align_on_click_callback(axes, surface, save_path, meta_path):
	clicked_vertices = []

	def callback(event):
		if len(clicked_vertices) < 4 and event.dblclick:

			print 'Processing, please wait .' + '.' * len(clicked_vertices)
			clicked_vertex = closest_vertex_to_click(axes, surface, event)
			clicked_vertices.append(clicked_vertex)

			if len(clicked_vertices) == 4:
				print 'Aligning surface to ground plane ...'

				ground_vertices = [ clicked_vertices[0], clicked_vertices[1], clicked_vertices[2] ]
				apex_vertex = clicked_vertices[3]

				apex_distance, ground_radius, translation_vector, rotation_axis, rotation_radians = align_surface_to_ground(
					axes, surface, ground_vertices, apex_vertex, illustrate=True
				)

				print 'Apex distance: ' + str(apex_distance)
				print 'Ground radius: ' + str(ground_radius)
				print 'Translation vector: ' + str(translation_vector)
				print 'Rotation axis: ' + str(rotation_axis)
				print 'Rotation radians: ' + str(rotation_radians)
				

				surface.save(save_path)

				meta_file = open(meta_path, 'w')
				meta_file.write(str(apex_distance) + '\n')
				meta_file.write(str(ground_radius) + '\n')
				meta_file.write(str(translation_vector) + '\n')
				meta_file.write(str(rotation_axis) + '\n')
				meta_file.write(str(rotation_radians) + '\n')
				meta_file.close()

				print 'Done!'
				print 'Result saved to ' + save_path
				print 'Meta data saved to ' + meta_path
				
				
				print "\nAlignment completes, please close all the windows!!!"

				aligned_figure, aligned_axes = new_3d_figure()
				axes_add_surface(aligned_axes, surface, 'green')
				scale_axes_to_surface(aligned_axes, surface)
				pyplot.show()
				


	return callback

if len(sys.argv) == 4:
	unaligned_figure, unaligned_axes = new_3d_figure()
	surface = axes_add_stl_file(unaligned_axes, sys.argv[1])
	scale_axes_to_surface(unaligned_axes, surface)

	unaligned_figure.canvas.callbacks.connect('button_press_event',
		align_on_click_callback(unaligned_axes, surface, sys.argv[2], sys.argv[3])
	)

	pyplot.show()
else:
	print 'Usage: ' + sys.argv[0] + ' [Input STL] [Output STL] [Output Meta File]'
