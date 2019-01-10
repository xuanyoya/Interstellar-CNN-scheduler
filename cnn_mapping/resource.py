'''
Hardware resource types.
'''
#import numpy as np
from collections import namedtuple
from operator import mul
import math

class Buffer(namedtuple('Buffer',
                        ['capacity', 'access_cost', 'unit_static_cost'])):
    '''
    Buffer specification.

    Immutable type.

    Buffer attributes include capacity, access cost, unit static cost.

    Capacity is for a single buffer (If current level has parallelsim, 
    then it is the capacity of the buffer bank inside each parallel 
    units); access cost is the cost per access; 
    unit static cost is the static cost per time unit.
    '''
    pass

class Parallelism(namedtuple('Parallelism',
                             ['count', 'access_mode', 'array_access_cost', 'array_dim', 'array_width'])):
    '''
    Parallelism specification.

    Immutable type.

    Parallelism attributes include count and access_mode.

    Count is the number of parallel units. 

    Access mode is the mode of access non-private data, 
    for example, whether access neighborhood PE, or 
    goes to next level buffer.

    Array access cost is the cost of accessing array level buffers.

    Array dimension is the dimension of PE array, whether it is 1D or 2D.

    Array width is the width of PE array, if 1D array, same as array dimension. 
    if 2D array, sqrt(array_dim)
    
    Note: shared buffer level is the level
    index of the lowest shared buffer for this parallelism.
    '''
    pass

class Resource(object):
    '''
    Hardware resource specification.
    Hardware resource includes buffer hierarchy and parallel processing units.
    
    mac_capacity[0, 1], determines whether MAC can buffer 1 output.
    '''

    def __init__(self, buf_capacity_list, buf_access_cost_list,
                 buf_unit_static_cost_list, para_count_list,  
                 mac_capacity=1, partition_mode=None, array_access_cost=None, 
                 array_dim = None, utilization_threshold = 0.75, replication=True):

        # Buffers.
        assert len(buf_capacity_list) == len(buf_access_cost_list)
        assert len(buf_capacity_list) == len(buf_unit_static_cost_list)
        assert len(buf_capacity_list) == len(para_count_list)
        
        self.bufs = [Buffer(*t) for t in zip(buf_capacity_list, \
            buf_access_cost_list, buf_unit_static_cost_list)]

        self.num_levels = len(self.bufs)
        # Parallelism.
        array_access_costs = [None] * len(para_count_list)
        if not partition_mode :
            partition_mode = [0] * len(para_count_list)
        else :
            array_level = 0
            for i in xrange(self.num_levels):
                # when using non-default partition mode, the parallelism
                # count needs to be large than 1
                assert partition_mode[i] == 0 or para_count_list <= 1 \
                       or (partition_mode[i] > 0 and para_count_list > 1)
                if partition_mode[i] == 1 or partition_mode[i] == 2:
                    array_access_costs[i] = array_access_cost[array_level]
                    array_level += 1
 
        self.para_index = [i for i, e in enumerate(para_count_list) if e != 1]

        if not array_dim:
            array_dim = [2 if e != 1 else 1 for e in para_count_list]

        array_width = [para_count_list[i] if array_dim[i] == 1 else int(math.sqrt(para_count_list[i])) for i in xrange(self.num_levels)]
 
        self.paras = [Parallelism(*t) for t in zip(para_count_list, \
            partition_mode, array_access_costs, array_dim, array_width)]
        self.access_cost = buf_access_cost_list
        self.mac_capacity = mac_capacity
        self.array_access_cost = array_access_cost
        self.para_count_list = para_count_list
        self.utilization_threshold = utilization_threshold
        self.replication = replication

    @classmethod
    def arch(cls, info):
        return cls(info["capacity"], info["access_cost"], info["static_cost"],
                        info["parallel_count"], info["mac_capacity"], info["parallel_mode"],
                        info["parallel_cost"], info["array_dim"], info["utilization_threshold"], info["replication"])  

    def buffer_levels(self):
        '''
        Return total levels of buffers in the hierarchy.
        '''
        return self.num_levels

    def buffer(self, level):
        '''
        Return the specification of the buffer of the given level.
        '''
        return self.bufs[level]


    def parallelism(self, level):
        '''
        Return the specification of the parallelism of the given level.
        '''
        return self.paras[level]

    def total_parallelism(self):
        '''
        Return the specification of the total parallelism.
        '''
        return reduce(mul, self.para_count_list, 1)
