# CNN-blocking
Tool for optimize CNN blocking

usage: run_optimizer.py [-h] [-s SCHEDULE] [-v]
                        {basic,mem_explore, dataflow_explore} arch network

positional arguments:
  
  {basic,mem_explore, dataflow_explore}   optimizer type

  arch                  architecture specification

  layer                 layer specification

optional arguments:

  -h, --help            show this help message and exit

  -s SCHEDULE, --schedule SCHEDULE restriction of the schedule space
  this is optional but restricting the schedule space will accelerate the scipt significantly

  -v, --verbose         vebosity


# Examples
## To optimize loop blocking.
Dataflow: C | K

Memory Architecture: 3 level

Network: AlexNet Conv3 Batch16

```
python ./tools/run_optimizer.py basic ./examples/arch/3_level_mem_basic_example.json ./examples/layer/alex_conv3_batch16.json -s ./examples/schedule/dataflow_C_K.json -v 
```

## To optimize memory capacity.
Dataflow: C | K

Memory Architecture: 3 level

Network: AlexNet Conv3 Batch16

```
python ./tools/run_optimizer.py mem_explore ./examples/arch/3_level_mem_explore_example.json ./examples/layer/alex_conv3_batch16.json -s ./examples/schedule/eyeriss_alex_conv3.json -v 
```

## To explore dataflow.
Dataflow: All

Memory Architecture: Eyeriss

Network: AlexNet Conv3 Batch16

```
python ./tools/run_optimizer.py dataflow_explore ./examples/arch/3_level_mem_basic_example.json ./examples/layer/alex_conv3_batch16.json -v
```

or:

```
python ./tools/run_optimizer.py dataflow_explore ./examples/arch/3_level_mem_basic_example.json ./examples/layer/alex_conv3_batch16.json -n user_defined_pickle_filename -v
```
