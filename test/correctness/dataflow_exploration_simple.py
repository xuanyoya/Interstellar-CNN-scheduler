'''
Simple test case for dataflow exploration
'''

import unittest
import cnn_mapping as cm


class TestDataflow(unittest.TestCase):
   
    def test_parallel_blocking(self):
        '''test non-exact divide case''' 

        capacity_list = [512, 131072, 2097152]
        access_cost_list = [1, 6, 64]
        static_cost_list = [0.2, 32*0.2, 4096*0.2]
        para_count_list = [12, 1, 1]

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0, 0], [2])
        layer = cm.Layer(32, 32, 16, 16, 3, 3, 4)
        loop_blocking = [(3, 1, 1), (3, 1, 1), (1, 16, 1), (4, 4, 1), (8, 2, 2), (2, 4, 8), (4, 1, 1)]

        parallel_generator = cm.mapping_point_generator.parallel_blocking_generator_function(zip(*loop_blocking), resource, layer, under_utilized=True) 
        expected_result = ([1, 1, 1, 1, 1, 2, 4], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1])
        self.assertEqual(next(parallel_generator), expected_result)
        expected_result = ([1, 1, 1, 1, 2, 1, 4], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1])
        self.assertEqual(next(parallel_generator), expected_result)
        expected_result = ([1, 1, 1, 1, 2, 2, 3], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1])
        self.assertEqual(next(parallel_generator), expected_result)


    def test_dataflow_explore(self):
        capacity_list = [32, 131072, 2097152]
        access_cost_list = [0.1, 6, 64]
        static_cost_list = [0.2, 32*0.2, 4096*0.2]
        para_count_list = [12, 1, 1]

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0, 0], [2])
        layer = cm.Layer(32, 32, 16, 16, 3, 3, 4)
   
        dataflow_tb = cm.mapping_point_generator.dataflow_exploration(resource, layer, True)
        print "dataflows:", dataflow_tb

if __name__ == '__main__':
    unittest.main()
