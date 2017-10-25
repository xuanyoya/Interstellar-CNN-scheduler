'''
Hardware resource types.
'''
#import numpy as np
from collections import namedtuple

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
                             ['count', 'access_mode'])):
    '''
    Parallelism specification.

    Immutable type.

    Parallelism attributes include count and access_mode.

    Count is the number of parallel units. 

    Access mode is the mode of access non-private data, 
    for example, whether access neighborhood PE, or 
    goes to next level buffer.
    
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
                 mac_capacity=1, partition_mode=None):
        # Buffers.
        assert len(buf_capacity_list) <= len(buf_access_cost_list)
        assert len(buf_capacity_list) == len(buf_unit_static_cost_list)
        
        self.bufs = [Buffer(*t) for t in zip(buf_capacity_list, \
            buf_access_cost_list, buf_unit_static_cost_list)]

        # Parallelism.
        if not partition_mode :
            partition_mode = [0] * len(para_count_list)
        else :
            for i in xrange(len(para_count_list)):
                # when using non-default partition mode, the parallelism
                # count needs to be large than 1
                assert partition_mode[i] == 0 or para_count_list <= 1 \
                       or (partition_mode[i] > 0 and para_count_list > 1)
 
        self.paras = [Parallelism(*t) for t in zip(para_count_list, \
            partition_mode)]
        self.access_cost = buf_access_cost_list
        self.mac_capacity = mac_capacity

    def buffer_levels(self):
        '''
        Return total levels of buffers in the hierarchy.
        '''
        return len(self.bufs)

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
