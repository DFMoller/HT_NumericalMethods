import pygal
from os import getcwd

# Given Parameters
L = 0.03 # m
T_inf = 220 + 273.15 # K
T_0 = 40 + 273.15 # K
T_inner = 25 + 273.15 # K
q_bottom = 4200 # W/m2
h = 47.1 # W/m2K - combined
density = 1090 # kg/m3
cp = 3424.5 # J/kgK
k = 0.471 # W/mK
cooking_seconds = 11*60 # s

# More Parameters
num_increments = 50 # number of divisions of the steak. 50 divisions mean 51 nodes
dt = 1/100 # dt is chosen significantly lower than the stability criterion
dx = L / num_increments # distance between nodes
tau = k*dt/(density*cp*pow(dx,2)) # time constant

# The number of calculations below is the number of times a new steak thermal
# state will be calculated
num_calculations = int(cooking_seconds / dt) # this must be an int!

# Initialize temperatures arrays
temps = [0]*(num_increments+1) # last temperature buffer
for count, t in enumerate(temps):
    if count == 0 or count == (len(temps)-1):
        temps[count] = T_0 # initial surface temp
    else:
        temps[count] = T_inner # initial internal temp
new_temps = temps # new temperature buffer

# Initialize charts -> pygal charts will be created in the /tmp folder in .svg format
#                   -> if opened in a browser, they are interactive
distribution_chart = pygal.XY(stroke=True, show_dots=True, x_title="Distance (m)", y_title="Temperature (Degrees C)")
distribution_chart.title = 'Temperature Distribution across the Steak per minute'
mid_temp_chart = pygal.XY(stroke=True, show_dots=True, x_title="Time (min)", y_title="Temperature (Degrees C)")
mid_temp_chart.title = 'Temperature at Midpoint of Steak over Time'

mid_temp_line = [(0, temps[25] - 273.15)] # a list containing the midpoint temp over time
for i in range(num_calculations): # one loop per dt
    distribution_line = [] # a list containing the current temperature distribution
    new_temps[0] = 2*dt*h*(T_inf - temps[0])/(density*dx*cp) + 2*dt*k*(temps[1] - temps[0])/(density*pow(dx,2)*cp) + temps[0] # first node
    new_temps[-1] = 2*dx*tau*q_bottom/k + 2*tau*(temps[-2] - temps[-1]) + temps[-1] # last node
    for m in range(len(temps)):
        if m > 0 and m < (len(temps)-1): # middle nodes
            new_temps[m] = tau*temps[m-1] + (1 - 2*tau)*temps[m] + tau*temps[m+1]

    for x in range(len(temps)):
        temps[x] = new_temps[x] # move new buffer into old buffer
        distribution_line.append((dx*x, temps[x] - 273.15)) 
    
    if (i+1) % (60/dt) == 0: # Plot the temperature distribution every 60 seconds
        distribution_chart.add(f'{(i+1)/(60/dt)} min', distribution_line)

    if (i+1) % (15/dt) == 0: # Plot the midpoint temperature every 15 seconds
        mid_temp_line.append(((i+1)*dt/60, temps[25] - 273.15))

mid_temp_chart.add('midpoint', mid_temp_line)

distribution_chart.render_to_file(f'{getcwd()}/tmp/distribution_chart.svg')
mid_temp_chart.render_to_file(f'{getcwd()}/tmp/midpoint_chart.svg')
        
