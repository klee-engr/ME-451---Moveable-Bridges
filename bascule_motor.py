###############################################################################
#################### General notes on code organization #######################
###############################################################################
#
# Commenting conventions:
# 
# Use {} to reference a function, i.e. {Rect_inertia} is referring to the 
#   Rect_inertia function
#
# Use '' to reference a variable, i.e. 'mass' is referring to the mass variable
#
# Use "" to reference a value of a variable, i.e. if 'mass' is "23", the value
#   of 'mass' is the number "23"
#
# Use <> to reference an object in the code, i.e. <py1> is the first pylon 
#   created
#
# Use [] to denote the primary units of a value, i.e. [m] is for meters
#
# Use () to denote the secondary units of a value, i.e. (ft) is for feet
#
# Use / / for checkboxes for notes on future work/to-do lists. Once 
#   functionality has been checked, notes can be deleted.
#
# 
#
# We used a common template to build our models. If we were to continue this 
# project long term, many of the common features between our models like the 
# {inertia} function and /Pylon/ class would be in a library that we could
# call. Since our project is small, we decided to keep a consistent template 
# instead of making such a library.
###############################################################################

#------------------------------------------------------------------------------
################## Required packages for running our code #####################
#------------------------------------------------------------------------------

import math
import numpy as np
import pychrono as chrono
import matplotlib.pyplot as plt
import pychrono.irrlicht as chronoirr

#------------------------------------------------------------------------------
########################### Classes and functions #############################
#------------------------------------------------------------------------------
   
###############################################################################
# I'm trying to make a class to automate the creation of pylons (the vertical 
# supports that hold the bridge deck). This isn't working at the moment. 
#
# / / Get to function correctly
#
# / / Add a class to make sections of the deck
###############################################################################

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
#
# THIS CODE IS CURRENTLY NOT USED IN MODELS.
#
# This code functions as described, but proved to be unneeded in our models.
# In the future, we would need the various moments of inertia of different
# geometries, but we only thought we needed to compute rectangular sections.
# After further developing our models, we realized we didn't need to compute
# the moments of inertia so we aren't utilizing this function, but future work 
# would involve expanding this function to include multiple geometries that are
# commonly used in bridge construction like circular cross sections, I-beams, 
# and hollow shapes as well.
# 
# TO DO:
#
# / / Expand arguements for 'inertia' to allow for variable number of input
#     dimensions. Will need a different number of paramters based on geometry.
#
# / / Add more formulas for common areas: Circ_inertia, Ibeam_inertia, 
#     HollowRect_inertia, etc...
###############################################################################

def inertia(shape,segments,axis,length,width,depth):
    if shape == "rect":                                         # Tests 'shape' variable to confirm correct formula is used
        if axis == 1:                                           # Calls {Rect_inertia} and uses correct variables for X moment of inertia
            I = Rect_inertia(length/segments,width)
        elif axis == 2:                                         # Calls {Rect_inertia} and uses correct variables for Y moment of inertia
            I = Rect_inertia(depth,length/segments)
        elif axis == 3:                                         # Calls {Rect_inertia} and uses correct variables for Z moment of inertia
            I = Rect_inertia(width,length/depth)
        else:                                                   # If 'axis' is not "1", "2", or "3" print a warning to console and return a value of "1"
            print("!!!Incorrect AXIS input!!!")
            I = 1
    else:                                                       # If the 'shape' string is not recognized, print a warning to console and reture a value of "1"
        print("!!!Incorrect SHAPE input!!!")
        I = 1
    return I
   
def Rect_inertia(b,h):                                          # Function to determine and return the area moment of inertia of a rectangular area to {inertia} function
    I = (1/12)*b*h**3
    return I


###############################################################################
############################ MAIN CODE FOR MODEL ##############################
###############################################################################

###############################################################################
# Main body of code. Starts with basic parameters, then moves into the ground
# body, the bridge deck(s), and finally the joints/motors. Our models consist 
# of two pylons, set at 500 feet/152.4 m apart symmetrically about the origin 
# along the x-axis of the simulation. The pylons are all 5 m tall, and the
# bridge deck(s) are also elevated to 5 m above the z-plane.
#
# In this model, of a 2-decked bascule design, there are 2 bridge decks of
# equal length (250 feet/76.2 m). Each deck is connected either by a joint or a
# motor to the adjacent pylon. 
###############################################################################

#------------------------------------------------------------------------------
##################### Bridge dimensions and parameters ########################
#------------------------------------------------------------------------------

# Gravity Vector
g = chrono.ChVectorD(0,-9.81,0)         # gravitational acceleration in [m/s^2]

# Geometric Parameters
l = 152.4                               # length of bridge in [m] (500 ft)
w = 22.86                               # width of bridge in [m] (75 ft)
d = .3048                               # depth of bridge in [m] (12 in)

# Material Properties
rho_c = 2500                            # density of concrete in [kg/m^3] (156.07 lb/ft^3)
mat = chrono.ChMaterialSurfaceNSC()     # ground material contact system

# Weight and Mass Calculations
vol = l/2*w*d                           # total volume of reinforced concrete in [m^3]
mass = vol*rho_c                        # total mass of reinforced concrete in [kg]
weight_num = mass*g.Length()            # total weight of reinforced concrete in [N]

# Simulation Parameters
time_step = 2e-3                        # time step of simulation [s]
time_end = 15                           # start time of simulation [s]
omg = math.pi/(2*time_end)              # rotational velocity of motors [rad/s]

#------------------------------------------------------------------------------
########################### Bascule Bridge Model ##############################
#------------------------------------------------------------------------------

# Create Chrono system with NSC contact
system = chrono.ChSystemNSC()           
system.Set_G_acc(g)                     
z2x = chrono.Q_from_AngY(0)             

# Create ground body, textures it as water, and adds it to system
ground_thickness = 0.2
ground_pos_y = 0
ground = chrono.ChBodyEasyBox(1.2*l, 1, 5*(w+10), 1000, True, True, mat)
system.AddBody(ground)
ground.SetIdentifier(0)
ground.SetBodyFixed(True)
ground.SetName("table")
ground.SetPos(chrono.ChVectorD(0, ground_pos_y, 0))
ground.GetVisualShape(0).SetTexture(chrono.GetChronoDataFile("textures/water1.jpg"))

# Creates first pylon using ChBodyEasyBox centered at -76.2 m/-250 feet, textures it as concrete, and adds <py1> to the system
py1 = chrono.ChBodyEasyBox(1,10,w,1000,True,True, mat)
py1.SetPos(chrono.ChVectorD(-l/2,5.5,5))
py1.GetVisualShape(0).SetTexture(chrono.GetChronoDataFile("textures/concrete.jpg"))
py1.SetIdentifier(1)
py1.SetBodyFixed(True)
py1.SetCollide(True)
system.Add(py1)

# Creates second pylon using ChBodyEasyBox centered at 76.2 m/250 feet, textures it as concrete, and adds <py2> to the system
py2 = chrono.ChBodyEasyBox(1,10,w,1000,True,True, mat)
py2.GetVisualShape(0).SetTexture(chrono.GetChronoDataFile("textures/concrete.jpg"))
py2.SetIdentifier(2)
py2.SetPos(chrono.ChVectorD(l/2,5.5,5))
py2.SetBodyFixed(True)
py2.SetCollide(True)
system.Add(py2)

# Creates first bridge deck using ChBodyEasyBox centered at -38.1 m/-125 feet, textures it as concrete, and adds <deck1> to the system
deck1 = chrono.ChBodyEasyBox(l/2,d,w,1000,True,True, mat)
deck1.SetMass(mass)
deck1.GetVisualShape(0).SetTexture(chrono.GetChronoDataFile("textures/concrete.jpg"))
deck1.SetIdentifier(3)
deck1.SetPos(chrono.ChVectorD(-l/4,10+((d)/2),5))
deck1.SetBodyFixed(False)
deck1.SetCollide(True)
system.Add(deck1)

# Creates second bridge deck using ChBodyEasyBox centered at 38.1 m/125 feet, textures it as concrete, and adds <deck1> to the system
deck2 = chrono.ChBodyEasyBox(l/2,d,w,1000,True,True, mat)
deck2.SetMass(mass)
deck2.GetVisualShape(0).SetTexture(chrono.GetChronoDataFile("textures/concrete.jpg"))
deck2.SetIdentifier(4)
deck2.SetPos(chrono.ChVectorD(l/4,10+((d)/2),5))
deck2.SetBodyFixed(False)
deck2.SetCollide(True)
system.Add(deck2)

###############################################################################
################# MOTORS AND JOINTS (COMMENT OUT THE SECTION ##################
##################### THAT WILL NOT BE USED FOR ANALYSIS) #####################
###############################################################################

#------------------------------------------------------------------------------
# This section contains both the joints, used for pseudo-static analysis, as 
# well as the motors for the full kinematic analysis. Simply comment out the 
# joints AND uncomment the motors if you want to run the kinematic analysis, or
# vice-versa for the pseudo-static analysis. For simplicity, each pair of 
# joints and motors are called <jmX> where the X is an identifier. We did this
# so the end user only has to comment/uncomment between the motors and the 
# joints - none of the data collection code or arrays code needs to be changed
# when switching from joints to motors or vice-versa.
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
############### Section for pseudo-static analysis using joints ###############
#------------------------------------------------------------------------------


#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

# mj = "pseudo-static"

# # Creates first revolute joint between <py1> and <deck1> at -76.2 m/-250 feet and adds <jm1> to the system
# jm1 = chrono.ChLinkLockRevolute()
# jm1.Initialize(py1, deck1, chrono.ChCoordsysD())
# system.AddLink(jm1)

# # Creates second revolute joint between <py2> and <deck2> at 76.2 m/250 feet and adds <jm2> to the system
# jm2 = chrono.ChLinkLockRevolute()
# jm2.Initialize(py2, deck1, chrono.ChCoordsysD())
# system.AddLink(jm2)

#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||





#------------------------------------------------------------------------------
################# Section for kinematic analysis using motors #################
#------------------------------------------------------------------------------


#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

mj = "kinematic"

# Creates first motor driving <py1> and <deck1> at -76.2 m/-250 feet with a ramped rotational velocity of -'omg' and adds <jm1> to the system
jm1 = chrono.ChLinkMotorRotationAngle()
jm1.Initialize(py1, deck1, chrono.ChFrameD(chrono.ChVectorD(-l/2, 10, 5), z2x))
jm1.SetAngleFunction(chrono.ChFunction_Ramp(0, -omg))
system.AddLink(jm1)

# Creates second motor driving <py2> and <deck2> at 76.2 m/250 feet with a ramped rotational velocity of 'omg' and adds <jm2> to the system
jm2 = chrono.ChLinkMotorRotationAngle()
jm2.Initialize(py2, deck2, chrono.ChFrameD(chrono.ChVectorD(l/2, 10, 5), z2x))
jm2.SetAngleFunction(chrono.ChFunction_Ramp(0, omg))
system.AddLink(jm2)

#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||





#------------------------------------------------------------------------------
#################### Irrlicht visualization of simulation #####################
#------------------------------------------------------------------------------

vis = chronoirr.ChVisualSystemIrrlicht()
vis.AttachSystem(system)
vis.SetWindowSize(1024,768)
vis.SetWindowTitle('bascule bridge')
vis.Initialize()
vis.AddSkyBox()
vis.AddCamera(chrono.ChVectorD(-200, 0, 3))
vis.AddTypicalLights()

#------------------------------------------------------------------------------
########################## Arrays for data storage ############################
#------------------------------------------------------------------------------

array_time = []                         # Array for time
array_1x = []                           # Array for X reaction force at joint1/motor1
array_1y = []                           # Array for Y reaction force at joint1/motor1
array_1z = []                           # Array for Z reaction force at joint1/motor1
array_1t = []                           # Array for reaction torque at joint1/motor1
array_2x = []                           # Array for X reaction force at joint2/motor2
array_2y = []                           # Array for Y reaction force at joint2/motor2
array_2z = []                           # Array for Z reaction force at joint2/motor2
array_2t = []                           # Array for reaction torque at joint2/motor2

# array_joint1 = []
# array_joint1_avg = []
# array_joint2 = []
# array_joint2_avg = []

#------------------------------------------------------------------------------
######################## Simulation of bridge model ###########################
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# This section runs the simulation on our system for a length of 'time_end' and
# a time step of 'time_step'. We collect the reaction forces and torques from
# each motor/joint in arrays intialized above.
#------------------------------------------------------------------------------

while (vis.Run() and system.GetChTime() < time_end):
    
    array_time.append(system.GetChTime())
    array_1x.append(jm1.Get_react_force().x)
    array_1y.append(jm1.Get_react_force().y)
    array_1z.append(jm1.Get_react_force().z)
    array_1t.append(jm1.Get_react_torque().z)
    array_2x.append(jm2.Get_react_force().x)
    array_2y.append(jm2.Get_react_force().y)
    array_2z.append(jm2.Get_react_force().z)
    array_2t.append(jm2.Get_react_torque().z)
    
    # array_joint1.append(jm1.Get_react_torque().z)
    # array_joint1_avg.append(np.mean(array_joint1))
    
    # array_joint2.append(joint2.Get_react_torque().z)
    # array_joint2_avg.append(np.mean(array_joint2))
    
    # array_joint1
    vis.BeginScene() 
    vis.Render()
    vis.EndScene()
    system.DoStepDynamics(time_step)

#------------------------------------------------------------------------------
######################## Calculations and plotting ############################
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# This section computes the average reaction forces and torques at each
# joint/motor, prints them to console, and plots the time history data as well.
# Saves the plots to the local folder from which the script is ran.
#------------------------------------------------------------------------------
ave1 = np.sqrt(np.mean(array_1x)**2 + np.mean(array_1y)**2 + np.mean(array_1z)**2)
print("Average reaction at jm1: ",ave1)

print("Average reaction torque at jm1:",np.mean(array_1t))

ave2 = np.sqrt(np.mean(array_2x)**2 + np.mean(array_2y)**2 + np.mean(array_2z)**2)
print("Average reaction at jm2: ",ave2)

print("Average reaction torque at jm2:",np.mean(array_2t))

fig, (ax1, ax2, ax3) = plt.subplots(3, sharex = True)

# ax1.plot(array_time,array_joint1_avg)
ax1.plot(array_time,array_1x)
ax1.plot(array_time,array_1y)
ax1.plot(array_time,array_1z)
ax1.set(ylabel='Reaction Force [N]')
ax1.grid()

# ax2.plot(array_time,array_joint2_avg)
ax2.plot(array_time,array_2x)
ax2.plot(array_time,array_2y)
ax2.plot(array_time,array_2z)
ax2.set(ylabel='Reaction Force [N]')
ax2.grid()

ax3.plot(array_time,array_1t)
ax3.plot(array_time,array_2t)
ax3.set(ylabel='Reaction Torque [Nm]',xlabel='Time [s]')
ax3.grid()

if mj == "pseudo-static":
    plt.savefig('bascule bridge - pseudo-static.png')
    plt.xlim(0.2, 4.95)
    plt.show()
elif mj == "kinematic":
    plt.savefig('bascule bridge - kinematic.png')
    plt.xlim(0.2, 4.95)
    plt.show()
else:
    plt.savefig('bascule bridge - unknown.png')
    plt.xlim(0.2, 4.95)
    plt.show()
