import json
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
    assert data["mem_levels"] == len(data["static_cost"]), \
        "static_cost list is invalid, too many or too few elements"
    assert data["mem_levels"] == len(data["parallel_mode"]), \
        "parallel_mode list is invalid, too many or too few elements"

    num_bytes = data["precision"]/8
    capacity_list =  [x/num_bytes for x in data["capacity"]]
    data["capacity"] = capacity_list
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

    return data

def extract_schedule_info(schedule_file, num_levels):
    with open(schedule_file) as json_data_file:
        data = json.load(json_data_file)

    schedule_hint = {}
    for loop in data:
        schedule_hint[le.loop_table[loop]] = [None,]*num_levels
        for level in data[loop]:
            level_index = int(level.lstrip('level'))
            schedule_hint[le.loop_table[loop]][level_index] = [None,]*3
            if  "order" in data[loop][level]:
                schedule_hint[le.loop_table[loop]][level_index][0] = data[loop][level]["order"]
            if  "blocking_size" in data[loop][level]:
                schedule_hint[le.loop_table[loop]][level_index][1] = data[loop][level]["blocking_size"]
            if  "partitioning_size" in data[loop][level]:
                schedule_hint[le.loop_table[loop]][level_index][2] = data[loop][level]["partitioning_size"]
  
    return schedule_hint


def extract_info(args):
    arch_info = extract_arch_info(args.arch)
    network_info = extract_network_info(args.network)
    schedule_info = extract_schedule_info(args.schedule, arch_info["mem_levels"]) if args.schedule else None
    return arch_info, network_info, schedule_info

