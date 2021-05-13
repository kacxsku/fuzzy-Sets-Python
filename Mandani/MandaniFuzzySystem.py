import numpy as np
import matplotlib.pyplot as plt
from fuzzython.ruleblock import RuleBlock
from fuzzython.fsets.triangular import Triangular
from fuzzython.variable import Variable
from fuzzython.adjective import Adjective
from fuzzython.systems.mamdani import MamdaniSystem
from mpl_toolkits.mplot3d import Axes3D

# speed
speed_s = Triangular((9.9, 0), (0, 1), (50, 0))
speed_a = Triangular((40, 0), (70, 1), (100, 0))
speed_f = Triangular((80, 0), (115, 1), (150, 0))
speed_v_f = Triangular((110, 0), (150, 0), (200.1, 1))
a_speed_s = Adjective('speed_s', speed_s)
a_speed_a = Adjective('speed_a', speed_a)
a_speed_f = Adjective('speed_f', speed_f)
a_speed_v_f = Adjective('speed_v_f', speed_v_f)
speed = Variable('speed', 'km/h', a_speed_s, a_speed_a, a_speed_f, a_speed_v_f)

#visibility
v_p = Triangular((0.04, 0), (0, 1), (2, 0))
v_a = Triangular((0.05, 0), (2, 1), (4, 0))
v_g = Triangular((2, 0), (4, 1), (4.1, 0))
a_v_p = Adjective('v_p', v_p)
a_v_a = Adjective('v_a', v_a)
a_v_g = Adjective('v_g', v_g)
visibility = Variable('visibility', 'km', a_v_p, a_v_a, a_v_g)

#accident
accident_v_s = Triangular((-0.1, 0), (0, 1), (0.2, 0))
accident_s = Triangular((0, 0), (0.2, 1), (0.4, 0))
accident_a = Triangular((0.2, 0), (0.5, 1), (0.8, 0))
accident_b = Triangular((0.5, 0), (0.8, 0), (1.1, 1))
a_a_v_s = Adjective('accident_v_s', accident_v_s)
a_a_s = Adjective('accident_s', accident_s)
a_a_a = Adjective('accident_a', accident_a)
a_a_b = Adjective('accident_b', accident_b)
accident = Variable('accident', '%', a_a_v_s, a_a_s, a_a_a, a_a_b, defuzzification='COG', default=0)

def plot_fuzzyset(ax, fuzzy_set, x, *args, **kwargs):
    y = np.array([fuzzy_set(e) for e in x])
    ax.plot(x, y, *args, **kwargs)
    ax.set_ylim(-0.1, 1.1)
    ax.legend()

x = np.linspace(10, 201, 1000)
x2 = np.linspace(0.05, 4, 1000)
x3 = np.linspace(0, 1, 1000)
fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(12, 8))
((ax1), (ax2), (ax3)) = axs

plot_fuzzyset(ax1, speed_s, x, 'b', label='speed_small')
plot_fuzzyset(ax1, speed_a, x, 'g', label='speed_average')
plot_fuzzyset(ax1, speed_f, x, 'r', label='speed_fast')
plot_fuzzyset(ax1, speed_v_f, x, 'y', label='speed_very_fast')

plot_fuzzyset(ax2, v_p, x2, 'b', label='visibility_poor')
plot_fuzzyset(ax2, v_a, x2, 'g', label='visibility_average')
plot_fuzzyset(ax2, v_g, x2, 'r', label='visibility_good')

plot_fuzzyset(ax3, accident_v_s, x3, 'b', label='a_accident_very_small')
plot_fuzzyset(ax3, accident_s, x3, 'g', label='a_accident_small')
plot_fuzzyset(ax3, accident_a, x3, 'r', label='a_accident_average')
plot_fuzzyset(ax3, accident_b, x3, 'y', label='a_accident_big')

plt.show()

scope = locals()

accident_rule_1 = 'if speed is a_speed_s then accident is a_a_v_s'

accident_rule_2 = 'if speed is a_speed_v_f and visibility is a_v_p then accident is a_a_b'
accident_rule_3 = 'if speed is a_speed_v_f and visibility is a_v_a then accident is a_a_a'
accident_rule_4 = 'if speed is a_speed_v_f and visibility is a_v_g then accident is a_a_s'

accident_rule_5 = 'if speed is a_speed_f and visibility is a_v_p then accident is a_a_b'
accident_rule_6 = 'if speed is a_speed_f and visibility is a_v_a then accident is a_a_a'
accident_rule_7 = 'if speed is a_speed_f and visibility is a_v_g then accident is a_a_s'

accident_rule_8 = 'if speed is a_speed_a and visibility is a_v_a then accident is a_a_a'
accident_rule_9 = 'if speed is a_speed_a and visibility is a_v_p then accident is a_a_b'
accident_rule_10 = 'if speed is a_speed_a and visibility is a_v_g then accident is a_a_s'

block = RuleBlock('rb_mamdani', operators=('MIN', 'MAX', 'ZADEH'), activation='MIN', accumulation='MAX')
block.add_rules(accident_rule_1, accident_rule_2, accident_rule_3, accident_rule_4, accident_rule_5,
                accident_rule_6, accident_rule_7, accident_rule_8, accident_rule_9, accident_rule_10, scope=scope)

mamdani = MamdaniSystem('mamdani_model', block)

inputs = {'speed': 110, 'visibility': 2}
res = mamdani.compute(inputs)

# 3d graph
sampled1 = np.linspace(10, 200, 100)
sampled2 = np.linspace(0.05, 4, 100)
x, y = np.meshgrid(sampled1, sampled2)
z = np.zeros((len(sampled1), len(sampled2)))

for i in range(len(sampled1)):
    for j in range(len(sampled2)):
        inputs = {'speed': x[i, j], 'visibility': y[i, j]}
        res = mamdani.compute(inputs)
        z[i, j] = res['rb_mamdani']['accident']

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(x, y, z, rstride=1, cstride=1, cmap='viridis', linewidth=0.4, antialiased=True)
cset = ax.contourf(x, y, z, zdir='z', offset=-1, cmap='viridis', alpha=0.5)
cset = ax.contourf(x, y, z, zdir='x', offset=11, cmap='viridis', alpha=0.5)
cset = ax.contourf(x, y, z, zdir='y', offset=11, cmap='viridis', alpha=0.5)
ax.set_xlabel('speed')
ax.set_ylabel('visibility')
ax.set_zlabel('accident')
ax.view_init(30, 200)
