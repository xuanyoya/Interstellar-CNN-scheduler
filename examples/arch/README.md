The format of the arch.json file to perform blocking search is as below:
```
{
    "mem_levels": "number of memory levels",
    "capacity": "[1st level buffer size, 2nd level buffer size, ...]",
    "access_cost": "[1st level per access cost, 2nd level per access cost, ...]",
    "parallel_count": "[1st level parallel factor, 2nd level parallel factor, ...]",
    "parallel_cost": "communication cost among adjacent parallel units (PEs)",
    "precision": "number of bits",
    "utilization_threshold": "only consider the designs that achieve utilization ratio larger than this threshold, default 0.75",
    "replication": "whether allow replication, default true"  
}
```

To perform memory search, the format is as below

```
{
    "mem_levels": "number of memory levels",
    "capacity": "[1st level buffer size, 2nd level buffer size, ...]",
    "access_cost": "[1st level per access cost, 2nd level per access cost, ...]",
    "parallel_count": "[1st level parallel factor, 2nd level parallel factor, ...]",
    "parallel_cost": "communication cost among adjacent parallel units (PEs)",
    "precision": "number of bits",
    "utilization_threshold": "only consider the designs that achieve utilization ratio larger than this threshold, default 0.75",
    "replication": "whether allow replication, default true" , 
    "capacity_scale":[cs1, cs2],
    "access_cost_scale":[2, 1.5],
    "explore_points":[count1, count2]
}
```

With adding the last three fields("capacity_scale", "access_cost_scale", "explore_points"), the optimizer will explore all the memory systems with the register file size in the range [1st level buffer size, 1st level buffer size * cs1^count1], and the buffer size in the range [2nd level buffer size, 2nd level buffer size * cs2^count2]. 
