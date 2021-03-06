import numpy as np
import matplotlib.pyplot as plt
from fuzzython.ruleblock import RuleBlock
from fuzzython.fsets.triangular import Triangular
from fuzzython.variable import Variable
from fuzzython.adjective import Adjective
from mpl_toolkits.mplot3d import Axes3D 
from fuzzython.systems.sugeno import SugenoSystem

yesterday_low = Triangular((0.9,0),(0,1),(10,0))
yesterday_medium = Triangular((1,0),(10.5,1),(20,0))
yesterday_high = Triangular((10,0),(20,1),(20.1,0))
a_yesterday_low = Adjective('yesterday_low',yesterday_low)
a_yesterday_medium = Adjective('yesterday_medium',yesterday_medium)
a_yesterday_high = Adjective('yesterday_high',yesterday_high)
yesterday = Variable('yesterday',a_yesterday_low,a_yesterday_medium,a_yesterday_high)

today_low = Triangular((0.9,0),(0,1),(10,0))
today_medium = Triangular((1,0),(10.5,1),(20,0))
today_high = Triangular((10,0),(20,1),(20.1,0))
a_today_low = Adjective('today_low',today_low)
a_today_medium = Adjective('today_medium',today_medium)
a_today_high = Adjective('today_high',today_high)
today = Variable('today',a_today_low,a_today_medium,a_today_high)

tomorrow_low = Triangular((-0.1,0),(0,1),(10,0))
tomorrow_medium = Triangular((0,0),(10,1),(20,0))
tomorrow_high = Triangular((10,0),(20,1),(20.1,0))
a_tomorrow_low = Adjective('tomorrow_low',tomorrow_low)
a_tomorrow_medium = Adjective('tomorrow_medium',tomorrow_medium)
a_tomorrow_high = Adjective('tomorrow_high',tomorrow_high)
tomorrow = Variable('tomorrow','%',a_tomorrow_low,a_tomorrow_medium,a_tomorrow_high,defuzzification='COG', default=0)

#diagrams
def plot_fuzzyset(ax, fuzzy_set, x, *args, **kwargs):
    y = np.array([fuzzy_set(e) for e in x])
    ax.plot(x, y,  *args, **kwargs)
    ax.set_ylim(-0.1, 1.1)
    ax.legend()

x = np.linspace(0,20,1000)
x2 = np.linspace(0,20,1000)
x3 = np.linspace(0,20,1000)
fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(12,8))
((ax1), (ax2), (ax3)) = axs

plot_fuzzyset(ax1, yesterday_low, x, 'b', label='yesterday_low')
plot_fuzzyset(ax1, yesterday_medium, x, 'g', label='yesterday_medium')
plot_fuzzyset(ax1, yesterday_high, x, 'r', label='yesterday_high')

plot_fuzzyset(ax2, today_low, x2, 'b', label='today_low')
plot_fuzzyset(ax2, today_medium, x2, 'g', label='today_medium')
plot_fuzzyset(ax2, today_high, x2, 'r', label='today_high')

plot_fuzzyset(ax3, tomorrow_low, x3, 'b', label='tomorrow_low')
plot_fuzzyset(ax3, tomorrow_medium, x3, 'g', label='tomorrow_medium')
plot_fuzzyset(ax3, tomorrow_high, x3, 'r', label='tomorrow_high')
plt.show()

scope = locals()

#rules
takagi_rule_1 = 'if yesterday is a_yesterday_low and today is a_today_low then z=0.9*yesterday-0.4*today-1'
takagi_rule_2 = 'if yesterday is a_yesterday_low and today is a_today_medium then z=0.2*yesterday+0.9*today'
takagi_rule_3 = 'if yesterday is a_yesterday_low and today is a_today_high then z=0.6*yesterday+0.5*today+1'

takagi_rule_4 = 'if yesterday is a_yesterday_medium and today is a_today_medium then z=0.2*yesterday+1.0*today'
takagi_rule_5 = 'if yesterday is a_yesterday_medium and today is a_today_high then z=0.9*yesterday+0.4*today+1'
takagi_rule_6 = 'if yesterday is a_yesterday_medium and today is a_today_low then z=0.4*yesterday+0.8*today'

takagi_rule_7 = 'if yesterday is a_yesterday_high and today is a_today_high then z=0.3*yesterday+1.5*today+1'
takagi_rule_8 = 'if yesterday is a_yesterday_high and today is a_today_medium then z=0.4*yesterday+0.7*today'
takagi_rule_9 = 'if yesterday is a_yesterday_high and today is a_today_low then z=0.4*yesterday+0.7*today'

block = RuleBlock('rb_takagi', operators=('MIN', 'MAX', 'ZADEH'), activation='MIN', accumulation='MAX')
block.add_rules(takagi_rule_1, takagi_rule_2, takagi_rule_3,takagi_rule_4,takagi_rule_5,takagi_rule_6,
                takagi_rule_7,takagi_rule_8,takagi_rule_9, scope=scope)

#sugeno fuzzy drive
sugeno = SugenoSystem('model_takagi', block)

inputs = {'yesterday': 10, 'today': 1}
res = sugeno.compute(inputs)

#3d graph
sampled = np.linspace(0, 20, 20)
x, y = np.meshgrid(sampled, sampled)
z = np.zeros((len(sampled),len(sampled)))

for i in range(len(sampled)):
    for j in range(len(sampled)):
        inputs = {'yesterday': x[i, j], 'today': y[i, j]}
        res = sugeno.compute(inputs)
        z[i, j] = res['rb_takagi']
            
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(x, y, z, rstride=1, cstride=1, cmap='viridis', linewidth=0.4, antialiased=True)
cset = ax.contourf(x, y, z, zdir='z', offset= -1, cmap='viridis', alpha=0.5)
cset = ax.contourf(x, y, z, zdir='x', offset= 11, cmap='viridis', alpha=0.5)
cset = ax.contourf(x, y, z, zdir='y', offset= 11, cmap='viridis', alpha=0.5)
ax.set_xlabel('yesterday')
ax.set_ylabel('today')
ax.set_zlabel('tomorrow')
ax.view_init(30, 200)
