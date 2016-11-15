'''
Hardware resource types.
'''

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
                             ['count', 'shared_buffer_level'])):
    '''
    Parallelism specification.

    Immutable type.

    Parallelism attributes include count, shared buffer level.

    Count is the number of parallel units; shared buffer level is the level
    index of the lowest shared buffer for this parallelism.
    '''
    pass

class Resource(object):
    '''
    Hardware resource specification.

    Hardware resource includes buffer hierarchy and parallel processing units.

    '''

    def __init__(self, buf_capacity_list, buf_access_cost_list,
                 buf_unit_static_cost_list, para_count_list,
                 para_shared_buffer_level_list):
        # Buffers.
        self.bufs = []
        assert len(buf_capacity_list) == len(buf_access_cost_list)
        assert len(buf_capacity_list) == len(buf_unit_static_cost_list)
        for (cap, acost, uscost) in zip(buf_capacity_list,
                                        buf_access_cost_list,
                                        buf_unit_static_cost_list):
            self.bufs.append(Buffer(cap, acost, uscost))

        # Parallelism.
        self.paras = []
        assert len(para_count_list) == len(para_shared_buffer_level_list)
        for (cnt, shlvl) in zip(para_count_list,
                                para_shared_buffer_level_list):
            self.paras.append(Parallelism(cnt, shlvl))

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

    def parallelism_levels(self):
        '''
        Return total levels of parallelism in the hierarchy.
        '''
        return len(self.paras)

    def parallelism(self, idx):
        '''
        Return the specification of the idx-th parallelism.
        '''
        return self.paras[idx]
