'''
Cost model.
'''
from operator import mul

import LoopEnum as le
import BufferEnum as be

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


def get_if_size(acc_list, par_list, layer):
    '''
    Get size of if block at current level
    '''
 
    fx_acc = acc_list[le.FX] * par_list[le.FX] 
    fy_acc = acc_list[le.FY] * par_list[le.FY] 
    ox_acc = acc_list[le.OX] * par_list[le.OX]
    oy_acc = acc_list[le.OY] * par_list[le.OY]
    width = fx_acc + (ox_acc - 1) * layer.wstd
    height = fy_acc + (oy_acc - 1) * layer.hstd

    return width * height * acc_list[le.IC] * par_list[le.IC] * \
    acc_list[le.ON] * par_list[le.ON]

def get_of_size(acc_list, par_list):
    '''
    Get size of of block at current level
    '''
 
    return acc_list[le.OX] * par_list[le.OX] * acc_list[le.OY] * \
    par_list[le.OY] * acc_list[le.OC] * par_list[le.OC] * \
    acc_list[le.ON] * par_list[le.ON]
   
        
def get_fl_size(acc_list, par_list):
    '''
    Get size of fl block at current level
    '''
 
    return acc_list[le.FX] * par_list[le.FX] * acc_list[le.FY] * \
    par_list[le.FY] * acc_list[le.IC] * par_list[le.IC] * \
    acc_list[le.OC] * par_list[le.OC]


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
    '''
    fx_acc = reduce(mul, point.loop_blocking(le.FX)[level+1:], 1) # exlusive
    fy_acc = reduce(mul, point.loop_blocking(le.FY)[level+1:], 1) # exlusive
    ox_acc = reduce(mul, point.loop_blocking(le.OX)[level+1:], 1) #exclusive
    oy_acc = reduce(mul, point.loop_blocking(le.OY)[level+1:], 1) #exclusive
    oc_acc = reduce(mul, point.loop_blocking(le.OC)[level+1:], 1) #exclusive
    ic_acc = reduce(mul, point.loop_blocking(le.IC)[level+1:], 1) #exclusive



    fx_par = reduce(mul, point.loop_partitioning(le.FX)[level+1:], 1) 
    fy_par = reduce(mul, point.loop_partitioning(le.FY)[level+1:], 1) 
    ox_par = reduce(mul, point.loop_partitioning(le.OX)[level+1:], 1) 
    oy_par = reduce(mul, point.loop_partitioning(le.OY)[level+1:], 1) 
    oc_par = reduce(mul, point.loop_partitioning(le.OC)[level+1:], 1) 
    ic_par = reduce(mul, point.loop_partitioning(le.IC)[level+1:], 1) 
    '''
    
    access_list = []
    for level in xrange(num_levels):
        if_block_access = get_if_access(level, point)
        of_block_access = get_of_access(level, point)
        fl_block_access = get_fl_access(level, point)
        access_list.append((if_block_access, of_block_access, fl_block_access))

    return access_list


def get_block_size(num_levels, point, layer):
    '''
    Get size of ifmap, ofmap, filter 
    '''
    block_list = []
    for level in xrange(num_levels):
        acc_list = []
        par_list = []
        for i in xrange(le.NUM):
            acc_list.append(reduce(mul, point.loop_blocking(i)[:level+1], 1))
            par_list.append(reduce(mul, point.loop_partitioning(i)[:level+1], 1))

        if_block_size = get_if_size(acc_list, par_list, layer)
        of_block_size = get_of_size(acc_list, par_list)
        fl_block_size = get_fl_size(acc_list, par_list)
        block_list.append((if_block_size, of_block_size, fl_block_size))

    return block_list


def fit_in_level(cap, blocks):
    return sum(blocks) <= cap



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
    block_size_list = get_block_size(num_levels, point, layer)
    layer_size = get_layer_size(layer)
    
    if verbose:
        print 'access_list: ', access_list
        print 'block_size_list: ', block_size_list
        print 'layer_size: ', layer_size

    total_cost = 0.0
    for i in xrange(num_levels):
        ''' List of total access of each buffer at level i'''
        if not fit_in_level(resource.buffer(i).capacity, block_size_list[i]):
           return float("inf")
        buffer_access = map(mul, access_list[i], layer_size) 
        total_cost += sum(buffer_access) * resource.buffer(i).access_cost

    return total_cost
