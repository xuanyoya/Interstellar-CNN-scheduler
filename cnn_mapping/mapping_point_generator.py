'''
Mapping point generator

Current implementation only supports the blocking factor and 
parallelism to be factors of the layer size 
'''

#from __future__ import division
import itertools
import copy
from operator import mul

from mapping_point import MappingPoint
from cache import Cache
import cost_model

import loop_enum as le
import buffer_enum as be
import utils

def get_fixed_partitioning(num_levels, hint):
    '''
    Get a prefixed partitioning from hint
    Helper function used for developping
    '''
    #TODO remove this function

    if not hint:
        return [(1,) * num_levels] * le.NUM  

    partitioning_list = [] 
    for loop in xrange(le.NUM):
        partitioning = [1] * num_levels
        if loop in hint:
            for i in xrange(num_levels):
                if hint[loop][i]:
                    partitioning[i] = hint[loop][i][2]
        partitioning_list.append(tuple(partitioning))
    return partitioning_list 

def get_non_empty_loops(point, num_levels):
    ''' 
    non_empty_loops is a list that contains #levels tuples, 
    each tuple contains the loop whose size is not 1 at this level 
    '''
    blocking = zip(*(point.loop_blockings))
    partitioning = zip(*(point.loop_partitionings))
 
    non_empty_loops = []
    for i in xrange(num_levels):
        t0 = blocking[i]
        t1 = partitioning[i]
        non_empty_blocking = [i for i, e in enumerate(t0) if e != 1]
        non_empty_partitioning = [i for i, e in enumerate(t1) if e != 1]
        non_empty_loop = list(set().union(non_empty_blocking, non_empty_partitioning))
        non_empty_loops.append(non_empty_loop)
    return non_empty_loops


def get_loop_order(partial_order, non_empty_loops, level):
    order_curr_level = [le.NUM-1] * le.NUM
    for i in xrange(len(non_empty_loops[level])):
        order_curr_level[non_empty_loops[level][i]] = partial_order[i]
    return order_curr_level


def opt_order_generator_function(point, num_loops, num_levels):
    '''
    Smart loop_order_list generator.

    We need this because the general one can easily generate 
    more than 10^10 loop orders

    We reduce the number of generated loop orders by only 
    order the loops whose size at current level is not 1 
    '''
    non_empty_loops = get_non_empty_loops(point, num_levels)
    #print "non_empty_loops: ", non_empty_loops
 
    all_order_permutations = [] 
    for level in xrange(num_levels):
        one_level_permutations = []
        for order in itertools.permutations(range(len(non_empty_loops[level]))):
            one_level_permutations.append(get_loop_order(order, non_empty_loops, level))
        all_order_permutations.append(one_level_permutations)

    for loop_order in itertools.product(*all_order_permutations):
        yield zip(*loop_order)
    
def level_order_generator_function(point, num_loops, non_empty_loops, level):
 
    for order in itertools.permutations(range(len(non_empty_loops[level]))):
        yield get_loop_order(order, non_empty_loops, level)
   
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


def loop_tile_with_para_hint(tile_permutations, loop_extent, num_level, loop_hint):
    para_hint = loop_hint[0][2]
    #TODO use faster way for this checking
    for i in factors(loop_extent):
        if i >= para_hint :
            recursive_tile(tile_permutations, [i], loop_extent/i, 1, num_level)         
  
def loop_tile_with_hint(tile_permutations, loop_extent, num_level, loop_hint):
    #TODO support more than 1 level of para hint
    for level in xrange(num_level):
        if loop_hint[level] != None:
            loop_hint_level = level
            break

    blocking_hint = 1 if loop_hint[loop_hint_level][1] == None else loop_hint[loop_hint_level][1]
    assert loop_hint[loop_hint_level][2] 
    para_hint = loop_hint[loop_hint_level][2]
    #para_hint = 1 if loop_hint[loop_hint_level][2] == None else loop_hint[loop_hint_level][2]
    blocking_factor = blocking_hint * para_hint

   
    pre_tile_permutations = [] 
    if loop_hint_level == 0 :
        pre_tile_permutations.append([])
    else : 
        for sub_extent in factors((loop_extent+blocking_factor-1)//blocking_factor):
            recursive_tile(pre_tile_permutations, [], sub_extent, 0, loop_hint_level)
 
    for pre_tile in pre_tile_permutations:
        #TODO support not fixed blocking hint
        if loop_hint[loop_hint_level][1]: 
            pre_tile.append(blocking_factor)
            blocking_accum = reduce(mul, pre_tile, 1)
            recursive_tile(tile_permutations, pre_tile, (loop_extent+blocking_accum-1)//blocking_accum, loop_hint_level+1, num_level)
        else:
            blocking_accum = reduce(mul, pre_tile, 1)
            for i in factors((loop_extent+blocking_accum-1)//blocking_accum):
                if i >= para_hint:
                    new_pre_tile= copy.copy(pre_tile)
                    new_pre_tile.append(i)
                    new_blocking_accum = blocking_accum * i
                    recursive_tile(tile_permutations, new_pre_tile,
                        (loop_extent+new_blocking_accum-1)//new_blocking_accum, loop_hint_level+1, num_level)
                     

def loop_tile(loop_extent, num_level, loop_hint=None):
    
    tile_permutations = []
    if not loop_hint:
        recursive_tile(tile_permutations, [], loop_extent, 0, num_level)   
    else:
        loop_tile_with_hint(tile_permutations, loop_extent, num_level, loop_hint)
    '''
    elif loop_hint[0][1] and loop_hint[0][2]:
        #TODO hint not only at 1st level
        blocking_factor = loop_hint[0][1] * loop_hint[0][2] 
        new_loop_extent = (loop_extent + blocking_factor - 1 )//(blocking_factor)
        recursive_tile(tile_permutations, [blocking_factor], 
                              new_loop_extent, 1, num_level)
    else:
        loop_tile_with_para_hint(tile_permutations, loop_extent, num_level, loop_hint)
    '''
    return tile_permutations

def opt_valid_blocking(blocking_cache, resource, layer, blocking):
   num_levels = resource.buffer_levels()
   blocking_tuple = zip(*blocking)
   dummy_partitioning = [(1,) * num_levels] * le.NUM  
   dummy_mapping_point = MappingPoint(None, list(blocking), dummy_partitioning)
  
   '''
   Use cache to compute valid of first level
   '''
   level = 0 
   value_in_cache = blocking_cache.read_cache(level, blocking_tuple[level]) 
   if value_in_cache == None: 
       valid = cost_model.valid_blocking_size_current_level(resource, dummy_mapping_point, layer, level)
       blocking_cache.write_cache(level, blocking_tuple[level], valid)
   else :
       valid = value_in_cache
   if not valid:
       return False
 

   for level in xrange(1, num_levels):
       if not cost_model.valid_blocking_size_current_level(resource, dummy_mapping_point, layer, level):
           return False
   return True 
    
def blocking_generator_function(resource, layer, hint=None ,verbose=False):

    '''
    Generate all possible loop tilings for each loop,
    store them in one list. 
    '''
    num_levels = resource.buffer_levels()

    all_tile_permutations = []
    for i in xrange(le.NUM):
        loop_hint = hint[i] if hint and i in hint else None
        all_tile_permutations.append(loop_tile(layer.sizes[i], num_levels, loop_hint))

    '''
    Generate all possible loop tilings for all loops,
    then transform the data organizations to match with loop_blocking_list 
    Use cache to buffer the valid status of blocking for the first level
    '''
    blocking_cache = Cache(1, 100)
    for tile in itertools.product(*all_tile_permutations):
        #TODO here the generated is a list of lists, not a list of tuples
        #if cost_model.valid_blocking_size(resource, dummy_mapping_point, layer):
        if opt_valid_blocking(blocking_cache, resource, layer, tile):
            yield list(tile)

'''
def partition_loops(loops, para, num_level):
   partitioned_loop = []
   partitioned_para = []

   para_factors = list(factors(para.count))     
   for f in para_factors[1:]: #excluding 1
       for i in xrange(len(loops)):
           if f <= loops[i] : 
               p = [1] * le.NUM
               p[i] = f
               l = list(loops)
               l[i] = (loops[i] + f - 1) // f #ceiling division
               partitioned_loop.append(l)      
               partitioned_para.append(p)      
        
   return [partitioned_loop, partitioned_para]


def partition_blocking(lp, resource):
    num_level = resource.buffer_levels()

    
    partitioned_loops = []
    partitioned_paras = []

    para_index = [i for i, e in enumerate(resource.paras) if e.count != 1]    
    for index in para_index:
        para = resource.paras[index]
        partitioned_loop, partitioned_para = partition_loops(lp[index], para, num_level)
        partitioned_loops.append(partitioned_loop)
        partitioned_paras.append(partitioned_para)
    
    iter_partition_loops = list(itertools.product(*partitioned_loops))
    iter_partition_paras = list(itertools.product(*partitioned_paras))     
    #print iter_partition_loops
    #print iter_partition_paras
    return [iter_partition_loops, iter_partition_paras]
'''

def current_level_recursive_partition_blocking(para_permutation, slb, slp, cur_loop, cur_factor, para_count):
    if cur_loop == le.NUM -1 :
        if cur_factor <= slb[le.NUM-1] : 
            slp.append(cur_factor)
            para_permutation.append(slp)
        return
    else :
        for f in list(factors(cur_factor)) :
            if f <= slb[cur_loop] :
                new_slp = copy.copy(slp)
                new_slp.append(f) #TODO not exact divide case 
                current_level_recursive_partition_blocking(para_permutation, slb, new_slp, cur_loop+1, cur_factor/f, para_count)    


def parallel_blocking_generator_function(lp, resource):
    num_level = resource.buffer_levels()

    para_index = [i for i, e in enumerate(resource.paras) if e != 1]
    para_permutations = []
    for index in para_index:
        para = resource.paras[index]
        para_permutation = []
        current_level_recursive_partition_blocking(para_permutation, lp[index], [], 0, para.count, para.count) #FIXME check non-para level
        para_permutations.append(para_permutation)

    for partition in itertools.product(*para_permutations) :
        yield partition

def blocking_partitioning_generator_function_with_hint(resource, layer, hint, verbose=False):
    
    #loop_blocking_list and loop_partitioning_list generator.
    assert hint    
    num_level = resource.buffer_levels()
    blocking_generator = blocking_generator_function(resource, layer, hint, verbose)

    partitioning_list = get_fixed_partitioning(num_level, hint) 
    for loop_blocking in blocking_generator: 
       #print "loop_blocking: ", loop_blocking

       loop_blocking_reshape = zip(*loop_blocking)
       loop_partitioning_reshape = zip(*partitioning_list)
       partitioned_loop_blocking_reshape = []
       for level in xrange(num_level):
           partitioned_loop_blocking_reshape.append([ (x+y-1) // y 
               for x, y in zip(loop_blocking_reshape[level], loop_partitioning_reshape[level])])   #TODO check if using two maps with floordiv is faster 
       blocking_list = zip(*partitioned_loop_blocking_reshape)
       dummy_mapping_point = MappingPoint(None, blocking_list, partitioning_list)
       if cost_model.valid_partitioning(resource, dummy_mapping_point, layer, verbose):
       #if cost_model.valid_mapping_point(resource, dummy_mapping_point, layer, verbose):
           yield [blocking_list, partitioning_list]


def blocking_partitioning_generator_function(resource, layer, verbose=False):
    
    #loop_blocking_list and loop_partitioning_list generator.
    
    num_level = resource.buffer_levels()
    blocking_generator = blocking_generator_function(resource, layer, None, verbose)

    for loop_blocking in blocking_generator:
        #print "loop_blocking: ", loop_blocking
        
        loop_blocking_reshape = zip(*loop_blocking)
        pb_generator = parallel_blocking_generator_function(loop_blocking_reshape, resource)
        
        for partition in pb_generator:
            partitioned_loop_blocking_reshape = []
            for level in xrange(num_level):
                partitioned_loop_blocking_reshape.append([ (x+y-1) // y 
                    for x, y in zip(loop_blocking_reshape[level], partition[level])])   #TODO check if using two maps with floordiv is faster 
            blocking_list = zip(*partitioned_loop_blocking_reshape)
            partitioning_list = zip(*partition)
            
            dummy_mapping_point = MappingPoint(None, blocking_list, partitioning_list)
            if cost_model.valid_partitioning(resource, dummy_mapping_point, layer, verbose):
            #if cost_model.valid_mapping_point(resource, dummy_mapping_point, layer, verbose):
                yield [blocking_list, partitioning_list]
    
        

def opt_get_best_loop_order(resource, layer, point, verbose=False):
    '''
    When no paritioning, the cost of the current level only depends on the current 
    level loop orders, given the blocking factors. Thus we can leverage this to 
    find the best loop order for each level individually. 
    '''
    num_levels = resource.buffer_levels()
    best_loop_order = []
    blocking = point.loop_blockings
    partitioning = point.loop_partitionings
    #dummy_partitioning = [(1,) * num_levels] * le.NUM 
    non_empty_loops = get_non_empty_loops(point, num_levels)
    #print blocking, partitioning

    best_cost = 0
    para_level = 0
    for level in xrange(num_levels):
        smallest_cost = float("inf") 
        for curr_level_order in level_order_generator_function(point, le.NUM, non_empty_loops, level):
            dummy_loop_order = [[0] * le.NUM] * num_levels 
            dummy_loop_order[level] = curr_level_order
            #print zip(*dummy_loop_order)
            mapping_point = MappingPoint(zip(*dummy_loop_order), blocking, partitioning)        
            if level <= 0 or resource.paras[level-1].count <= 1 \
                or resource.paras[level-1].access_mode < 1:
                curr_cost = cost_model.get_level_cost(resource, mapping_point, layer, level, verbose)
            else:
                curr_cost = cost_model.get_array_and_curr_level_cost(resource, mapping_point, layer, level, verbose) 
            if curr_cost < smallest_cost:
                best_curr_level_order = curr_level_order 
                smallest_cost = curr_cost
            if resource.mac_capacity == 0 and level == 0:
                break
        best_loop_order.append(best_curr_level_order)
        best_cost += smallest_cost

    return best_cost, zip(*best_loop_order)

def opt_mapping_point_generator_function(resource, layer, hint=None, verbose=False):
    '''
    Mapping point generator.

    Generates a new mapping point each iteration.
    '''

    num_levels = resource.buffer_levels()

    if not hint:
        blocking_partitioning_generator = \
            blocking_partitioning_generator_function(resource, layer)
    else :
         blocking_partitioning_generator = \
            blocking_partitioning_generator_function_with_hint(resource, layer, hint)

    #dummy_partitioning = [(1,) * num_levels] * le.NUM  

    smallest_cost = float("inf")
    best_mapping_point = None 
    for blocking_partitioning in blocking_partitioning_generator:
        ''' 
           dummy_mapping_point is used to validate the current blocking_partitioning,
           and abandon the ones that exceed the buffer size at any level.
           Since this validation does not depend on loop_orders, we perform the validation
           at this early stage, so that we can avoid generating all the loop orders for 
           an invalid blocking_partitioning 
        '''
        if verbose >= 2:
            print "Find best order for schedule: ", blocking_partitioning
        [blocking, partitioning] = blocking_partitioning
        dummy_mapping_point = MappingPoint(None, blocking, partitioning)
        #print "blocking_partitioning: ", blocking_partitioning
        cost, loop_order = opt_get_best_loop_order(resource, layer, dummy_mapping_point, verbose)
        if cost < smallest_cost:
            smallest_cost = cost
            best_mapping_point = MappingPoint(loop_order, blocking, partitioning)
            if verbose:
                print "best loop order: ", best_mapping_point.loop_orders
                print "Update smallest cost: ", smallest_cost
                print "Update best shedule: ", utils.print_loop_nest(best_mapping_point)
    assert best_mapping_point, "No valid mapping point found."
    return smallest_cost, best_mapping_point
 

def mapping_point_generator_function(resource, layer, hint=None, verbose=False):
    '''
    Mapping point generator.

    Generates a new mapping point each iteration.
    '''

    num_levels = resource.buffer_levels()

    blocking_partitioning_generator = \
        blocking_partitioning_generator_function(resource, layer, hint)

    for blocking_partitioning in blocking_partitioning_generator:
        ''' 
           dummy_mapping_point is used to validate the current blocking_partitioning,
           and abandon the ones that exceed the buffer size at any level.
           Since this validation does not depend on loop_orders, we perform the validation
           at this early stage, so that we can avoid generating all the loop orders for 
           an invalid blocking_partitioning 
        '''
        [blocking, partitioning] = blocking_partitioning
        dummy_mapping_point = MappingPoint(None, blocking, partitioning)
        #print "blocking_partitioning: ", blocking_partitioning
        if cost_model.valid_mapping_point(resource, dummy_mapping_point, layer, verbose):
            #opt_order_generator_function(dummy_mapping_point, le.NUM, num_levels)
            order_generator = \
                opt_order_generator_function(dummy_mapping_point, le.NUM, num_levels)
            for loop_order in order_generator:
                mapping_point = MappingPoint(loop_order, \
                                blocking, \
                                partitioning)
                yield mapping_point
            
