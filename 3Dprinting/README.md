#3D printing

1. 	Before you run the program, you have to install the following software:
	- python 2.6
	- MeshLab
	- python library numpy-stl
	- python library matplotlib
	- OpenSCAD
	- CURA 

2. 	If you have a scanned object, e.g. "scanned.stl", you can perform semi-automatic object isolation in terminal by:

	`python flooring_cropping.py -p -s scanned`

	where -p is the percentage of the of mesh that you want to keep on the turntable,
	and -s is the name (without extension) of your stl file.