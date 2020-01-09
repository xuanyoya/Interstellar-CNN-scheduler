'''
Simple test case for checking get_cost
'''
import unittest
import cnn_mapping as cm 

class TestCostModel(unittest.TestCase):


    def test_simple(self):
        capacity_list = [512, 131072]
        access_cost_list = [1, 64]
        static_cost_list = [0.2, 4096*0.2] 
        para_count_list = [16, 1]

        loop_order_list = [(0, 6), (2, 6), (6, 0), (3, 1), (6, 3), (1, 2), (6, 4)]
        loop_blockings_list = [(3, 1), (1, 1), (1, 8), (1, 2), (1, 32), (8, 8), (1, 1)]
        loop_partitionings_list = [(1, 1), (3, 1), (1, 1), (4, 1), (1, 1), (1, 1), (1, 1)]
        para_dim_list = [[[1], [3]], None]

        point = cm.MappingPoint(loop_order_list, loop_blockings_list, loop_partitionings_list, para_dim_list)
        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0], [2])
        layer = cm.Layer(64, 32, 8, 8, 3, 3, 1)
        cm.utils.print_loop_nest(point)
        cost = cm.cost_model.get_cost(resource, point, layer, True)
        real_cost = (6400*288 + 2048*1151 + 18432*64) + (6400*96 + 2048*24 + 18432*4)*2 + (6400*32 + 2048*15 + 18432*1)*64
        self.assertEqual(cost, real_cost)

    '''
    def test_block_cost(self):
        capacity_list = [512, 131072]
        access_cost_list = [1, 64]
        static_cost_list = [0.2, 4096*0.2] 
        para_count_list = [12, 1]

        loop_order_list = [(0, 6), (2, 6), (6, 0), (3, 1), (6, 3), (1, 2), (6, 4)]
        loop_blockings_list = [(3, 1), (1, 1), (1, 8), (1, 2), (1, 32), (8, 8), (1, 1)]
        loop_partitionings_list = [(1, 1), (3, 1), (1, 1), (4, 1), (1, 1), (1, 1), (1, 1)]
        para_dim_list = [[[1], [3]], None]

        point = cm.MappingPoint(loop_order_list, loop_blockings_list, loop_partitionings_list, para_dim_list)
        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0], [2])
        layer = cm.Layer(64, 32, 8, 8, 3, 3, 1)
        cm.utils.print_loop_nest(point)
        cost_total = cm.cost_model.get_cost(resource, point, layer, True)
        cost_blocks = cm.cost_model.get_block_cost(resource, point, layer, True)
        self.assertEqual(cost_total, sum(cost_blocks))
    '''

    def test_2d_in_1d(self):
        capacity_list = [512, 131072]
        access_cost_list = [1, 64]
        static_cost_list = [0.2, 4096*0.2] 
        para_count_list = [16, 1]

        loop_order_list = [(0, 6), (2, 6), (6, 0), (3, 1), (6, 3), (1, 2), (6, 4)]
        loop_blockings_list = [(3, 1), (1, 1), (1, 8), (1, 2), (1, 32), (8, 8), (1, 1)]
        loop_partitionings_list = [(1, 1), (3, 1), (1, 1), (4, 1), (1, 1), (1, 1), (1, 1)]
        para_dim_list = [[[1,3]], None]

        point = cm.MappingPoint(loop_order_list, loop_blockings_list, loop_partitionings_list, para_dim_list)
        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0], [2], array_dim=[1, 0, 0])
        layer = cm.Layer(64, 32, 8, 8, 3, 3, 1)
        cm.utils.print_loop_nest(point)
        cost = cm.cost_model.get_cost(resource, point, layer, True)
        real_cost = (6400*288 + 2048*1151 + 18432*64) + (6400*96 + 2048*24 + 18432*1)*2 + (4*18432)*6 + (6400*32 + 2048*15 + 18432*1)*64
        self.assertEqual(cost, real_cost)
        cost_levels = cm.cost_model.get_level_cost(resource, point, layer, 0, True) + \
               cm.cost_model.get_array_and_curr_level_cost(resource, point, layer, 1, True)
        self.assertEqual(cost, cost_levels)
        

    def test_3d_in_2d(self):
        capacity_list = [512, 131072]
        access_cost_list = [1, 64]
        static_cost_list = [0.2, 4096*0.2] 
        para_count_list = [16, 1]

        loop_order_list = [(0, 6), (2, 6), (6, 0), (3, 1), (6, 3), (1, 2), (6, 4)]
        loop_blockings_list = [(3, 1), (1, 1), (1, 8), (1, 2), (1, 32), (1, 8), (1, 1)]
        loop_partitionings_list = [(1, 1), (3, 1), (1, 1), (4, 1), (1, 1), (16, 1), (1, 1)]
        para_dim_list = [[[1, 3], [5]], None]

        point = cm.MappingPoint(loop_order_list, loop_blockings_list, loop_partitionings_list, para_dim_list)
        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0], [2])
        layer = cm.Layer(128, 32, 8, 8, 3, 3, 1)
        cm.utils.print_loop_nest(point)
        cost = cm.cost_model.get_cost(resource, point, layer, True)
        real_cost = (12800*288 + 2048*2303 + 36864*64) + (12800*96 + 2048*384 + 36864*1)*2 + (36864*4)*6 + (12800*32 + 2048*15 + 36864*1)*64
        self.assertEqual(cost, real_cost)
        cost_levels = cm.cost_model.get_level_cost(resource, point, layer, 0, True) + \
               cm.cost_model.get_array_and_curr_level_cost(resource, point, layer, 1, True)
        self.assertEqual(cost, cost_levels)
     

    def test_4d_in_2d(self):    
        capacity_list = [512, 131072]
        access_cost_list = [1, 64]
        static_cost_list = [0.2, 4096*0.2] 
        para_count_list = [16, 1]

        loop_order_list = [(0, 6), (2, 6), (6, 0), (3, 1), (6, 3), (1, 2), (4, 4)]
        loop_blockings_list = [(3, 1), (1, 1), (1, 8), (1, 2), (1, 32), (2, 8), (1, 1)]
        loop_partitionings_list = [(1, 1), (3, 1), (1, 1), (4, 1), (1, 1), (4, 1), (4, 1)]
        para_dim_list = [[[1, 3], [5, 6]], None]

        point = cm.MappingPoint(loop_order_list, loop_blockings_list, loop_partitionings_list, para_dim_list)
        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0], [2])
        layer = cm.Layer(64, 32, 8, 8, 3, 3, 4)
        cm.utils.print_loop_nest(point)
        cost = cm.cost_model.get_cost(resource, point, layer, True)
        real_cost = (25600*288 + 8192*1151 + 18432*256) + (25600*96 + 8192*96+ 18432*1)*2 + (18432*4)*6 + (18432*4)*8 + (25600*32 + 8192*15 + 18432*1)*64
        #self.assertEqual(cost, real_cost)
        cost_levels = cm.cost_model.get_level_cost(resource, point, layer, 0, True) + \
               cm.cost_model.get_array_and_curr_level_cost(resource, point, layer, 1, True)
        self.assertEqual(cost, cost_levels)
 

    def test_level_cost(self):
        capacity_list = [512, 131072]
        access_cost_list = [1, 64]
        static_cost_list = [0.2, 4096*0.2] 
        para_count_list = [12, 1]
        para_dim_list = [[[1], [3]], None]

        loop_order_list = [(0, 6), (2, 6), (6, 0), (3, 1), (6, 3), (1, 2), (6, 4)]
        loop_blockings_list = [(3, 1), (1, 1), (1, 8), (1, 2), (1, 32), (8, 8), (1, 1)]
        loop_partitionings_list = [(1, 1), (3, 1), (1, 1), (4, 1), (1, 1), (1, 1), (1, 1)]

        point = cm.MappingPoint(loop_order_list, loop_blockings_list, loop_partitionings_list, para_dim_list)
        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0], [2])
        layer = cm.Layer(64, 32, 8, 8, 3, 3, 1)
        cm.utils.print_loop_nest(point)
        cost_total = cm.cost_model.get_cost(resource, point, layer, True)
        cost_levels = cm.cost_model.get_level_cost(resource, point, layer, 0, True) + \
               cm.cost_model.get_array_and_curr_level_cost(resource, point, layer, 1, True)
        self.assertEqual(cost_total, cost_levels)

'''
    def test_parallelism(self):   
        capacity_list = [512, 4096, 16384]
        access_cost_list = [1, 6, 23]
        static_cost_list = [0.2, 32*0.2, 512*0.2] 
        para_count_list = [1, 4, 16]

        loop_order_list = [(0, 2, 2), (1, 3, 3), (2, 0, 4), (3, 1, 5), (4, 4, 0), (5, 5, 1), (6, 6, 6)]
        loop_blockings_list = [(3, 1, 1), (3, 1, 1), (1, 4, 1), (1, 4, 1), (1, 1, 8), (1, 1, 16), (1, 1, 1)]
        loop_partitionings_list = [(1, 1, 1), (1, 1, 1), (1, 2, 1), (1, 2, 1), (1, 1, 4), (1, 1, 4), (1, 1, 1)]

        point = cm.MappingPoint(loop_order_list, loop_blockings_list, loop_partitionings_list)
        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list)
        layer = cm.Layer(64, 32, 8, 8, 3, 3, 1)
        cost = cm.cost_model.get_cost(resource, point, layer, True)
        real_cost = (6400*32 + 2048*64*2 + 18432*64) + (6400*32 + 2048*64*2 + 18432*1)*6 + (6400 + 2048*64*2 + 18432)*23
        self.assertEqual(cost, real_cost)

'''
     
    
if __name__ == '__main__':
    unittest.main()
