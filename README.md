# CNN-blocking
Tool for optimize CNN blocking

usage: run_optimizer.py [-h] [-s SCHEDULE] [-v]
                        {basic,mem_explore, dataflow_explore} arch network

positional arguments:
  
  {basic,mem_explore, dataflow_explore}   optimizer type

  arch                  architecture specification

  network               network specification

optional arguments:

  -h, --help            show this help message and exit

  -s SCHEDULE, --schedule SCHEDULE restriction of the schedule space
  this is optional but restricting the schedule space will accelerate the scipt significantly

  -v, --verbose         vebosity


# Examples
## To optimize loop blocking.
Dataflow: Eyeriss

Memory Architecture: 3 level

Network: AlexNet Conv2 Batch16

```
python ./tools/run_optimizer.py -v -s ./examples/schedule/eyeriss_alex_conv2.json basic ./examples/arch/3_level_mem_baseline_asic.json ./examples/network/alex_conv2_batch16.json 
```

Dataflow: TPU

Memory Architecture: 3 level

Network: AlexNet Conv2 Batch16

```
python ./tools/run_optimizer.py -v -s ./examples/schedule/tpu.json basic ./examples/arch/3_level_mem_baseline_asic.json ./examples/network/alex_conv2_batch16.json
```

## To optimize memory capacity.
Dataflow: Eyeriss

Memory Architecture: 3 level

Network: AlexNet Conv2 Batch16

```
python ./tools/run_optimizer.py -v -s ./examples/schedule/eyeriss_alex_conv2.json mem_explore ./examples/arch/3_level_mem_explore.json ./examples/network/alex_conv2_batch16.json
```

## To explore dataflow.
Dataflow: All

Memory Architecture: Eyeriss

Network: AlexNet Conv2 Batch16

```
python ./tools/run_optimizer.py -v dataflow_explore ./examples/arch/3_level_mem_baseline_asic.json ./examples/network/alex_conv2_batch16.json
```

or:

```
python ./tools/run_optimizer.py -v -n user_defined_pickle_filename dataflow_explore ./examples/arch/3_level_mem_baseline_asic.json ./examples/network/alex_conv3_batch16.json
```
