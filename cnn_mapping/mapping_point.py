'''
Type for a specific mapping point.
'''

class MappingPoint(object):
    '''
    Configurations of a specific mapping.

    Mapping includes the complete description of the loop order and loop
    blocking factors of each buffer level, loop partitioning onto each level of
    parallel units, etc.

    Each loop order and each set of loop blocking factors are corresponding to
    each loop at all buffer levels, because it does not make much sense to block
    more than once at a single buffer level.

    Each set of loop partitioning factors is corresponding to number of parallelism of
    each loop at all all levels.

    Partition mode is the access mode in parallelism case. 
        0(default): access to next level of memory
        1: access buffers in neighbor processing units
    '''

    def __init__(self, loop_order_list, loop_blockings_list,
                 loop_partitionings_list, para_loop_dim_list=None):
        # NOTE(mgao12): no value validation here; cost model needs to abandon
        # invalid mapping.
        self.loop_orders = loop_order_list
        self.loop_blockings = loop_blockings_list
        self.loop_partitionings = loop_partitionings_list
        self.para_loop_dim = para_loop_dim_list

    def loop_order(self, loop):
        '''
        Loop order of the given loop.

        Return a tuple of the order indices for the same loop at all buffer
        levels, i.e., if a tuple for loop OX is returned, and the first 
        element of this tuple t[0] = 2, then loop OX is the third innermost 
        loop at the first buffer level.  

        Tuples are organized as the same order as loop enum order.

        E.g., for a two-level memory hierachy, each tuple contains two 
        elements, [(0, 0), (1, 1), (2, 4), (3, 5), (4, 3), (5, 2), (6, 6)]
        means for the first loop (FX = 0), at both levels FX is at the
        innermost (tuple (0, 0)), etc.. I.e., it means a loop structure as:
          for on
            for oy
              for ox
                for oc
                  for ic
                    for fy
                      for fx

                        for on
                          for ic
                            for oc
                              for oy
                                for ox
                                  for fy
                                    for fx
                                      ...
        '''
        return self.loop_orders[loop]

    def loop_blocking(self, loop):
        '''
        Loop blocking factors of the given loop.

        Return a tuple of factors for the given loop at all buffer levels, from
        inside level to outside level.

        Tuples are organized as the same order as loop enum order.

        E.g., [(4, 2), (8, 1), ...] means for the first loop (FX = 0), the
        blocking factor is 4 for the innermost level, and 2 for the next level;
        for the second loop (FY = 0), the blocking factor is 8 for the
        innermost level, and 1 for the next level.
        '''
        return self.loop_blockings[loop]

    def loop_partitioning(self, loop):
        '''
        Loop partitioning factors of the given loop.

        Return a tuple of factors for the given loop at all buffer levels, from
        inside level to outside level.

        Tuples are organized as the same order as loop enum order.

        E.g., [(4, 2), (8, 1), ...] means for the first loop (FX = 0), it is
        parallelized in 4 units for the first parallel level, and 2 for the
        next level, etc..
        '''
        return self.loop_partitionings[loop]
