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
    '''

    def __init__(self, loop_order_list, loop_blockings_list,
                 loop_partitionings_list):
        # NOTE(mgao12): no value validation here; cost model needs to abandon
        # invalid mapping.
        self.loop_orders = loop_order_list
        self.loop_blockings = loop_blockings_list
        self.loop_partitionings = loop_partitionings_list

    def loop_order(self, loop):
        '''
        Loop order of the given loop.

        A tuple with loop index for each level, 
        with smaller index corresponding to inner loop.

        Tuples are organized as the same order as loop enum order.

        E.g., (FX, FY, OX, OY, OC, IC) means a loop structure as:
        E.g., [(0, 0), (1, 1), (2, 4), (3, 5), (4, 3), (5, 2)]
        means a loop structure as:
            for oy
              for ox
                for oc
                  for ic
                    for fy
                      for fx

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

        A tuple with factor for each level from inside loop to 
        outside loop.

        Tuples are organized as the same order as loop enum order.

        E.g., blocking factor at buffer level l is blocking[l].
        '''
        return self.loop_blockings[loop]

    def loop_partitioning(self, loop):
        '''
        Loop partitioning factors of the given loop. 

        A tuple with factor for each level from inside loop to outside loop.

        Tuples are organized as the same order as loop enum order.

        E.g., partitioning factor at level l is partitioning[l].
        '''
        return self.loop_partitionings[loop]
