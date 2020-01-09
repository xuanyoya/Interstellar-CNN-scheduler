The format of the schedule.json file is as below:
```
{
    "schedule_hint": {
        "loop_name": {
             "levelx": {
                 "order": "the index of this loop counting from innermost", 
                 "partitioning_size": "unroll factor of this loop"
             }
         }

    },
    "partition_loops": "["loop_name1", "loop_name2", ...] (the loops are allowed to be replicated/unrolled to improve utilization)"

}
```
