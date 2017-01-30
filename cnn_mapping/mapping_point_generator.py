'''
Mapping point generator

Current implementation only supports the blocking factor and 
parallelism to be factors of the layer size 
'''

import itertools
import copy

from mapping_point import MappingPoint
import cost_model

import loop_enum as le
import buffer_enum as be

def get_non_empty_loops(loop_blocking_trans):
    ''' 
    non_empty_loops is a list that contains #levels tuples, 
    each tuple contains the loop whose size is not 1 at this level 
    '''

    non_empty_loops = []
    for t in loop_blocking_trans:
        non_empty_loops.append([i for i, e in enumerate(t) if e != 1])
    return non_empty_loops

#TODO optimize, current takes 30s 
def get_loop_order(partial_order, non_empty_loops):
    loop_order = []
    for level in xrange(len(non_empty_loops)):
        order_curr_level = [le.NUM-1]*le.NUM
        for i in xrange(len(non_empty_loops[level])):
            order_curr_level[non_empty_loops[level][i]] = partial_order[level][i]  
        loop_order.append(order_curr_level)
    return zip(*loop_order)

def opt_order_generator_function(bp, num_loops, num_levels):
    '''
    Smart loop_order_list generator.

    We need this because the general one can easily generate 
    more than 10^10 loop orders

    We reduce the number of generated loop orders by only 
    order the loops whose size at current level is not 1 
    '''
    non_empty_loops = get_non_empty_loops(zip(*bp))
    #print "non_empty_loops: ", non_empty_loops
 
    all_order_permutations = [] 
    for level in xrange(num_levels):
        one_level_permutations = []
        for order in itertools.permutations(range(len(non_empty_loops[level]))):
            one_level_permutations.append(order)
        all_order_permutations.append(one_level_permutations)

    for partial_order in itertools.product(*all_order_permutations):
        loop_order = get_loop_order(partial_order, non_empty_loops)
        yield loop_order
    

def order_generator_function(num_loops, num_levels):
    '''
    General loop_order_list generator.
    
    Arguments are number of loop types, number of buffer levels.
    '''

    '''Generator all possible loop orders in one buffer level'''
    one_level_permutations = []
    for order in itertools.permutations(range(num_loops)):
        one_level_permutations.append(order)

    all_order_permutations = []
    for level in xrange(num_levels):
        all_order_permutations.append(one_level_permutations)

    '''Consider system with all buffer levels, generator all 
       possible loop orders, then transform the data 
       organization to match with loop_order_list'''
    for order in itertools.product(*all_order_permutations):
        yield zip(*order)


def factors(n):    
    return set(reduce(list.__add__, 
                ([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0)))
 

def recursive_tile(tile_permutations, curr_loop_tile, n, curr_level, num_level):
    if curr_level == num_level - 1:
        curr_loop_tile.append(n)
        tile_permutations.append(curr_loop_tile)
        return 

    for i in factors(n):
        new_loop_tile = copy.copy(curr_loop_tile)
        new_loop_tile.append(i)
        recursive_tile(tile_permutations, new_loop_tile, n/i, curr_level+1, num_level)
            
 
def loop_tile(loop_extent, num_level):

    tile_permutations = []
    recursive_tile(tile_permutations, [], loop_extent, 0, num_level)    

    return tile_permutations

def blocking_generator_function(layer, num_level):

    '''
    Generate all possible loop tilings for each loop,
    store them in one list. 
    '''
    all_tile_permutations = []
    for i in xrange(le.NUM):
        all_tile_permutations.append(loop_tile(layer.sizes[i], num_level))

    '''
    Generate all possible loop tilings for all loops,
    then transform the data organizations to match with loop_blocking_list 
    '''
    for tile in itertools.product(*all_tile_permutations):
        #TODO here the generated is a list of lists, not a list of tuples
        yield list(tile) 

'''
def blocking_partitioning_generator_function(resource, layer):
    
    #loop_blocking_list and loop_partitioning_list generator.
    
    blocking_generator = blocking_generator_function(layer, resource.buffer_levels)

    for loop_blocking in blocking_generator:
        loop_blocking_reshape = zip(*loop_blocking)
        blocking_after_partition = []
        partitioning_after_partition = []
        for i in xrange(resource.buffer_levels()):
            curr_para = resource.parallelism(i)
            if curr_para.count == 1:
                blocking_after_partition.append(loop_blocking_reshape[i])
                partitioning_after_partition.append([1] * le.NUM)
            else :
                #The case that loops at the current level can be partitioned#
                loop_tiles_to_partition = loop_blocking_reshape[i]
                partitioned_result = partition_loops(loop_tiles_to_partition, curr_para.count)
                blocking_after_partition.append(partitioned_result[0])
                partitioning_after_partition.append(partitioned_result[1])

        #combine partitioned loop tiles to generate both 
        #   blocking_list and partitioning list 
        for :
            yield []
'''    
def valid_blocking_partitioning(resource, point, layer):
    for i in xrange(resource.buffer_levels()):
        if not cost_model.valid_mapping_point(resource, point, layer, i):
            return False

    return True

def mapping_point_generator_function(resource, layer, verbose=False):
    '''
    Mapping point generator.

    Generates a new mapping point each iteration.
    '''

    num_levels = resource.buffer_levels()

    blocking_partitioning_generator = \
        blocking_generator_function(layer, num_levels) 
        #blocking_partitioning_generator_function(resource, layer)
    
    dummy_partitioning = [(1,) * num_levels] * le.NUM 

    for blocking_partitioning in blocking_partitioning_generator:
        ''' 
           dummy_mapping_point is used to validate the current blocking_partitioning,
           and abandon the ones that exceed the buffer size at any level.
           Since this validation does not depend on loop_orders, we perform the validation
           at this early stage, so that we can avoid generating all the loop orders for 
           an invalid blocking_partitioning 
        '''
        dummy_mapping_point = MappingPoint(None, blocking_partitioning, dummy_partitioning)
        #print "blocking_partitioning: ", blocking_partitioning
        if valid_blocking_partitioning(resource, dummy_mapping_point, layer):
            opt_order_generator_function(blocking_partitioning, le.NUM, num_levels)
            order_generator = \
                opt_order_generator_function(blocking_partitioning, le.NUM, num_levels)
            for loop_order in order_generator:
                mapping_point = MappingPoint(loop_order, \
                                blocking_partitioning, \
                                dummy_partitioning)
                                #blocking_partitioning[0], \
                                #blocking_partitioning[1])
                yield mapping_point
            
