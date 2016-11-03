'''
Simple test case for checking get_cost
'''
import unittest
from cnn_mapping.MappingPoint import MappingPoint 
from cnn_mapping.Resource import Resource
from cnn_mapping import CostModel 

class TestCostModel(unittest.TestCase):

    
    def test_blocking_list_length(self):
        capacity_list = [512, 16384, 262144, 2097152]
        access_cost_list = [1, 6, 23, 64]
        static_cost_list = [0.2, 32*0.2, 512*0.2, 4096*0.2] 
        para_count_list = [4, 16]
        para_shared_level_list = [1, 3]

        loop_order_list = []
        loop_blockings_list = [(3, 1, 1, 1,), (3, 1, 1, 1,), (1, 4, 1, 1,), (1, 4, 1, 1,), (1, 1, 32, 1), (1, 1, 1, 4)]
        loop_partitionings_list = [(1, 1, 1, 1), (1, 1, 1, 1), (1, 2, 1, 1,), (1, 2, 1, 1), (1, 1, 1, 1), (1, 1, 1, 16)]

        point = MappingPoint(loop_order_list, loop_blockings_list, loop_partitionings_list)
        resource = Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, para_shared_level_list)
        cost = CostModel.get_cost(resource, point)
        print cost

if __name__ == '__main__':
    unittest.main()
