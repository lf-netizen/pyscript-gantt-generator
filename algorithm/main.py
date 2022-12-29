from src import solve, read_data
import numpy as np
import pandas as pd

data = pd.DataFrame(np.array([
        ['A', 1, 2, 8, 8, 8],
        ['B', 1, 4, 2, 2, 2],
        ['C', 1, 3, 4, 4, 4],
        ['D', 2, 4, 4, 4, 4],
        ['E', 2, 5, 4, 4, 4],
        ['F', 4, 6, 5, 5, 5],
        ['G', 3, 6, 13, 13, 13],
        ['H', 5, 7, 3, 3, 3],
        ['I', 6, 7, 5, 5, 5]
        ]), 
        columns=['name', 'src', 'dst', 'tc', 'tm', 'tp'])


data = pd.DataFrame(np.array([
        ['1.',   10,   1,  1,  1,  1],
        ['2.',   1,   2,  2,  2,  2],
        ['3.',   2,   8,  0,  0,  0],
        ['3.',   4,   8,  0,  0,  0],
        ['3.',   8,   3,  3,  3,  3],
        ['4.',   1,   4,  4,  4,  4],
        ['5.',   10,   5,  5,  5,  5],
        ['6.',   3,   9,  0,  0,  0],
        ['6.',   5,   9,  0,  0,  0],
        ['6.',   9,   6,  0,  0,  0],
        ]), 
        columns=['name', 'src', 'dst', 'tc', 'tm', 'tp'])
        
solve(data)