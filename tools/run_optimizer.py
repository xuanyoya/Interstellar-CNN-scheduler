import numpy as np
import argparse
import math
import cnn_mapping as cm

def basic_optimizer(arch_info, network_info, schedule_info, basic=False, verbose=False):    

    resource = cm.Resource.arch(arch_info) 
    layer = cm.Layer.layer(network_info)
    opt_result = cm.optimizer.opt_optimizer(resource, layer, schedule_info, verbose)
    
    level_costs = cm.cost_model.get_level_costs(resource, opt_result[1], layer, verbose)
    if verbose or basic:
        print "best energy: ", opt_result[0]
        print "cost for each level: ", level_costs #TODO
        print "best schedule: ", cm.utils.print_loop_nest(opt_result[1])
    return opt_result[0]


def mem_explore_optimizer(arch_info, network_info, schedule_info, verbose=False):
   
    assert "explore_points" in arch_info, "missing explore_points in arch file" 
    assert "capacity_scale" in arch_info, "missing capacity_scale in arch file" 
    assert "access_cost_scale" in arch_info, "missing access_cost_scale in arch file" 

    explore_points = arch_info["explore_points"]
    energy_list = np.zeros(tuple(explore_points))
    #TODO support more than two levels of explorations
    capacity0 = arch_info["capacity"][0]
    capacity1 = arch_info["capacity"][1]
    cost0 = arch_info["access_cost"][0]
    cost1 = arch_info["access_cost"][1]
    for x in xrange(explore_points[0]):
        arch_info["capacity"][0] = capacity0 * (arch_info["capacity_scale"][0]**x)
        arch_info["access_cost"][0] = cost0 * (arch_info["access_cost_scale"][0]**x)
        for y in xrange(explore_points[1]):
            arch_info["capacity"][1] = capacity1 * (arch_info["capacity_scale"][1]**y)
            arch_info["access_cost"][1] = cost1 * (arch_info["access_cost_scale"][1]**y)
            print arch_info
            energy = basic_optimizer(arch_info, network_info, schedule_info, False, verbose)
            energy_list[x][y] = energy

    print list(energy_list)


def mem_explore_optimizer(arch_info, network_info, schedule_info, verbose=False):
    
    dataflow_res = []
    #TODO check the case when parallel count larger than layer dimension size
    dataflow_generator = dataflow_generator_function(arch_info)

    for dataflow in dataflow_generator:
        energy = basic_optimizer(arch_info, network_info, schedule_info, False, verbose)            
        dataflow_res.append[energy]
        
    if verbose:
        print "optimal energy for all dataflows: ", dataflow_res

    return dataflow_res


def dataflow_explore_optimizer(arch_info, network_info, verbose=False):

    assert arch_info["parallel_count"] > 1, \
        "parallel count has to be more than 1 for dataflow exploration"

    resource = cm.Resource.arch(arch_info) 
    layer = cm.Layer.layer(network_info)
    dataflow_tb = cm.mapping_point_generator.dataflow_exploration(resource, layer, verbose)
    
    if verbose:
        print "dataflow table: ", dataflow_tb


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("type", choices=["basic", "mem_explore", "dataflow_explore"], help="optimizer type")
    parser.add_argument("arch", help="architecture specification")
    parser.add_argument("network", help="network specification")
    parser.add_argument("-s", "--schedule", help="restriction of the schedule space")
    parser.add_argument("-v", "--verbose", action='count', help="vebosity")
    args = parser.parse_args()

    arch_info, network_info, schedule_info = cm.extract_input.extract_info(args)    
    if args.type == "basic":
        basic_optimizer(arch_info, network_info, schedule_info, True, args.verbose)
    elif args.type == "mem_explore":
        mem_explore_optimizer(arch_info, network_info, schedule_info, args.verbose)
    elif args.type == "dataflow_explore":
        dataflow_explore_optimizer(arch_info, network_info, args.verbose)


