from tspdata import TSPData
from sys import argv
from mip.model import *
from mip.constants import *
#from matplotlib.pyplot import plot

if len(argv) <= 1:
    print('enter instance name.')
    exit(1)
    
inst = TSPData(argv[1])
n = inst.n
d = inst.d
print('solving TSP with {} cities'.format(inst.n))

model = Model( )

# binary variables indicating if arc (i,j) is used on the route or not
x = [ [ model.add_var(
           var_type=BINARY) 
             for j in range(n) ] 
               for i in range(n) ]

# continuous variable to prevent subtours: each
# city will have a different "identifier" in the planned route
y = [ model.add_var(
       name='y({})'.format(i),
       lb=0.0,
       ub=n) 
         for i in range(n) ]

# objective function: minimize the distance
model += xsum( d[i][j]*x[i][j]
                for j in range(n) for i in range(n) )

# constraint : enter each city coming from another city
for i in range(n):
    model += xsum( x[j][i] for j in range(n) if j != i ) == 1, 'enter({})'.format(i)
    
# constraint : leave each city coming from another city
for i in range(n):
    model += xsum( x[i][j] for j in range(n) if j != i ) == 1, 'leave({})'.format(i)
    
# no 2 subtours
for i in range(n):
    for j in range(n):
        if j!=j:
            model += x[i][j] + x[j][i] <= 1
    
# subtour elimination
for i in range(0, n):
    for j in range(0, n):
        if i==j or i==0 or j==0:
            continue
        model += \
            y[i]  - (n+1)*x[i][j] >=  y[j] -n, 'noSub({},{})'.format(i,j)

print('model has {} variables, {} of which are integral and {} rows'.format(model.num_cols, model.num_int, model.num_rows))

st = model.optimize(max_seconds=10)

print('best route found has length {}, best possible (obj bound is) {} st: {}'.format(model.objective_value, model.objective_bound, st))

for i in range(n):
    for j in range(n):
        if x[i][j].x >= 0.98:
            print('arc ({},{})'.format(i,j))

