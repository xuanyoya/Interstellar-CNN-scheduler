'''
Cost model.
'''
#import numpy as np
from operator import mul
from operator import add
import copy
import math

import loop_enum as le
import buffer_enum as be


def get_comp_cost(layer):
    '''
    Compute the computation cost, it is indepdent of other optimizations
    '''
    cost = layer.wofm * layer.hofm * layer.nifm * layer.nofm \
           * layer.nimg * layer.wfil * layer.hfil 
    return cost

def get_layer_size(layer):
    '''
    Get size of ifmap, ofmap, filter of the layer 
    '''

    ifmap_size = layer.wifm * layer.hifm * layer.nifm * layer.nimg
    ofmap_size = layer.wofm * layer.hofm * layer.nofm * layer.nimg
    flmap_size = layer.wfil * layer.hfil * layer.nifm * layer.nofm
 
    return [ifmap_size, ofmap_size, flmap_size]


def get_if_access(level, point, layer, mac_capacity = 1):
    '''
    Get # access of if block at current level

    The repeated access to ifmap is determined by the blocking factors and
    parallelism counts of those loops other than ifmap-related loops outside of
    this level.

    At the same buffer level, if the other loops are outside of the innermost
    loop of ifmap-related loops, their blocking factors and parallelism counts
    at this level should also contribute to the number of accesses.
    '''

    if level == 0 and mac_capacity == 0:
        return layer.wfil * layer.hfil * layer.nofm / (layer.wstd * layer.hstd)
    
    ex_order_index = min(point.loop_orders[le.OX][level], 
        point.loop_orders[le.OY][level], 
        point.loop_orders[le.IC][level], 
        point.loop_orders[le.ON][level])

    fx_exclusive = point.loop_orders[le.FX][level] < ex_order_index
    fy_exclusive = point.loop_orders[le.FY][level] < ex_order_index
    oc_exclusive = point.loop_orders[le.OC][level] < ex_order_index

    fx_acc = reduce(mul, point.loop_blockings[le.FX][level+fx_exclusive:], 1) 
    fy_acc = reduce(mul, point.loop_blockings[le.FY][level+fy_exclusive:], 1) 
    oc_acc = reduce(mul, point.loop_blockings[le.OC][level+oc_exclusive:], 1) 

    # No loop orders among unrolled loops, they have the same order 
    fx_par = reduce(mul, point.loop_partitionings[le.FX][level:], 1) 
    fy_par = reduce(mul, point.loop_partitionings[le.FY][level:], 1) 
    oc_par = reduce(mul, point.loop_partitionings[le.OC][level:], 1) 

    return fx_acc * fy_acc * oc_acc * fx_par * fy_par * oc_par / (layer.wstd * layer.hstd)


def get_of_access(level, point, layer, mac_capacity = 1):
    '''
    Get # access of of block at current level

    See comments in routine for ifmap.
    '''

    if level == 0 and mac_capacity == 0 :
        return layer.wfil * layer.hfil * layer.nifm

    ex_order_index = min(point.loop_orders[le.OX][level], 
        point.loop_orders[le.OY][level], 
        point.loop_orders[le.OC][level], 
        point.loop_orders[le.ON][level])

    fx_exclusive = point.loop_orders[le.FX][level] < ex_order_index
    fy_exclusive = point.loop_orders[le.FY][level] < ex_order_index
    ic_exclusive = point.loop_orders[le.IC][level] < ex_order_index

    fx_acc = reduce(mul, point.loop_blockings[le.FX][level+fx_exclusive:], 1) 
    fy_acc = reduce(mul, point.loop_blockings[le.FY][level+fy_exclusive:], 1) 
    ic_acc = reduce(mul, point.loop_blockings[le.IC][level+ic_exclusive:], 1) 

    fx_par = reduce(mul, point.loop_partitionings[le.FX][level:], 1) 
    fy_par = reduce(mul, point.loop_partitionings[le.FY][level:], 1) 
    ic_par = reduce(mul, point.loop_partitionings[le.IC][level:], 1) 

    return fx_acc * fy_acc * ic_acc * fx_par * fy_par * ic_par
   
        
def get_fl_access(level, point, layer, mac_capacity = 1):
    '''
    Get # access of fl block at current level

    See comments in routine for ifmap.
    '''

    if level == 0 and mac_capacity == 0:
        return layer.wofm * layer.hofm * layer.nimg

    ex_order_index = min(point.loop_orders[le.FX][level], 
        point.loop_orders[le.FY][level], 
        point.loop_orders[le.IC][level], 
        point.loop_orders[le.OC][level])

    ox_exclusive = point.loop_orders[le.OX][level] < ex_order_index
    oy_exclusive = point.loop_orders[le.OY][level] < ex_order_index
    on_exclusive = point.loop_orders[le.ON][level] < ex_order_index

    ox_acc = reduce(mul, point.loop_blockings[le.OX][level+ox_exclusive:], 1) 
    oy_acc = reduce(mul, point.loop_blockings[le.OY][level+oy_exclusive:], 1)
    on_acc = reduce(mul, point.loop_blockings[le.ON][level+on_exclusive:], 1) 

    ox_par = reduce(mul, point.loop_partitionings[le.OX][level:], 1) 
    oy_par = reduce(mul, point.loop_partitionings[le.OY][level:], 1) 
    on_par = reduce(mul, point.loop_partitionings[le.ON][level:], 1) 

    return ox_acc * oy_acc * on_acc * ox_par * oy_par * on_par


def opt_get_if_access(level, point, ba_arr, pa_arr):
    '''
    Get # access of if block at current level

    The repeated access to ifmap is determined by the blocking factors and
    parallelism counts of those loops other than ifmap-related loops outside of
    this level.

    At the same buffer level, if the other loops are outside of the innermost
    loop of ifmap-related loops, their blocking factors and parallelism counts
    at this level should also contribute to the number of accesses.
    '''
    
    ex_order_index = min(point.loop_orders[le.OX][level], 
        point.loop_orders[le.OY][level], 
        point.loop_orders[le.IC][level], 
        point.loop_orders[le.ON][level])

    fx_exclusive = point.loop_orders[le.FX][level] < ex_order_index
    fy_exclusive = point.loop_orders[le.FY][level] < ex_order_index
    oc_exclusive = point.loop_orders[le.OC][level] < ex_order_index

    fx_acc = ba_arr[le.FX][level+fx_exclusive] #reduce(mul, point.loop_blockings[le.FX][level+fx_exclusive:], 1) 
    fy_acc = ba_arr[le.FY][level+fy_exclusive] #reduce(mul, point.loop_blockings[le.FY][level+fy_exclusive:], 1) 
    oc_acc = ba_arr[le.OC][level+oc_exclusive] #reduce(mul, point.loop_blockings[le.OC][level+oc_exclusive:], 1) 

    fx_par = pa_arr[le.FX][level] #reduce(mul, point.loop_partitionings[le.FX][level+fx_exclusive:], 1) 
    fy_par = pa_arr[le.FY][level] #reduce(mul, point.loop_partitionings[le.FY][level+fy_exclusive:], 1) 
    oc_par = pa_arr[le.OC][level] #reduce(mul, point.loop_partitionings[le.OC][level+oc_exclusive:], 1) 

    return fx_acc * fy_acc * oc_acc * fx_par * fy_par * oc_par 


def opt_get_of_access(level, point, ba_arr, pa_arr):
    '''
    Get # access of of block at current level

    See comments in routine for ifmap.
    '''

    ex_order_index = min(point.loop_orders[le.OX][level], 
        point.loop_orders[le.OY][level], 
        point.loop_orders[le.OC][level], 
        point.loop_orders[le.ON][level])

    fx_exclusive = point.loop_orders[le.FX][level] < ex_order_index
    fy_exclusive = point.loop_orders[le.FY][level] < ex_order_index
    ic_exclusive = point.loop_orders[le.IC][level] < ex_order_index

    #TODO
    fx_acc = ba_arr[le.FX][level+fx_exclusive] #reduce(mul, point.loop_blockings[le.FX][level+fx_exclusive:], 1) 
    fy_acc = ba_arr[le.FY][level+fy_exclusive] #reduce(mul, point.loop_blockings[le.FY][level+fy_exclusive:], 1) 
    ic_acc = ba_arr[le.IC][level+ic_exclusive] #reduce(mul, point.loop_blockings[le.OC][level+oc_exclusive:], 1) 

    fx_par = pa_arr[le.FX][level] #reduce(mul, point.loop_partitionings[le.FX][level+fx_exclusive:], 1) 
    fy_par = pa_arr[le.FY][level] #reduce(mul, point.loop_partitionings[le.FY][level+fy_exclusive:], 1) 
    ic_par = pa_arr[le.IC][level] #reduce(mul, point.loop_partitionings[le.OC][level+oc_exclusive:], 1) 


    return fx_acc * fy_acc * ic_acc * fx_par * fy_par * ic_par
   
        
def opt_get_fl_access(level, point, ba_arr, pa_arr):
    '''
    Get # access of fl block at current level

    See comments in routine for ifmap.
    '''

    ex_order_index = min(point.loop_orders[le.FX][level], 
        point.loop_orders[le.FY][level], 
        point.loop_orders[le.IC][level], 
        point.loop_orders[le.OC][level])

    ox_exclusive = point.loop_orders[le.OX][level] < ex_order_index
    oy_exclusive = point.loop_orders[le.OY][level] < ex_order_index
    on_exclusive = point.loop_orders[le.ON][level] < ex_order_index

    ox_acc = ba_arr[le.OX][level+ox_exclusive] #reduce(mul, point.loop_blockings[le.OX][level+ox_exclusive:], 1) 
    oy_acc = ba_arr[le.OY][level+oy_exclusive] #reduce(mul, point.loop_blockings[le.OY][level+oy_exclusive:], 1)
    on_acc = ba_arr[le.ON][level+on_exclusive] #reduce(mul, point.loop_blockings[le.ON][level+on_exclusive:], 1) 

    ox_par = pa_arr[le.OX][level] #reduce(mul, point.loop_partitionings[le.OX][level+ox_exclusive:], 1) 
    oy_par = pa_arr[le.OY][level] #reduce(mul, point.loop_partitionings[le.OY][level+oy_exclusive:], 1) 
    on_par = pa_arr[le.ON][level] #reduce(mul, point.loop_partitionings[le.ON][level+on_exclusive:], 1) 

    return ox_acc * oy_acc * on_acc * ox_par * oy_par * on_par



def get_if_size(blocking_accum_list, partitioning_accum_list, partitioning_list, layer):
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
    blocking_accum_list[le.ON] * partitioning_accum_list[le.ON] * \
    partitioning_list[le.OC] # Duplication when OC partitions

def get_of_size(blocking_accum_list, partitioning_accum_list, partitioning_list):
    '''
    Get size of of block at current level
    '''
 
    return blocking_accum_list[le.OX] * partitioning_accum_list[le.OX] * \
    blocking_accum_list[le.OY] * partitioning_accum_list[le.OY] * \
    blocking_accum_list[le.OC] * partitioning_accum_list[le.OC] * \
    blocking_accum_list[le.ON] * partitioning_accum_list[le.ON] * \
    partitioning_list[le.IC] * partitioning_list[le.FX] * \
    partitioning_list[le.FY]  # Duplication when IC, FX or FY partitions
   
        
def get_fl_size(blocking_accum_list, partitioning_accum_list, partitioning_list):
    '''
    Get size of fl block at current level
    '''
 
    return blocking_accum_list[le.FX] * partitioning_accum_list[le.FX] * \
    blocking_accum_list[le.FY] * partitioning_accum_list[le.FY] * \
    blocking_accum_list[le.IC] * partitioning_accum_list[le.IC] * \
    blocking_accum_list[le.OC] * partitioning_accum_list[le.OC] * \
    partitioning_list[le.OX] * partitioning_list[le.OY] *\
    partitioning_list[le.ON] # Duplication when OX, OY or ON partitions 

def get_if_bank_size(blocking_accum_list, layer):
    '''
    Get size of if block at current level
    '''
 
    fx_acc = blocking_accum_list[le.FX]  
    fy_acc = blocking_accum_list[le.FY] 
    ox_acc = blocking_accum_list[le.OX] 
    oy_acc = blocking_accum_list[le.OY] 
    width = fx_acc + (ox_acc - 1) * layer.wstd
    height = fy_acc + (oy_acc - 1) * layer.hstd

    return width * height * \
    blocking_accum_list[le.IC] * blocking_accum_list[le.ON] 

def get_of_bank_size(blocking_accum_list):
    '''
    Get size of of block at current level
    '''
 
    return blocking_accum_list[le.OX] * blocking_accum_list[le.OY] * \
    blocking_accum_list[le.OC] *blocking_accum_list[le.ON]  
   
        
def get_fl_bank_size(blocking_accum_list):
    '''
    Get size of fl block at current level
    '''
 
    return blocking_accum_list[le.FX] * blocking_accum_list[le.FY] * \
    blocking_accum_list[le.IC] * blocking_accum_list[le.OC] 


def get_array_access_and_cost(level, para, access_list, point):
    '''
    Get the access at array level from the access at the 
    lower level of memory hierachy
    '''

    para_mode = para.access_mode
    assert para_mode == 1 or para_mode == 2

    array_dim = para.array_dim
    para_count = para.array_width
    para_cost = para.array_access_cost * 1.0
    nearest_pe_cost = para_cost 
 
    [if_block_access, of_block_access, fl_block_access] = access_list
    partitions = zip(*point.loop_partitionings)[level]
    para_dim = point.para_loop_dim[level]

    partitions_nearest = [1,]*le.NUM
    partitions_far = []
    across_block_cost = [0]*array_dim
   
    if para_mode == 1:
        for i in xrange(len(para_dim)):
            para_index = para_dim[i]
            partitions_far.append([1,]*le.NUM)
            if len(para_index) == 1:
                partitions_nearest[para_index[0]] = partitions[para_index[0]]
            else:
                inner_loop, outer_loop = para_index  
                partitions_nearest[inner_loop] = partitions[inner_loop] 
                partitions_far[i][outer_loop] = partitions[outer_loop]
                across_block_cost[i] = para_cost * partitions[inner_loop] 
    
        array_if_block_access_nearest = if_block_access  * partitions_nearest[le.FX] * \
                                partitions_nearest[le.FY] * partitions_nearest[le.OC]
        array_of_block_access_nearest = of_block_access  * partitions_nearest[le.FX] * \
                                partitions_nearest[le.FY] * partitions_nearest[le.IC]
        array_fl_block_access_nearest = fl_block_access  * partitions_nearest[le.OX] * \
                                partitions_nearest[le.OY] * partitions_nearest[le.ON]
    
        array_access = [[array_if_block_access_nearest, array_of_block_access_nearest, array_fl_block_access_nearest]]
    
        for i in xrange(array_dim):
            if_partitions_far = partitions_far[i][le.FX] * partitions_far[i][le.FY] * partitions_far[i][le.OC]
            if_partitions_far = if_partitions_far if if_partitions_far != 1 else 0   
            of_partitions_far = partitions_far[i][le.FX] * partitions_far[i][le.FY] * partitions_far[i][le.IC]
            of_partitions_far = of_partitions_far if of_partitions_far != 1 else 0   
            fl_partitions_far = partitions_far[i][le.OX] * partitions_far[i][le.OY] * partitions_far[i][le.ON]
            fl_partitions_far = fl_partitions_far if fl_partitions_far != 1 else 0   
             
            if_array_block_access = if_block_access * if_partitions_far
            of_array_block_access = of_block_access * of_partitions_far
            fl_array_block_access = fl_block_access * fl_partitions_far
            
            array_access.append([if_array_block_access, of_array_block_access, fl_array_block_access])
    
        return [array_access, [nearest_pe_cost] + across_block_cost]

    elif para_mode == 2:
        for i in xrange(len(para_dim)):
            para_index = para_dim[i]
            for j in para_index:
                partitions_nearest[j] = partitions[j]
    
        array_if_block_access_nearest = if_block_access  * partitions_nearest[le.FX] * \
                                partitions_nearest[le.FY] * partitions_nearest[le.OC]
        array_of_block_access_nearest = of_block_access  * partitions_nearest[le.FX] * \
                                partitions_nearest[le.FY] * partitions_nearest[le.IC]
        array_fl_block_access_nearest = fl_block_access  * partitions_nearest[le.OX] * \
                                partitions_nearest[le.OY] * partitions_nearest[le.ON]
    
        array_access = [[array_if_block_access_nearest, array_of_block_access_nearest, array_fl_block_access_nearest]]
    
        return [array_access, [nearest_pe_cost]]



def get_access(point, layer, resource):
    '''
    Get the total access of each block at each level,
    return the list as 
    [[if_block_access, of_block_access, fl_block_access], ...].
 
    Assume all the buffers are inclusive, so buffers in lower level 
    appear in higher level as well.

    For the parallelism case assume read from next memory level,
    
    Support more access modes in parallelism case
    '''
    #TODO support more customized memory
    #TODO more access at overlapped boundary
   
 
    num_levels = resource.buffer_levels()
    mac_capacity = resource.mac_capacity

    access_list = []
    for level in xrange(num_levels):
        if_block_access = get_if_access(level, point, layer, mac_capacity)
        of_block_access = 2 * get_of_access(level, point, layer, mac_capacity) - 1 
        fl_block_access = get_fl_access(level, point, layer, mac_capacity)
        access_list.append([if_block_access, of_block_access, fl_block_access])

    #para_mode = [e.access_mode for i, e in enumerate(resource.paras) if e.access_mode != 0]
    para_mode_level = [i for i, e in enumerate(resource.paras) if e.access_mode != 0]
    partitions = zip(*point.loop_partitionings)
    array_costs = []
    if para_mode_level:
        # access at array level 
        #para_mode_level = [i for i, e in enumerate(resource.paras) if e.access_mode != 0]
        delta = 0
        for level in para_mode_level:
            if level + delta + 1 >= num_levels :
                next_level_access = [1, 1, 1]
            else:
                next_level_access = copy.copy(access_list[level + delta + 1])
                next_level_access[1] = (next_level_access[1] + 1)/2 
            array_access, array_cost = get_array_access_and_cost(level, resource.paras[level], next_level_access, point) 
            array_costs.append(array_cost)
            access_list.insert(level + delta + 1, array_access)
            delta += 1
 
    return [access_list, array_costs]

def opt_get_access(num_levels, point, mac_capacity):
    '''
    See the above function's comments. This function is just an
    optimized version of the above function 
    '''
    ''' blocking_accum_arr is reversed cumprod numpy array '''
    #TODO support mac_capacity

    #blocking_arr = np.ones((le.NUM, num_levels+1))
    #partitioning_arr = np.ones((le.NUM, num_levels+1))

    #blocking_arr[:,:-1] = np.array(point.loop_blockings)
    #partitioning_arr[:,:-1] = np.array(point.loop_partitionings)

    #blocking_accum_arr = np.ones((le.NUM, num_levels+1)) 
    #partitioning_accum_arr = np.ones((le.NUM, num_levels+1)) 

    #for i in xrange(le.NUM):
    #    blocking_accum_arr[i][:-1] = np.cumprod(blocking_arr[i][::-1])[::-1] 
    #    partitioning_accum_arr[i][:-1] = np.cumprod(partitioning_arr[i][::-1])[::-1] 

    #blocking_accum_arr = blocking_arr[...,::-1].cumprod(axis=-1)[...,::-1]
    #partitioning_accum_arr = partitioning_arr[...,::-1].cumprod(axis=-1)[...,::-1]

    #blocking_accum_arr = np.hstack((blocking_accum_arr, np.ones((le.NUM, 1))))
    #partitioning_accum_arr = np.hstack((partitioning_accum_arr, np.ones((le.NUM, 1))))


    blocking_accum_arr = []
    partitioning_accum_arr = []
    for i in xrange(le.NUM):
        ba_current_level = [1]
        pa_current_level = [1] 
        ba_tmp = 1
        pa_tmp = 1
        for level in xrange(num_levels-1, -1, -1):
            ba_tmp = ba_tmp * point.loop_blockings[i][level]
            pa_tmp = pa_tmp * point.loop_partitionings[i][level]
            ba_current_level.append(ba_tmp)
            pa_current_level.append(pa_tmp)
   
        blocking_accum_arr.append(ba_current_level[::-1])
        partitioning_accum_arr.append(pa_current_level[::-1])
 
    access_arr = np.zeros((num_levels, 3))
    for level in xrange(num_levels):
        access_arr[level][0] = opt_get_if_access(level, point, blocking_accum_arr, partitioning_accum_arr) 
        access_arr[level][1] = 2 * opt_get_of_access(level, point, blocking_accum_arr, partitioning_accum_arr) - 1 
        access_arr[level][2] = opt_get_fl_access(level, point, blocking_accum_arr, partitioning_accum_arr) 
    
    return access_arr

def get_bank_size(point, layer, level):

    blocking_accum_list = []
    for i in xrange(le.NUM):
        blocking_accum_list.append(reduce(mul, point.loop_blocking(i)[:level+1], 1))

    if_bank_size = get_if_bank_size(blocking_accum_list, layer)
    of_bank_size = get_of_bank_size(blocking_accum_list)
    fl_bank_size = get_fl_bank_size(blocking_accum_list)

    return (if_bank_size, of_bank_size, fl_bank_size)

def get_block_size(point, layer, level):

    blocking_accum_list = []
    partitioning_accum_list = []
    partitioning_reshape = zip(*point.loop_partitionings)
    partitioning_list = partitioning_reshape[level]
    for i in xrange(le.NUM):
        blocking_accum_list.append(reduce(mul, point.loop_blocking(i)[:level+1], 1))
        partitioning_accum_list.append(reduce(mul, point.loop_partitioning(i)[:level+1], 1)) #FIXME inclusive mode also duplicates data
    
    if_block_size = get_if_size(blocking_accum_list, partitioning_accum_list, partitioning_list, layer)
    of_block_size = get_of_size(blocking_accum_list, partitioning_accum_list, partitioning_list)
    fl_block_size = get_fl_size(blocking_accum_list, partitioning_accum_list, partitioning_list)

    return (if_block_size, of_block_size, fl_block_size)



def get_block_sizes(num_levels, point, layer):
    '''
    Get size of ifmap, ofmap, filter 
    '''
    bank_list = []
    block_list = []
    for level in xrange(num_levels):
        block_list.append(get_block_size(point, layer, level))
        bank_list.append(get_bank_size(point, layer, level))

    return [bank_list, block_list]

def fit_in_level(cap, blocks, invalid_underutilized):
    total_size = sum(blocks)
    if invalid_underutilized:
        return (total_size <= cap) and (2*total_size >= cap)
    else:
        return (total_size <= cap) 
 
def valid_partition_number(resource, partitioning, level):
    max_parallelism = resource.parallelism(level).count
    actual_parallelism = reduce(mul, partitioning[level], 1)
    return actual_parallelism <= max_parallelism  

def valid_partitioning_current_level(resource, point, layer, level, verbose=False):
    valid_size = fit_in_level(resource.buffer(level).capacity, \
             get_bank_size(point, layer, level), True) 

    return valid_size 

def valid_mapping_point_current_level(resource, point, layer, level, verbose=False):
    if resource.paras[level].count > 1:
        valid_size = fit_in_level(resource.buffer(level).capacity, 
             get_bank_size(point, layer, level)) 
    else :
        valid_size = fit_in_level(resource.buffer(level).capacity, 
             get_block_size(point, layer, level)) 

    partitioning = zip(*(point.loop_partitionings)) 
    valid_para = valid_partition_number(resource, partitioning, level)    

    if verbose == 3:
        print "Level ", level, ": Partitioned block size fit in bank: ", valid_size
        print "Level ", level, ": Partition number is valid: ", valid_para
    
    return valid_size and valid_para 

def valid_partitioning(resource, point, layer, verbose=False):
    para_level = resource.para_index 
    for level in para_level:
        if not valid_partitioning_current_level(resource, point, layer, level, verbose):
            return False
    return True

def valid_blocking_size_current_level(resource, point, layer, level, verbose=False):
    if level == resource.buffer_levels()-1:
        return True
    return fit_in_level(resource.buffer(level).capacity * resource.paras[level].count, 
        get_block_size(point, layer, level), (level not in resource.para_index))
        #get_block_size(point, layer, level), (level > min(resource.para_index)))


def valid_blocking_size(resource, point, layer, verbose=False):
    for level in xrange(resource.buffer_levels()):
        if not valid_blocking_size_current_level(resource, point, layer, level, verbose):
            return False
    return True 


def valid_mapping_point(resource, point, layer, verbose=False):
    for i in xrange(resource.buffer_levels()):
        if not valid_mapping_point_current_level(resource, point, layer, i, verbose):
            return False
    return True

def get_total_access_cost(resource, array_cost):
    total_access_cost = copy.deepcopy(resource.access_cost)

    if not resource.array_access_cost: 
        return total_access_cost

    para_index = [i for i, e in enumerate(resource.paras) if e.access_mode != 0]
    addition_levels = len(para_index)

    delta = 1
    for i in xrange(addition_levels):
        index = para_index[i]
        total_access_cost.insert(index+delta, array_cost[i])
        delta += 1
    return total_access_cost 

def get_array_level_cost(resource, point, layer_size, level, next_level_access, verbose=False):
    #TODO add support for other access_mode
   
    assert resource.paras[level].count and resource.paras[level].access_mode

    level_access, level_cost = get_array_access_and_cost(level, resource.paras[level], next_level_access, point) 

    total_cost = 0
    for i in xrange(len(level_access)):
        buffer_access = map(mul, level_access[i], layer_size)
        total_cost += sum(buffer_access) *level_cost[i]

    if verbose >= 2:
        print "Level ", level, " array level access: ", level_access 
 
    return total_cost


def get_array_and_curr_level_cost(resource, point, layer, level, verbose=False):
    layer_size = get_layer_size(layer)
    mac_capacity = resource.mac_capacity
   
    level_access = [get_if_access(level, point, layer, mac_capacity), \
                    get_of_access(level, point, layer, mac_capacity), \
                    get_fl_access(level, point, layer, mac_capacity)] 

    [if_access, of_access, fl_access] = level_access 

    buffer_level_access = [if_access, 2*of_access-1, fl_access]
    total_buffer_access = map(mul, buffer_level_access, layer_size)
    level_cost = sum(total_buffer_access) * resource.access_cost[level]

    if verbose >= 2:
        print "Level ", level, " access: ", buffer_level_access 
 
    level_cost += get_array_level_cost(resource, point, layer_size, level-1, level_access, verbose)

    return level_cost

    
def get_level_cost(resource, point, layer, level, verbose=False):
    layer_size = get_layer_size(layer)
    mac_capacity = resource.mac_capacity

    level_access = [get_if_access(level, point, layer, mac_capacity), \
                    2 * get_of_access(level, point, layer, mac_capacity) - 1, \
                    get_fl_access(level, point, layer, mac_capacity)] 

    buffer_access = map(mul, level_access, layer_size)
    level_cost = sum(buffer_access) * resource.access_cost[level]

    if verbose >= 2:
        print "Level ", level, " access: ", level_access 
    return level_cost


def get_total_access(resource, point, layer, verbose=False):
    layer_size = get_layer_size(layer)

    access_list, array_cost  = get_access(point, layer, resource)

    if verbose >= 2:
        print "access breakdown: ", access_list 

    total_level_access = []
    for i in xrange(len(access_list)):
        ''' List of total access of each buffer at level i'''
        if not isinstance(access_list[i][0], list):
            buffer_access = map(mul, access_list[i], layer_size)
            total_level_access.append(sum(buffer_access))
        else :
            for j in xrange(len(access_list[i])):
                buffer_access = map(mul, access_list[i][j], layer_size)
                total_level_access.append(sum(buffer_access))

    return total_level_access



def get_level_costs(resource, point, layer, verbose=False):
    num_levels = resource.buffer_levels()
    
    level_energy = []
    for level in xrange(num_levels):
        level_energy.append(get_level_cost(resource, point, layer, level))
  
    para_index = [i for i, e in enumerate(resource.paras) if e.access_mode != 0]

    delta = 1
    for index in para_index:
        array_energy = get_array_and_curr_level_cost(resource, point, layer, index+1) - level_energy[index+delta]
        level_energy.insert(index+delta, array_energy)
        delta += 1

    return level_energy      

#FIXME
def get_block_cost(resource, point, layer, verbose=False):
    '''
    Get the cost of the given mapping point on given resource.

    If the point is not feasible on the resource, return inf.
    '''
    #TODO include static energy
    num_levels = resource.buffer_levels()

    access_list, array_cost  = get_access(point, layer, resource)
    layer_size = get_layer_size(layer)
    
    total_access_cost = get_total_access_cost(resource, array_cost)
    assert len(total_access_cost) == len(access_list)
  

    block_costs = [0.0, 0.0, 0.0]
    for i in xrange(len(total_access_cost)):
        buffer_access = [a*b for a,b in zip(access_list[i], layer_size)]
        block_cost = [x * total_access_cost[i] for x in buffer_access]
        print "block_cost ", block_cost
        block_costs = map(add, block_cost, block_costs)

    if verbose:
        print 'access_list: ', access_list
        bank_size_list, block_size_list = get_block_sizes(num_levels, point, layer)
        print 'bank_size_list: ', bank_size_list 
        print 'block_size_list: ', block_size_list
        print 'layer_size: ', layer_size
        print 'block costs: ', block_costs

    return block_costs

def get_cost(resource, point, layer, verbose=False):
    '''
    Get the cost of the given mapping point on given resource.

    If the point is not feasible on the resource, return inf.
    '''
    #TODO include static energy
    #TODO support other access_mode
    num_levels = resource.buffer_levels()
    assert len(point.loop_blockings[0]) == num_levels, \
    "number of blockings does not match with number of memory " \
    "levels: %d" % num_levels 

    access_list, array_cost  = get_access(point, layer, resource)
    layer_size = get_layer_size(layer)

    total_access_cost = get_total_access_cost(resource, array_cost)
    assert len(total_access_cost) == len(access_list)

    total_cost = 0.0
    for i in xrange(len(total_access_cost)):
        ''' List of total access of each buffer at level i'''
        if not isinstance(access_list[i][0], list):
            buffer_access = map(mul, access_list[i], layer_size)
            total_cost += sum(buffer_access) * total_access_cost[i]
        else :
            for j in xrange(len(access_list[i])):
                buffer_access = map(mul, access_list[i][j], layer_size)
                total_cost += sum(buffer_access) * total_access_cost[i][j]   

    if verbose:
        print 'access_cost: ', total_access_cost
        print 'access_list: ', access_list
        bank_size_list, block_size_list = get_block_sizes(num_levels, point, layer)
        print 'bank_size_list: ', bank_size_list 
        print 'block_size_list: ', block_size_list
        print 'layer_size: ', layer_size
        print 'total cost: ', total_cost
   
    return total_cost
