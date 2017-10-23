'''
Simple test case for checking get_cost
'''
import unittest
import cnn_mapping as cm 

class TestOptimizer(unittest.TestCase):

           
    def test_simple(self):
        capacity_list = [512, 262144] #[512, 16384, 262144, 2097152]
        access_cost_list = [1, 23] #[1, 6, 23, 64]
        static_cost_list = [0.2, 512*0.2] #[0.2, 32*0.2, 512*0.2, 4096*0.2] 
        para_count_list = [1, 1] #[1, 4, 1, 16]

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list)
        layer = cm.Layer(64, 32, 8, 8, 3, 3, 1)
        cm.optimizer.optimizer(resource, layer, True)
    
    '''
    def test_four_levels(self):
        capacity_list = [512, 16384, 262144] #, 2097152]
        access_cost_list = [1, 6, 23] #, 64]
        static_cost_list = [0.2, 32*0.2, 512*0.2] #, 4096*0.2] 
        para_count_list = [1, 1, 1] #, 1] #[1, 4, 1, 16]

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list)
        layer = cm.Layer(16, 32, 8, 8, 3, 3, 1)
        cm.optimizer.optimizer(resource, layer, True)
    '''

if __name__ == '__main__':
    unittest.main()
