import pygal
from os import getcwd

L = 0.03
T_inf = 220 + 273.15
q_bottom = 4200 # W/m2
h = 47.1 # W/m2K - combined
density = 1090 # kg/m3
cp = 3424.5 # J/kgK
k = 0.471 # W/mK

num_increments = 50
cooking_seconds = 11*60
dt = 1
dx = L / num_increments
# dx = 0.015
tau = k*dt/(density*cp*pow(dx,2))

# Initialize temperatures array
temps = [0]*(num_increments+1)
for count, t in enumerate(temps):
    if count == 0 or count == (len(temps)-1):
        temps[count] = 40 + 273.15 # initial surface temp
    else:
        temps[count] = 25 + 273.15 # initial internal temp
new_temps = temps

distribution_chart = pygal.XY(stroke=True, show_dots=True)
distribution_chart.title = 'Temperature Distribution across the Steak every minute'

mid_temp_line = [(0, temps[25] - 273.15)]
for i in range(cooking_seconds):
    line = []
    new_temps[0] = 2*dt*h*(T_inf - temps[0])/(density*dx*cp) + 2*dt*k*(temps[1] - temps[0])/(density*pow(dx,2)*cp) + temps[0]
    new_temps[-1] = 2*dx*tau*q_bottom/k + 2*tau*(temps[-2] - temps[-1]) + temps[-1]
    for m in range(len(temps)):
        if m > 0 and m < (len(temps)-1):
            new_temps[m] = tau*temps[m-1] + (1 - 2*tau)*temps[m] + tau*temps[m+1]

    for x in range(len(temps)):
        temps[x] = new_temps[x]
        line.append((dx*x, temps[x] - 273.15))
    
    if (i+1) % 60 == 0:
        distribution_chart.add(f'{(i+1)/60} min', line)

    mid_temp_line.append(((i+1)*dt, temps[25] - 273.15))

mid_temp_chart = pygal.XY(stroke=True, show_dots=False)
mid_temp_chart.title = 'Temperature change at the midpoint of the Steak'
mid_temp_chart.add('midpoint', mid_temp_line)

distribution_chart.render_to_file(f'{getcwd()}/tmp/distribution_chart.svg')
mid_temp_chart.render_to_file(f'{getcwd()}/tmp/midpoint_chart.svg')
        
