import sys
import subprocess
import math
import stl

import sys
import os
from optparse import OptionParser

import numpy
from stl import mesh
from subprocess import call
from parse import *

# find the max dimensions, so we can know the bounding box, getting the height,
# width, length (because these are the step size)...
def find_mins_maxs(obj):
    minx = maxx = miny = maxy = minz = maxz = None
    for p in obj.points:
    # p contains (x, y, z)
        if minx is None:
            minx = p[stl.Dimension.X]
            maxx = p[stl.Dimension.X]
            miny = p[stl.Dimension.Y]
            maxy = p[stl.Dimension.Y]
            minz = p[stl.Dimension.Z]
            maxz = p[stl.Dimension.Z]
        else:
            maxx = max(p[stl.Dimension.X], maxx)
            minx = min(p[stl.Dimension.X], minx)
            maxy = max(p[stl.Dimension.Y], maxy)
            miny = min(p[stl.Dimension.Y], miny)
            
            maxz = max(p[stl.Dimension.Z], maxz)
            minz = min(p[stl.Dimension.Z], minz)
    return minx, maxx, miny, maxy, minz, maxz




def parseline(mf):

    parts = mf.readline().split()

    if len(parts[0]) > 2:
        val = parts[0].split('[')
        parts.insert(1, val[1])
        
    if "]" in parts[3]:
        val = parts[3].split(']')
        
        parts.insert(3, val[0])        

    return [float(parts[1]), float(parts[2]), float(parts[3])]
    

def simpoisson_stl():
    mlxpoissonfilename = 'simpoisson.mlx'
    
    subprocess.call(["meshlabserver","-i", stlfilename + ".stl" ,\
            "-o", stlfilename+"_poisson.stl","-s", sys.path[0]+"/" + mlxpoissonfilename])
    
    return stlfilename+"_poisson"

    

def get_meta_data(metafilename):
    mf = open(metafilename, "r")
   
    height = float(mf.readline())
    width = float(mf.readline())
    

    translate = parseline(mf)
    rotate = parseline(mf)
    
    degree = float(mf.readline())*(-180/math.pi)
    
    mf.close()

    return height, width, translate, rotate, degree



  
def poisson_stl():
    mlxpoissonfilename = 'poisson.mlx'
    print "\nStep 2: Perform poisson reconstruction"
    
    subprocess.call(["meshlabserver","-i", stlfilename + ".stl" ,"-o",\
         stlfilename+"_poisson.stl","-s", sys.path[0]+"/" + mlxpoissonfilename])
    
    return stlfilename+"_poisson"



    
    
def align(poisson_stlfilename):
    print "\nStep 1: Perform alignment, please double-click on 3 other points" + \
            " on the turning table, and also the top part of the object";
    subprocess.call(["python", "Align.PY", poisson_stlfilename + ".stl", stlfilename +"_aligned.stl", "meta.txt"])
    
    return "meta.txt"
    

def crop_stl(poisson_stlfilename, metafilename):
    scadfilename = 'cropping.scad'
    scadfilename_template = 'cropping_template.scad'

    #read the original stl to get the size
    scan_mesh = mesh.Mesh.from_file(stlfilename+".stl")

    scan_mesh.rotate([0.0, 0.5, 0.0], math.radians(90))
    minx, maxx, miny, maxy, minz, maxz = find_mins_maxs(scan_mesh)
    w = maxx - minx
    l = maxy - miny
    h = maxz - minz
    

    d = l if w < l else w 
    d = math.sqrt(d*d + d*d)
    print "STL size x:%f, y:%f, z:%f diagonal:%f"%(w,l,h,d)
    
    scale = 100 if d < 1 else 1
    
    height, width, translate, rotate, degree = get_meta_data(metafilename)
    
    data = ''.join(open(scadfilename_template).readlines()[8:-1])

    data = "height=" + str(round(height,10)) + \
            ";\nradius=" + str(round(d,10)) + \
            "/2;\ncprecent=" + str(cprecent) +\
            ";\nstlname=\"" + poisson_stlfilename + ".stl" + "\";\n" +\
            "translate_vec=[" + str(translate[0]) + ", " + str(translate[1]) + ", " + str(translate[2]) + "];\n" + \
            "rotate_vec=[" + str(rotate[0]) + ", " + str(rotate[1]) + ", " + str(rotate[2]) + "];\n" + \
            "rotate_deg=" + str(degree) + ";\n" + \
            "scaling=" + str(scale) + ";\n" + \
            data
    open(scadfilename,"wb").write(data)

    print "\nStep 3: Perform certain cropping"
    
    croppedfilename = stlfilename + "_cropped.stl"
    subprocess.call(["openscad","-o",  croppedfilename, "cropping.scad"])

    return croppedfilename
    
    
def main():
    global stlfilename, cprecent
    
    usage = "usage: %prog [options] arguments"
    optparser = OptionParser(usage=usage)
    optparser.add_option("-s","--stl",dest="stl", 
                         help="The stl file for scanned object")
    optparser.add_option("-p","--cpercent",dest="cpercent",default=100, 
                         type='int', help="The percentage of area that you want to keep, default is 100\%")
    (options, args) = optparser.parse_args()

    
    if not options.stl:
        parser.error('STL file not given')
    else:
        stlfilename = options.stl
        cprecent = options.cpercent
        
        #launch matt's code
        poisson_stlfilename = simpoisson_stl()
        metafilename = align(poisson_stlfilename)
        
        poisson_stlfilename = poisson_stl()
        croppedfilename = crop_stl(poisson_stlfilename, metafilename)
        
        print "\nCropping completes, your file is named as: " + croppedfilename + "!!!"
    

if __name__ == '__main__':
    main()


