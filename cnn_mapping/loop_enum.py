'''
Loop enum type.

Loops include filter width (FX), filter height (FY), 
output width (OX), output height (OY),
output channel (OC), input channel (IC),
batch (ON).
'''

FX = 0
FY = 1
OX = 2
OY = 3
OC = 4
IC = 5
ON = 6
NUM = 7

table = {0: 'FX', 
         1: 'FY',
         2: 'OX',
         3: 'OY',
         4: 'OC',
         5: 'IC',
         6: 'ON' }

loop_table = { 'FX': 0,
               'FY': 1,
               'OX': 2,
               'OY': 3,
               'OC': 4,
               'IC': 5,
               'ON': 6}
