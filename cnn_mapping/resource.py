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

    Capacity is for a single buffer; access cost is the cost per access; unit
    static cost is the static cost per time unit.
    '''
    pass

class Parallelism(namedtuple('Parallelism',
                             ['count'])):
    '''
    Parallelism specification.

    Immutable type.

    Parallelism attributes include count.

    Count is the number of parallel units. 
    
    Note: shared buffer level is the level
    index of the lowest shared buffer for this parallelism.
    '''
    pass

class Resource(object):
    '''
    Hardware resource specification.
    Hardware resource includes buffer hierarchy and parallel processing units.

    '''

    def __init__(self, buf_capacity_list, buf_access_cost_list,
                 buf_unit_static_cost_list, para_count_list):
        # Buffers.
        assert len(buf_capacity_list) == len(buf_access_cost_list)
        assert len(buf_capacity_list) == len(buf_unit_static_cost_list)
        
        self.bufs = [Buffer(*t) for t in zip(buf_capacity_list, \
            buf_access_cost_list, buf_unit_static_cost_list)]

        # Parallelism.
        self.paras = [Parallelism(t) for t in para_count_list]
        self.access_cost = buf_access_cost_list

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
