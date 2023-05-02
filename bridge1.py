# -*- coding: utf-8 -*-
"""
Created on Sat Apr 29 08:10:56 2023

@author: Quinn
"""

# import os
import math
import numpy as np
import pychrono as chrono
import pychrono.robot as robot
import matplotlib.pyplot as plt
import pychrono.irrlicht as chronoirr
# try:
#    from pychrono import irrlicht as chronoirr
# except:
#    print('Could not import ChronoIrrlicht')
   
   
###############################################################################
# I'm trying to make a class to automate the creation of pylons (the vertical 
# supports that hold the bridge deck). This isn't working at the moment. Not
# sure if it is worth working on at the moment.
###############################################################################

# Helper class to make pylons
# class Pylon:
#     def __init__(self,x,y):
#         self.x_loc = x
#         self.y_loc = y
#     def GetVisualization(self):
#         pylon = chrono.ChBodyEasyBox(5,22.86,10,1000,True,True)
#         pylon.SetPos(self.x_loc,self.y_loc,5)
#         return pylon


###############################################################################
# These functions automate the calculation of the 3 moment's of inertia. Right
# now since we are only dealing with rectangular sections, I have only added 
# "Rect_inerita" as a possiblity. Requires a string "shape", then a double for 
# the number of sections the deck is broken up into, then the axis of interest 
# (x = 1, y = 2, z = 3), and finally the three dimensions. 

# Current issues/plans (4/29/23 - QJK):
#    
# [ ]Should update the functions to have input validation on number of segments
# to ensure integers-only. We don't want 2.4 sections.
###############################################################################
def inertia(shape,segments,axis,length,width,depth):
    if shape == "rect":
        if axis == 1:
            I = Rect_inertia(length/segments,width)
        elif axis == 2:
            I = Rect_inertia(depth,length/segments)
        elif axis == 3:
            I = Rect_inertia(width,length/depth)
        else:
            print("!!!Incorrect AXIS input!!!")
            I = 1
    else:
        print("!!!Incorrect SHAPE input!!!")
    return I
   
def Rect_inertia(b,h):
    I = (1/12)*b*h**3
    return I

###############################################################################
# Main body of code. Starts with basic parameters, then moves into the ground
# body, and finally the bridges. So far, only the first pylon is being rendered
# and I'm not sure why. Also, there is an error or something because the 
# visualization will kill itself prior to finishing the full simulation. I'm 
# not sure how long it is actually rendering, and I am not sure how to find 
# out. See Apr29.png for execution dialog. No errors are brought up.

# Current issues/plans (4/29/23 - QJK)

# [ ] Work on creating visuals for second pylon and static deck.
# [ ] Solve render-kill issue.
###############################################################################

# Bridge dimensions and parameters
l = 152.4                           # length of bridge in [m] (500 ft)
w = 22.86                           # width of bridge in [m] (75 ft)
d = .3048                           # depth of bridge in [m] (12 in)
rho_c = 2500                        # density of concrete in [kg/m^3] (156.07 lb/ft^3)
g = chrono.ChVectorD(0,-9.81,0)     # gravitational acceleration in [N]
vol = l*w*d                         # total volume of reinforced concrete in [m^3]
mass = vol*rho_c                    # total mass of reinforced concrete in [kg]
weight_num = mass*g.Length()        # total weight of reinforced concrete in [N]
num_bridges = 5                     # number of bridges being tested
sim_time = 10                       # length of simulation [s]
time_step = 2e-3                    # time step of simulation [s]
time = 0                            # start time of simulation [s]

mat = chrono.ChMaterialSurfaceNSC() # ground material
# Chreate Chrono system
system = chrono.ChSystemNSC()
system.Set_G_acc(g)

# Create ground body
# ground = chrono.ChBodyEasyBox(1.2*l, 1, num_bridges*(w+10), 1000, True, True)
# ground.SetPos(chrono.ChVectorD(0, -.5, 0))
# ground.SetBodyFixed(True)
# ground.GetVisualShape(0).SetTexture(chrono.GetChronoDataFile("textures/concrete.jpg"))
# system.Add(ground)
table_thickness = 0.2
table_pos_y = 0
table = chrono.ChBodyEasyBox(1.2*l, 1, num_bridges*(w+10), 1000, True, True, mat)
system.AddBody(table)
table.SetIdentifier(0)
table.SetBodyFixed(True)
table.SetName("table")
table.SetPos(chrono.ChVectorD(0, table_pos_y, 0))
table.GetVisualShape(0).SetTexture(chrono.GetChronoDataFile("textures/concrete.jpg"))

# Tries to use the "Pylon" class, not functioning (4/29/23 - QJK)
# pyl1 = Pylon(0,0)
#system.Add(pyl1)

# Creates first pylon using ChBodyEasyBox
py1 = chrono.ChBodyEasyBox(1,10,w,1000,True,True, mat)
py1.SetPos(chrono.ChVectorD(-l/2,5+(1/2),5))
py1.SetMass(mass)
py1.SetIdentifier(1)
py1.SetBodyFixed(False)
py1.SetCollide(True)
system.Add(py1)

# Creates second pylon using ChBodyEasyBox
py2 = chrono.ChBodyEasyBox(1,10,w,1000,True,True, mat)
py2.SetMass(mass)
py2.SetIdentifier(2)
py2.SetPos(chrono.ChVectorD(l/2,5+(1/2),5))
py2.SetBodyFixed(False)
py2.SetCollide(True)
system.Add(py2)

# Creates static bridge deck

deck1 = chrono.ChBodyEasyBox(l,d,w,1000,True,True, mat)
deck1.SetMass(mass)
deck1.SetIdentifier(3)
# deck1.SetPos(chrono.ChVectorD(0,0,5+(d/2)))
deck1.SetPos(chrono.ChVectorD(0,10+((d)/2),5))
# deck1.SetBodyFixed(True)
# deck1.SetInertiaXX(chrono.ChVectorD(inertia("rect",1,1,l,w,d),inertia("rect",1,2,l,w,d),inertia("rect",1,3,l,w,d)))
deck1.SetBodyFixed(False)
deck1.SetCollide(True)
# deck1_shape = chrono.ChBoxShape()
# deck1_shape = chrono.ChBodyEasyBox(l,w,d,1000,True,True)
# deck1_shape.GetBoxGeometry().Size = chrono.ChVectorD(l,w,d,1000,True,True)
# deck1_shape.SetColor(chrono.ChColor(.9,.4,.1))
# deck1.AddVisualShape(deck1_shape)
system.Add(deck1)


# Creates visualization
vis = chronoirr.ChVisualSystemIrrlicht()
vis.AttachSystem(system)
vis.SetWindowSize(1024,768)
vis.SetWindowTitle('slider crank demo')
vis.Initialize()
vis.AddSkyBox()
vis.AddCamera(chrono.ChVectorD(-200, 0, 3))
vis.AddTypicalLights()

time_end = 30
# Simulation
while (vis.Run() and system.GetChTime() < time_end):
    

    vis.BeginScene() 
    vis.Render()
    vis.EndScene()
    system.DoStepDynamics(time_step)   
    