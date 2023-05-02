# -*- coding: utf-8 -*-
"""
Created on Sat Apr 29 08:10:56 2023
@author: Quinn
"""

# import os
import math
import numpy as np
import pychrono as chrono
import matplotlib.pyplot as plt
import pychrono.irrlicht as chronoirr
   
   
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
vol = l/2*w*d                         # total volume of reinforced concrete in [m^3]
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
table_thickness = 0.2
table_pos_y = 0
table = chrono.ChBodyEasyBox(1.2*l, 1, num_bridges*(w+10), 1000, True, True, mat)
system.AddBody(table)
table.SetIdentifier(0)
table.SetBodyFixed(True)
table.SetName("table")
table.SetPos(chrono.ChVectorD(0, table_pos_y, 0))
table.GetVisualShape(0).SetTexture(chrono.GetChronoDataFile("textures/concrete.jpg"))

# Creates first pylon using ChBodyEasyBox
py1 = chrono.ChBodyEasyBox(1,10,w,1000,True,True, mat)
py1.SetPos(chrono.ChVectorD(-l/2,5.5,5))
#py1.SetMass(mass)
py1.SetIdentifier(1)
py1.SetBodyFixed(True)
py1.SetCollide(True)
system.Add(py1)

# Creates second pylon using ChBodyEasyBox
py2 = chrono.ChBodyEasyBox(1,10,w,1000,True,True, mat)
#py2.SetMass(mass)
py2.SetIdentifier(2)
py2.SetPos(chrono.ChVectorD(l/2,5.5,5))
py2.SetBodyFixed(True)
py2.SetCollide(True)
system.Add(py2)

# Creates static bridge deck
deck1 = chrono.ChBodyEasyBox(l/2,d,w,1000,True,True, mat)
deck1.SetMass(mass)
deck1.SetIdentifier(3)
deck1.SetPos(chrono.ChVectorD(-l/4,10+((d)/2),5))
deck1.SetBodyFixed(False)
deck1.SetCollide(True)
system.Add(deck1)

deck2 = chrono.ChBodyEasyBox(l/2,d,w,1000,True,True, mat)
deck2.SetMass(mass)
deck2.SetIdentifier(4)
deck2.SetPos(chrono.ChVectorD(l/4,10+((d)/2),5))
deck2.SetBodyFixed(False)
deck2.SetCollide(True)
system.Add(deck2)

joint1 = chrono.ChLinkLockRevolute()
joint1.Initialize(py1,
                   deck1, 
                   chrono.ChCoordsysD(chrono.ChVectorD(-l/2, 10, 5)))
system.Add(joint1)

joint2 = chrono.ChLinkLockRevolute()
joint2.Initialize(py2,
                   deck2, 
                   chrono.ChCoordsysD(chrono.ChVectorD(l/2, 10, 5)))
system.Add(joint2)

# Creates visualization
vis = chronoirr.ChVisualSystemIrrlicht()
vis.AttachSystem(system)
vis.SetWindowSize(1024,768)
vis.SetWindowTitle('bascule bridge')
vis.Initialize()
vis.AddSkyBox()
vis.AddCamera(chrono.ChVectorD(-200, 0, 3))
vis.AddTypicalLights()

time_end = 5

# Simulation

array_time = []
array_posx = []
array_posy = []
array_posz = []
array_negx = []
array_negy = []
array_negz = []

while (vis.Run() and system.GetChTime() < time_end):
    
    array_time.append(system.GetChTime())
    array_posx.append(joint2.Get_react_force().x)
    array_posy.append(joint2.Get_react_force().y)
    array_posz.append(joint2.Get_react_force().z)
    array_negx.append(joint1.Get_react_force().x)
    array_negy.append(joint1.Get_react_force().y)
    array_negz.append(joint1.Get_react_force().z)

    vis.BeginScene() 
    vis.Render()
    vis.EndScene()
    system.DoStepDynamics(time_step)

fig, (ax1, ax2) = plt.subplots(2, sharex = True)

ax1.plot(array_time,array_posx)
ax1.plot(array_time,array_posy)
ax1.plot(array_time,array_posz)
ax1.set(ylabel='Force [N]',xlabel='Time [s]')
ax1.grid()

ax2.plot(array_time,array_negx)
ax2.plot(array_time,array_negy)
ax2.plot(array_time,array_negz)
ax2.set(ylabel='Force [N]',xlabel='Time [s]')
ax2.grid()

plt.savefig('bascule bridge results.png')
plt.show()
