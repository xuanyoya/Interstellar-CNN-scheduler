# CNN-blocking
Tool for optimize CNN blocking

usage: run_optimizer.py [-h] [-s SCHEDULE] [-v]
                        {basic,mem_explore} arch network

positional arguments:
  {basic,mem_explore}   optimizer type
  arch                  architecture specification
  network               network specification

optional arguments:
  -h, --help            show this help message and exit
  -s SCHEDULE, --schedule SCHEDULE
                        restriction of the schedule space
  -v, --verbose         vebosity
