The format of the arch.json file is as below:
```
{
    "mem_levels": "number of memory levels",
    "capacity": "[1st level buffer size, 2nd level buffer size, ...]",
    "access_cost": "[1st level per access cost, 2nd level per access cost, ...]",
    "static_cost": "[1st level static cost, 2nd level static cost, ...]",
    "parallel_count": "[1st level parallel factor, 2nd level parallel factor, ...]",
    "mac_capacity": "How many elements can be buffered by MAC",
    "parallel_mode": "[1st level parallel mode, 2nd level parallel mode]",
    "parallel_cost": "communication cost among adjacent parallel units (PEs)",
    "precision": "number of bits"
    "utilization_threshould": "only consider the designs that achieve utilization ratio larger than this threshould",
    "replication": "whether allow replication"  
}
```
