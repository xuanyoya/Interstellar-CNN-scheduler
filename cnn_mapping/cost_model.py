'''
Cost model.
'''
from operator import mul

import loop_enum as le
import buffer_enum as be

def get_layer_size(layer):
    '''
    Get size of ifmap, ofmap, filter of the layer 
    '''

    ifmap_size = layer.wifm * layer.hifm * layer.nifm * layer.nimg
    ofmap_size = layer.wofm * layer.hofm * layer.nofm * layer.nimg
    flmap_size = layer.wfil * layer.hfil * layer.nifm * layer.nofm
 
    return (ifmap_size, ofmap_size, flmap_size)

def get_if_access(level, point):
    '''
    Get # access of if block at current level

    The repeated access to ifmap is determined by the blocking factors and
    parallelism counts of those loops other than ifmap-related loops outside of
    this level.

    At the same buffer level, if the other loops are outside of the innermost
    loop of ifmap-related loops, their blocking factors and parallelism counts
    at this level should also contribute to the number of accesses.
    '''
    
    ex_order_index = min(point.loop_order(le.OX)[level], 
        point.loop_order(le.OY)[level], 
        point.loop_order(le.IC)[level], 
        point.loop_order(le.ON)[level])

    fx_exclusive = point.loop_order(le.FX)[level] < ex_order_index
    fy_exclusive = point.loop_order(le.FY)[level] < ex_order_index
    oc_exclusive = point.loop_order(le.OC)[level] < ex_order_index

    fx_acc = reduce(mul, point.loop_blocking(le.FX)[level+fx_exclusive:], 1) 
    fy_acc = reduce(mul, point.loop_blocking(le.FY)[level+fy_exclusive:], 1) 
    oc_acc = reduce(mul, point.loop_blocking(le.OC)[level+oc_exclusive:], 1) 

    fx_par = reduce(mul, point.loop_partitioning(le.FX)[level+fx_exclusive:], 1) 
    fy_par = reduce(mul, point.loop_partitioning(le.FY)[level+fy_exclusive:], 1) 
    oc_par = reduce(mul, point.loop_partitioning(le.OC)[level+oc_exclusive:], 1) 

    return fx_acc * fy_acc * oc_acc * fx_par * fy_par * oc_par


def get_of_access(level, point):
    '''
    Get # access of of block at current level

    See comments in routine for ifmap.
    '''

    ex_order_index = min(point.loop_order(le.OX)[level], 
        point.loop_order(le.OY)[level], 
        point.loop_order(le.OC)[level], 
        point.loop_order(le.ON)[level])

    fx_exclusive = point.loop_order(le.FX)[level] < ex_order_index
    fy_exclusive = point.loop_order(le.FY)[level] < ex_order_index
    ic_exclusive = point.loop_order(le.IC)[level] < ex_order_index

    fx_acc = reduce(mul, point.loop_blocking(le.FX)[level+fx_exclusive:], 1) 
    fy_acc = reduce(mul, point.loop_blocking(le.FY)[level+fy_exclusive:], 1) 
    ic_acc = reduce(mul, point.loop_blocking(le.IC)[level+ic_exclusive:], 1) 

    fx_par = reduce(mul, point.loop_partitioning(le.FX)[level+fx_exclusive:], 1) 
    fy_par = reduce(mul, point.loop_partitioning(le.FY)[level+fy_exclusive:], 1) 
    ic_par = reduce(mul, point.loop_partitioning(le.IC)[level+ic_exclusive:], 1) 

    return fx_acc * fy_acc * ic_acc * fx_par * fy_par * ic_par
   
        
def get_fl_access(level, point):
    '''
    Get # access of fl block at current level

    See comments in routine for ifmap.
    '''

    ex_order_index = min(point.loop_order(le.FX)[level], 
        point.loop_order(le.FY)[level], 
        point.loop_order(le.IC)[level], 
        point.loop_order(le.OC)[level])

    ox_exclusive = point.loop_order(le.OX)[level] < ex_order_index
    oy_exclusive = point.loop_order(le.OY)[level] < ex_order_index
    on_exclusive = point.loop_order(le.ON)[level] < ex_order_index

    ox_acc = reduce(mul, point.loop_blocking(le.OX)[level+ox_exclusive:], 1) 
    oy_acc = reduce(mul, point.loop_blocking(le.OY)[level+oy_exclusive:], 1)
    on_acc = reduce(mul, point.loop_blocking(le.ON)[level+on_exclusive:], 1) 

    ox_par = reduce(mul, point.loop_partitioning(le.OX)[level+ox_exclusive:], 1) 
    oy_par = reduce(mul, point.loop_partitioning(le.OY)[level+oy_exclusive:], 1) 
    on_par = reduce(mul, point.loop_partitioning(le.ON)[level+on_exclusive:], 1) 

    return ox_acc * oy_acc * on_acc * ox_par * oy_par * on_par


def get_if_size(blocking_accum_list, partitioning_accum_list, layer):
    '''
    Get size of if block at current level
    '''
 
    fx_acc = blocking_accum_list[le.FX] * partitioning_accum_list[le.FX] 
    fy_acc = blocking_accum_list[le.FY] * partitioning_accum_list[le.FY] 
    ox_acc = blocking_accum_list[le.OX] * partitioning_accum_list[le.OX]
    oy_acc = blocking_accum_list[le.OY] * partitioning_accum_list[le.OY]
    width = fx_acc + (ox_acc - 1) * layer.wstd
    height = fy_acc + (oy_acc - 1) * layer.hstd

    return width * height * \
    blocking_accum_list[le.IC] * partitioning_accum_list[le.IC] * \
    blocking_accum_list[le.ON] * partitioning_accum_list[le.ON]

def get_of_size(blocking_accum_list, partitioning_accum_list):
    '''
    Get size of of block at current level
    '''
 
    return blocking_accum_list[le.OX] * partitioning_accum_list[le.OX] * \
    blocking_accum_list[le.OY] * partitioning_accum_list[le.OY] * \
    blocking_accum_list[le.OC] * partitioning_accum_list[le.OC] * \
    blocking_accum_list[le.ON] * partitioning_accum_list[le.ON]
   
        
def get_fl_size(blocking_accum_list, partitioning_accum_list):
    '''
    Get size of fl block at current level
    '''
 
    return blocking_accum_list[le.FX] * partitioning_accum_list[le.FX] * \
    blocking_accum_list[le.FY] * partitioning_accum_list[le.FY] * \
    blocking_accum_list[le.IC] * partitioning_accum_list[le.IC] * \
    blocking_accum_list[le.OC] * partitioning_accum_list[le.OC]


def get_access(num_levels, point):
    '''
    Get the total access of each block at each level,
    return the list as 
    [(if_block_access, of_block_access, fl_block_access), ...].
 
    Assume all the buffers are inclusive, so buffers in lower level 
    appear in higher level as well.

    For the parallelism case assume read from next memory level,
    '''
    #TODO support more access modes in parallelism case
    #TODO support more customized memory
    #TODO more access at overlapped boundary
    
    access_list = []
    for level in xrange(num_levels):
        if_block_access = get_if_access(level, point)
        of_block_access = get_of_access(level, point)
        fl_block_access = get_fl_access(level, point)
        access_list.append((if_block_access, of_block_access, fl_block_access))

    return access_list


def get_block_size(point, layer, level):
    blocking_accum_list = []
    partitioning_accum_list = []
    for i in xrange(le.NUM):
        blocking_accum_list.append(reduce(mul, point.loop_blocking(i)[:level+1], 1))
        partitioning_accum_list.append(reduce(mul, point.loop_partitioning(i)[:level+1], 1)) #FIXME inclusive mode also duplicates data

    if_block_size = get_if_size(blocking_accum_list, partitioning_accum_list, layer)
    of_block_size = get_of_size(blocking_accum_list, partitioning_accum_list)
    fl_block_size = get_fl_size(blocking_accum_list, partitioning_accum_list)

    return (if_block_size, of_block_size, fl_block_size)


def get_block_sizes(num_levels, point, layer):
    '''
    Get size of ifmap, ofmap, filter 
    '''
    block_list = []
    for level in xrange(num_levels):
        block_list.append(get_block_size(point, layer, level))

    return block_list


def fit_in_level(cap, blocks):
    return sum(blocks) <= cap

def valid_partition(resource, point, level):
    max_parallelism = resource.parallelism(level).count

    actual_parallelism = 1 
    for i in xrange(le.NUM):
        actual_parallelism *= point.loop_partitioning(i)[level]

    return actual_parallelism <= max_parallelism  

def valid_mapping_point(resource, point, layer, level):
    valid = fit_in_level(resource.buffer(level).capacity, 
             get_block_size(point, layer, level)) \
             and valid_partition(resource, point, level)    
    return valid 

def get_cost(resource, point, layer, verbose=False):
    '''
    Get the cost of the given mapping point on given resource.

    If the point is not feasible on the resource, return inf.
    '''
    #TODO include static energy

    num_levels = resource.buffer_levels()
    assert len(point.loop_blockings[0]) == num_levels, \
    "number of blockings does not match with number of memory " \
    "levels: %d" % num_levels 
    
    access_list  = get_access(num_levels, point)
    block_size_list = get_block_sizes(num_levels, point, layer)
    layer_size = get_layer_size(layer)
    
    if verbose:
        print 'access_list: ', access_list
        print 'block_size_list: ', block_size_list
        print 'layer_size: ', layer_size

    total_cost = 0.0
    for i in xrange(num_levels):
        ''' List of total access of each buffer at level i'''
        if not valid_mapping_point(resource, point, layer, i):
           #if not fit_in_level(resource.buffer(i).capacity, block_size_list[i]):
           return float("inf")
        buffer_access = map(mul, access_list[i], layer_size) 
        total_cost += sum(buffer_access) * resource.buffer(i).access_cost

    return total_cost
