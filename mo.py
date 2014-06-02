colors = [['red', 'green', 'green',   'red', 'red'],
          ['red',   'red', 'green',   'red', 'red'],
          ['red',   'red', 'green', 'green', 'red'],
          ['red',   'red',   'red',   'red', 'red']]

measurements = ['green', 'green', 'green' ,'green', 'green']

p = [[1./20, 1./20, 1./20, 1./20, 1./20],
     [1./20, 1./20, 1./20, 1./20, 1./20],
     [1./20, 1./20, 1./20, 1./20, 1./20],
     [1./20, 1./20, 1./20, 1./20, 1./20]]

motions = [[0,0],[0,1],[1,0],[1,0],[0,1]]

sensor_right = 0.7

p_move = 0.8

def show(p):
    for i in range(len(p)):
        print p[i]


show(p)
