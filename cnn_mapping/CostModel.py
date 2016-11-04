'''
Cost model.
'''
from operator import mul

import LoopEnum as le
import BufferEnum as be

def get_total_block_size(point):
    '''
    Get size of ifmap, ofmap, filter 
    '''

    #TODO problem size
    ox_size = reduce(mul, point.loop_blocking(le.OX)) 
    oy_size = reduce(mul, point.loop_blocking(le.OY)) 
    oc_size = reduce(mul, point.loop_blocking(le.OC)) 
    ic_size = reduce(mul, point.loop_blocking(le.IC)) 
    fx_size = reduce(mul, point.loop_blocking(le.FX)) 
    fy_size = reduce(mul, point.loop_blocking(le.FY)) 

    ox_par = reduce(mul, point.loop_partitioning(le.OX)) 
    oy_par = reduce(mul, point.loop_partitioning(le.OY)) 
    oc_par = reduce(mul, point.loop_partitioning(le.OC)) 
    ic_par = reduce(mul, point.loop_partitioning(le.IC)) 
    fx_par = reduce(mul, point.loop_partitioning(le.FX)) 
    fy_par = reduce(mul, point.loop_partitioning(le.FY)) 


    ifmap_size = ox_size * ox_par * oy_size * oy_par * ic_size * ic_par 
    ofmap_size = ox_size * ox_par * oy_size * oy_par * oc_size * oc_par
    flmap_size = fx_size * fx_par * fy_size * fy_par * ic_size * ic_par * oc_size * oc_par

    return (ifmap_size, ofmap_size, flmap_size)

def get_layer_size(layer):
    ifmap_size = layer.wifm * layer.hifm * layer.nifm
    ofmap_size = layer.wofm * layer.hofm * layer.nofm
    flmap_size = layer.wfil * layer.hfil * layer.nifm * layer.nofm
 
    return (ifmap_size, ofmap_size, flmap_size)

def get_if_access(acc_list, par_list):

    return acc_list[le.FX] * par_list[le.FX] * acc_list[le.FY] * \
    par_list[le.FY] * acc_list[le.OC] * par_list[le.OC]

def get_of_access(acc_list, par_list):

    return acc_list[le.FX] * par_list[le.FX] * acc_list[le.FY] * \
    par_list[le.FY] * acc_list[le.IC] * par_list[le.IC]
   
        

def get_fl_access(acc_list, par_list):

    return acc_list[le.OX] * par_list[le.OX] * acc_list[le.OY] * par_list[le.OY]

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
        acc_list = []
        par_list = []
        for i in xrange(le.NUM):
            acc_list.append(reduce(mul, point.loop_blocking(i)[level+1:], 1))
            par_list.append(reduce(mul, point.loop_partitioning(i)[level+1:], 1))

        if_block_access = get_if_access(acc_list, par_list)
        of_block_access = get_of_access(acc_list, par_list)
        fl_block_access = get_fl_access(acc_list, par_list)
        access_list.append((if_block_access, of_block_access, fl_block_access))

    return access_list


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
    layer_size = get_layer_size(layer)
    
    if verbose:
        print 'access_list: ', access_list
        print 'layer_size: ', layer_size

    total_cost = 0
    for i in xrange(num_levels):
        ''' List of total access of each buffer at level i'''
        buffer_access = map(mul, access_list[i], layer_size) 
        total_cost += sum(buffer_access) * resource.buffer(i).access_cost

    return total_cost
