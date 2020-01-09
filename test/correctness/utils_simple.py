'''
Simple test case for checking utils
'''
import unittest
import cnn_mapping as cm

class TestCostModel(unittest.TestCase):


    def test_simple(self):
        loop_order_list = [(0, 2, 1, 1), (1, 3, 2, 2), (2, 0, 3, 3), (3, 1, 4, 4), (4, 4, 0, 5), (5, 5, 5, 0), (6, 6, 6, 6)]
        loop_blockings_list = [(3, 1, 1, 1), (3, 1, 1, 1), (1, 4, 1, 1), (1, 4, 1, 1), (1, 1, 32, 1), (1, 1, 1, 4), (1, 1, 1, 1)]
        loop_partitionings_list = [(1, 1, 1, 1), (1, 1, 1, 1), (1, 2, 1, 1,), (1, 2, 1, 1), (1, 1, 1, 1), (1, 1, 1, 16), (1, 1, 1, 1)]
        point = cm.MappingPoint(loop_order_list, loop_blockings_list, loop_partitionings_list)   

        cm.utils.print_loop_nest(point)

if __name__ == '__main__':
    unittest.main()
