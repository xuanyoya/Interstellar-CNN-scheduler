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
    
    

    def test_hint(self):
        capacity_list = [512, 131072]
        access_cost_list = [1, 64]
        static_cost_list = [0.2, 4096*0.2]
        para_count_list = [12, 1]

        # {loop: [level, order, blocking, partitioning]}
        #schedule_hint = {cm.le.FX: [[0, 3, 1], None], cm.le.IC: [[1, 8, 1], None],
        #                 cm.le.FY: [[2, 1, 3], None], cm.le.OY: [[3, 1, 4], None],
        #                 cm.le.OX: [[4, 1, 1], None], cm.le.OC: [[5, 1, 1], None],
        #                 cm.le.ON: [[6, 1, 1], None]}

        schedule_hint = {cm.le.FX: [[0, 3, 1], None], 
                         cm.le.FY: [[2, 1, 3], None], cm.le.OY: [[3, None, 4], None],
                         cm.le.OX: [[4, 1, 1], None], 
                         cm.le.ON: [[6, 1, 1], None]}

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0], [2])
        layer = cm.Layer(64, 32, 8, 8, 3, 3, 1)
        opt_result = cm.optimizer.opt_optimizer(resource, layer, schedule_hint, True)
        result = cm.optimizer.optimizer(resource, layer, schedule_hint, True)
        self.assertEqual(opt_result[0], result[0])
        self.assertEqual(opt_result[1].loop_orders, result[1].loop_orders)
 
    
    def test_hint1(self):
        
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
    

    def test_alex_conv2(self):
        capacity_list = [512/2, 131072/2, 2097152*256]
        access_cost_list = [1, 6, 200]
        static_cost_list = [0, 0, 0]
        para_count_list = [256, 1, 1]

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0, 0], [2])
        layer = cm.Layer(48, 256, 28, 28, 5, 5, 1)
        opt_result = cm.optimizer.opt_optimizer(resource, layer, None, True)
        level0 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 0)
        level1 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 1)
        level2 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 2)
        level00 = cm.cost_model.get_array_and_curr_level_cost(resource, opt_result[1], layer, 1) - level1
        print level0, level00, level1, level2
        cm.utils.print_loop_nest(opt_result[1])
   
    '''
    def test_alex_conv3(self):
        capacity_list = [512/2, 131072/2, 2097152*256]
        access_cost_list = [1, 6, 200]
        static_cost_list = [0, 0, 0]
        para_count_list = [256, 1, 1]

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0, 0], [2])
        layer = cm.Layer(256, 384, 13, 13, 3, 3, 1)
        opt_result = cm.optimizer.opt_optimizer(resource, layer, None, True)
        level0 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 0)
        level1 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 1)
        level2 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 2)
        level00 = cm.cost_model.get_array_and_curr_level_cost(resource, opt_result[1], layer, 1) - level1
        print level0, level00, level1, level2
        cm.utils.print_loop_nest(opt_result[1])
    

if __name__ == '__main__':
    unittest.main()
