'''
Simple test case for checking get_cost
'''
import unittest
import cnn_mapping as cm 

class TestOptimizer(unittest.TestCase):
    '''
    def test_simple(self):
        capacity_list = [512, 262144] #[512, 16384, 262144, 2097152]
        access_cost_list = [1, 23] #[1, 6, 23, 64]
        static_cost_list = [0.2, 512*0.2] #[0.2, 32*0.2, 512*0.2, 4096*0.2] 
        para_count_list = [1, 1] #[1, 4, 1, 16]

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list)
        layer = cm.Layer(64, 32, 8, 8, 3, 3, 1)
        result = cm.optimizer.optimizer(resource, layer, False)
        opt_result = cm.optimizer.opt_optimizer(resource, layer, False)
        self.assertEqual(opt_result[0], result[0])
        self.assertEqual(opt_result[1].loop_orders, result[1].loop_orders)
    
    '''

    def test_hint(self):
        capacity_list = [512, 131072]
        access_cost_list = [1, 64]
        static_cost_list = [0.2, 4096*0.2]
        para_count_list = [12, 1]

        # {loop: [level, order, blocking, partitioning]}
        schedule_hint = {cm.le.FX: [[0, 3, 1], None], cm.le.IC: [[1, 8, 1], None],
                         cm.le.FY: [[2, 1, 3], None], cm.le.OY: [[3, 1, 4], None],
                         cm.le.OX: [[4, 1, 1], None], cm.le.OC: [[5, 1, 1], None],
                         cm.le.ON: [[6, 1, 1], None]}

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0], [2])
        layer = cm.Layer(64, 32, 8, 8, 3, 3, 1)
        opt_result = cm.optimizer.opt_optimizer(resource, layer, schedule_hint, True)
        result = cm.optimizer.optimizer(resource, layer, schedule_hint, True)
        self.assertEqual(opt_result[0], result[0])
        self.assertEqual(opt_result[1].loop_orders, result[1].loop_orders)
 
    '''
    def test_hint(self):
        
        capacity_list = [512, 131072, 2097152]
        access_cost_list = [1, 2, 6, 200]
        static_cost_list = [0, 0, 0]
        para_count_list = [12, 1, 1]

        # {loop: [level, order, blocking, partitioning]}
        schedule_hint = {cm.le.FX: [[0, 3, 1], None, None], cm.le.IC: [[1, 8, 1], None, None], 
                         cm.le.FY: [[2, 1, 3], None, None], cm.le.OY: [[3, 1, 4], None, None],
                         cm.le.OX: [[4, 1, 1], None, None], cm.le.OC: [[5, 1, 1], None, None],
                         cm.le.ON: [[6, 1, 1], None, None]}       

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0, 0])
        layer = cm.Layer(64, 32, 8, 8, 3, 3, 1)
        opt_result = cm.optimizer.opt_optimizer(resource, layer, schedule_hint, True)
        result = cm.optimizer.optimizer(resource, layer, schedule_hint, True)
        self.assertEqual(opt_result[0], result[0])
        self.assertEqual(opt_result[1].loop_orders, result[1].loop_orders)
        
   
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
