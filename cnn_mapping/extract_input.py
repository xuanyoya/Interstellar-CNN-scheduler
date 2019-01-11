import json
import os
import loop_enum as le

def extract_arch_info(arch_file):
    with open(arch_file) as json_data_file:
        data = json.load(json_data_file)
    assert data["mem_levels"] == len(data["capacity"]), \
        "capacity list is invalid, too many or too few elements"
    assert data["mem_levels"] == len(data["access_cost"]), \
        "access_cost list is invalid, too many or too few elements"
    assert data["mem_levels"] == len(data["parallel_count"]), \
        "parallel_count list is invalid, too many or too few elements"

    num_bytes = data["precision"]/8
    capacity_list =  [x/num_bytes for x in data["capacity"]]
    data["capacity"] = capacity_list
    if "static_cost" not in data:
        data["static_cost"] = [0,] * data["mem_levels"]
    else:
        assert data["mem_levels"] == len(data["static_cost"]), \
            "static_cost list is invalid, too many or too few elements"

    if "mac_capacity" not in data:
        data["mac_capacity"] = 0
    if "parallel_mode" not in data:
        data["parallel_mode"] = [0,] * data["mem_levels"]
        for level in xrange(data["mem_levels"]):
            if data["parallel_count"][level] != 1:
                data["parallel_mode"][level] = 1
    else:
        assert data["mem_levels"] == len(data["parallel_mode"]), \
            "parallel_mode list is invalid, too many or too few elements"
 
    if "array_dim" not in data:
        data["array_dim"] = None
    if "utilization_threshold" not in data:
        data["utilization_threshold"] = 0.75
    if "replication" not in data:
        data["replication"] = True
   
    return data

def extract_network_info(network_file):
    with open(network_file) as json_data_file:
        data = json.load(json_data_file)

    if "batch_size" not in data:
        data["batch_size"] = 1
    if "stride_width" not in data:
        data["stride_width"] = 1
    if "stride_height" not in data:
        data["stride_height"] = 1
   
    layer_summary = data.values()
    data['layer_info'] = layer_summary
    data['layer_name'] = os.path.splitext(os.path.basename(network_file))[0]

    return data

def extract_schedule_info(schedule_file, num_levels):
    with open(schedule_file) as json_data_file:
        data = json.load(json_data_file)

    schedule = {}
    hint = data["schedule_hint"]
    schedule_hint = {}
    for loop in hint:
        schedule_hint[le.loop_table[loop]] = [None,]*num_levels
        for level in hint[loop]:
            level_index = int(level.lstrip('level'))
            schedule_hint[le.loop_table[loop]][level_index] = [None,]*3
            if  "order" in hint[loop][level]:
                schedule_hint[le.loop_table[loop]][level_index][0] = hint[loop][level]["order"]
            if  "blocking_size" in hint[loop][level]:
                schedule_hint[le.loop_table[loop]][level_index][1] = hint[loop][level]["blocking_size"]
            if  "partitioning_size" in hint[loop][level]:
                schedule_hint[le.loop_table[loop]][level_index][2] = hint[loop][level]["partitioning_size"]

    schedule["schedule_hint"] = schedule_hint

    if "partition_loops" not in data:
        schedule["partition_loops"] = None
    else:
        schedule["partition_loops"] = data["partition_loops"]

    #TODO partition at dimension  
    return schedule


def extract_info(args):
    arch_info = extract_arch_info(args.arch)
    network_info = extract_network_info(args.network)
    schedule_info = extract_schedule_info(args.schedule, arch_info["mem_levels"]) if args.schedule else None
    return arch_info, network_info, schedule_info

