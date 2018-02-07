import argparse
import cnn_mapping as cm


def basic_optimizer(arch_info, network_info, schedule_info, verbose=False):    

    resource = cm.Resource.arch(arch_info) 
    layer = cm.Layer.layer(network_info)
    opt_result = cm.optimizer.opt_optimizer(resource, layer, schedule_info, verbose)
    
    level_costs = cm.cost_model.get_level_costs(resource, opt_result[1], layer, verbose)
    print "cost for each level", level_costs #TODO
    cm.utils.print_loop_nest(opt_result[1])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("type", choices=["basic", "mem_explore", "2level_reg_explore"], help="optimizer type")
    parser.add_argument("arch", help="architecture specification")
    parser.add_argument("network", help="network specification")
    parser.add_argument("-s", "--schedule", help="restriction of the schedule space")
    parser.add_argument("-v", "--verbose", type=int, help="vebosity")
    args = parser.parse_args()

    arch_info, network_info, schedule_info = cm.extract_input.extract_info(args)    
    if args.type == "basic":
        basic_optimizer(arch_info, network_info, schedule_info, args.verbose)



