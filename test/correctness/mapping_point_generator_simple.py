'''
Simple test case for checking mapping_point_generator
'''
import unittest
import cnn_mapping as cm 

class TestCostModel(unittest.TestCase):

            
    def test_simple(self):
        order_generator = cm.mapping_point_generator.order_generator_function(3, 2)
        self.assertEqual(next(order_generator), [(0,0), (1,1), (2,2)])
        self.assertEqual(next(order_generator), [(0,0), (1,2), (2,1)])
        self.assertEqual(next(order_generator), [(0,1), (1,0), (2,2)])
        self.assertEqual(next(order_generator), [(0,1), (1,2), (2,0)])

    def test_tile(self):
        result_permutations = cm.mapping_point_generator.loop_tile(6, 3)    
        self.assertEqual(len(result_permutations), 9)
        result_permutations = cm.mapping_point_generator.loop_tile(12, 3)    
        self.assertEqual(len(result_permutations), 18)

    def test_tile_generator(self):    
        capacity_list = [512, 16384, 262144, 2097152]
        access_cost_list = [1, 6, 23, 64]
        static_cost_list = [0.2, 32*0.2, 512*0.2, 4096*0.2] 
        para_count_list = [1, 4, 1, 16]

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list)
        layer = cm.Layer(1, 1, 6, 6, 1, 1, 1)
        tile_generator = cm.mapping_point_generator.blocking_generator_function(layer, 3)    
        expect_result = [[1, 1, 1], [1, 1, 1], [1, 1, 6], [1, 1, 6], [1, 1, 1], [1, 1, 1], [1, 1, 1]]
        self.assertEqual(next(tile_generator), expect_result)
        expect_result = [[1, 1, 1], [1, 1, 1], [1, 1, 6], [1, 2, 3], [1, 1, 1], [1, 1, 1], [1, 1, 1]]
        self.assertEqual(next(tile_generator), expect_result)
        expect_result = [[1, 1, 1], [1, 1, 1], [1, 1, 6], [1, 3, 2], [1, 1, 1], [1, 1, 1], [1, 1, 1]]
        self.assertEqual(next(tile_generator), expect_result)
        expect_result = [[1, 1, 1], [1, 1, 1], [1, 1, 6], [1, 6, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1]]
        self.assertEqual(next(tile_generator), expect_result)
    
    def test_blocking_generator(self):
        capacity_list = [512, 262144] 
        access_cost_list = [1, 23] 
        static_cost_list = [0.2, 512*0.2]  
        para_count_list = [1, 1] 

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list)
        layer = cm.Layer(64, 32, 8, 8, 3, 3, 1)
        mp_generator = cm.mapping_point_generator.mapping_point_generator_function(resource, layer)

        #for mp in mp_generator:
        #    print mp.loop_blockings, mp.loop_orders    

    def test_parationing_generator(self):
        capacity_list = [512, 262144] 
        access_cost_list = [1, 23] 
        static_cost_list = [0.2, 512*0.2]  
        para_count_list = [4, 4] 

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list)
        layer = cm.Layer(64, 32, 8, 8, 3, 3, 1)
        bp_generator = cm.mapping_point_generator.blocking_partitioning_generator_function(resource, layer)

        for bp in bp_generator:
            print bp[0], bp[1] 

if __name__ == '__main__':
    unittest.main()
