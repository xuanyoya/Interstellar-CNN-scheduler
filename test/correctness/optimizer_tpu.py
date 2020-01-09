'''
Simple test case for checking get_cost
'''
import unittest
import cnn_mapping as cm 

class TestOptimizer(unittest.TestCase):

    '''       
    def test_simple(self):
        capacity_list = [512/2, 131072/2, 2097152/2] 
        access_cost_list = [1, 6, 200] 
        static_cost_list = [0, 0, 0]  
        para_count_list = [256, 1, 1] 

        # {loop: [[order, blocking, partitioning],[],...]}
        schedule_hint = {cm.le.FX: [[0, 3, 1], None, None], cm.le.IC: [[1, 32, 1], None, None],
                         cm.le.FY: [[2, 1, 3], None, None], cm.le.OY: [[3, 1, 16], None, None],
                         cm.le.OX: [[5, 1, 1], None, None], cm.le.OC: [[4, 1, 5], None, None],
                         cm.le.ON: [[6, 1, 1], None, None]}

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0, 0], [2])
        layer = cm.Layer(32, 65, 16, 16, 3, 3, 1)
        opt_result = cm.optimizer.opt_optimizer(resource, layer, schedule_hint, True)
        level0 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 0)
        level1 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 1)
        level2 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 2)
        level00 = cm.cost_model.get_array_and_curr_level_cost(resource, opt_result[1], layer, 1) - level1
        print level0, level00, level1, level2
                    
    def test_alex_conv2(self):
        capacity_list = [512/2, 131072/2, 2097152*256] 
        access_cost_list = [1, 6, 200] 
        static_cost_list = [0, 0, 0]  
        para_count_list = [192, 1, 1] 

        # {loop: [[order, blocking, partitioning],[],...]}
        #schedule_hint = {cm.le.FX: [[0, 5, 1], None, None], cm.le.IC: [[3, 1, 12], None, None],
        #                 cm.le.FY: [[1, 5, 1], None, None], cm.le.OY: [[5, 1, 1], None, None],
        #                 cm.le.OX: [[4, 1, 1], None, None], cm.le.OC: [[4, 1, 16], None, None],
        #                 cm.le.ON: [[6, 1, 1], None, None]}

        schedule_hint = {cm.le.IC: [[3, None, 12], None, None],
                         cm.le.OC: [[4, None, 16], None, None]}

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0, 0], [2])
        layer = cm.Layer(48, 256, 28, 28, 5, 5, 1)
        opt_result = cm.optimizer.opt_optimizer(resource, layer, schedule_hint, True)
        level0 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 0)
        level1 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 1)
        level2 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 2)
        level00 = cm.cost_model.get_array_and_curr_level_cost(resource, opt_result[1], layer, 1) - level1
        print level0, level00, level1, level2
        cm.utils.print_loop_nest(opt_result[1])

     
    def test_alex_conv3(self):
        capacity_list = [512/2, 131072/2, 2097152*256] 
        access_cost_list = [1, 6, 200] 
        static_cost_list = [0, 0, 0]  
        para_count_list = [256, 1, 1] 

        # {loop: [[order, blocking, partitioning],[],...]}
        schedule_hint = {cm.le.IC: [[3, None, 16], None, None],
                         cm.le.OC: [[4, None, 16], None, None]}

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0, 0], [2])
        layer = cm.Layer(256, 384, 13, 13, 3, 3, 1)
        opt_result = cm.optimizer.opt_optimizer(resource, layer, schedule_hint, True)
        level0 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 0)
        level1 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 1)
        level2 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 2)
        level00 = cm.cost_model.get_array_and_curr_level_cost(resource, opt_result[1], layer, 1) - level1
        print level0, level00, level1, level2
        cm.utils.print_loop_nest(opt_result[1]) 
    
     
    def test_vgg_conv2(self):
        capacity_list = [512/2, 131072/2, 2097152*1024] 
        access_cost_list = [1, 6, 200] 
        static_cost_list = [0, 0, 0]  
        para_count_list = [256, 1, 1] 

        # {loop: [[order, blocking, partitioning],[],...]}
        schedule_hint = {cm.le.IC: [[3, None, 16], None, None],
                         cm.le.OC: [[4, None, 16], None, None]}

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0, 0], [2])
        layer = cm.Layer(64, 64, 224, 224, 3, 3, 1)
        opt_result = cm.optimizer.opt_optimizer(resource, layer, schedule_hint, True)
        level0 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 0)
        level1 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 1)
        level2 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 2)
        level00 = cm.cost_model.get_array_and_curr_level_cost(resource, opt_result[1], layer, 1) - level1
        print level0, level00, level1, level2
        cm.utils.print_loop_nest(opt_result[1]) 
    '''
    def test_vgg_conv12(self):
        capacity_list = [512/2, 131072/2, 2097152*1024]
        access_cost_list = [1, 6, 200]
        static_cost_list = [0, 0, 0]
        para_count_list = [256, 1, 1]

        # {loop: [[order, blocking, partitioning],[],...]}
        schedule_hint = {cm.le.IC: [[3, None, 16], None, None],
                         cm.le.OC: [[4, None, 16], None, None]}

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0, 0], [2])
        layer = cm.Layer(512, 512, 14, 14, 3, 3, 1)
        opt_result = cm.optimizer.opt_optimizer(resource, layer, schedule_hint, True)
        level0 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 0)
        level1 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 1)
        level2 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 2)
        level00 = cm.cost_model.get_array_and_curr_level_cost(resource, opt_result[1], layer, 1) - level1
        print level0, level00, level1, level2
        cm.utils.print_loop_nest(opt_result[1])
    ''' 
    def test_alex_fc2(self):
        capacity_list = [512/2, 131072/2, 2097152*1024]
        access_cost_list = [1, 6, 200]
        static_cost_list = [0, 0, 0]
        para_count_list = [256, 1, 1]

        # {loop: [[order, blocking, partitioning],[],...]}
        schedule_hint = {cm.le.IC: [[3, None, 16], None, None],
                         cm.le.OC: [[4, None, 16], None, None]}

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0, 0], [2])
        layer = cm.Layer(4096, 4096, 1, 1, 1, 1, 16)
        opt_result = cm.optimizer.opt_optimizer(resource, layer, schedule_hint, True)
        level0 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 0)
        level1 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 1)
        level2 = cm.cost_model.get_level_cost(resource, opt_result[1], layer, 2)
        level00 = cm.cost_model.get_array_and_curr_level_cost(resource, opt_result[1], layer, 1) - level1
        print level0, level00, level1, level2
        cm.utils.print_loop_nest(opt_result[1])
    '''

if __name__ == '__main__':
    unittest.main()
