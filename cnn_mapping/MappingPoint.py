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
    each buffer level, because it does not make much sense to block more than
    once at a single buffer level.

    Each set of loop partitioning factors is corresponding to each parallelism
    level.
    '''

    def __init__(self, loop_order_list, loop_blockings_list,
                 loop_partitionings_list):
        # NOTE(mgao12): no value validation here; cost model needs to abandon
        # invalid mapping.
        self.loop_orders = loop_order_list
        self.loop_blockings = loop_blockings_list
        self.loop_partitionings = loop_partitionings_list

    def loop_order(self, level):
        '''
        Loop order of the given level buffer.

        A tuple with operand type enum from inside loop to outside loop.

        E.g., (FIL, IFM, OFM) means a loop structure as:
            for ofmap
                for ifmap
                    for filter
                        ...
        '''
        return self.loop_orders[level]

    def loop_blocking(self, level):
        '''
        Loop blocking factors of the given level buffer.

        A tuple with factor for each operand type in enum order.

        E.g., blocking factor for FIL is blocking[FIL].
        '''
        return self.loop_blockings[level]

    def loop_partitioning(self, idx):
        '''
        Loop partitioning factors of the given index parallelism.

        A tuple with factor for each operand type in enum order.

        E.g., partitioning factor for FIL is partitioning[FIL].
        '''
        return self.loop_partitionings[idx]

