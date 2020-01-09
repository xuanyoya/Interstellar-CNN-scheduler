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
 
    def test_tile_hint(self):
        loop_hint = [[0, 3, 1], None, None]
        result_permutations = cm.mapping_point_generator.loop_tile(6, 3, loop_hint)    
        self.assertEqual(len(result_permutations), 2)
        result_permutations = cm.mapping_point_generator.loop_tile(12, 3, loop_hint)    
        self.assertEqual(len(result_permutations), 3)
        loop_hint = [[0, 3, 4], None, None]
        result_permutations = cm.mapping_point_generator.loop_tile(96, 3, loop_hint)    
        self.assertEqual(len(result_permutations), 4)
    
    def test_tile_generator(self):    
        capacity_list = [512, 4096, 262144]
        access_cost_list = [1, 6, 23]
        static_cost_list = [0.2, 32*0.2, 512*0.2] 
        para_count_list = [1, 4, 1]

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list)
        layer = cm.Layer(1, 1, 6, 6, 1, 1, 1)
        tile_generator = cm.mapping_point_generator.blocking_generator_function(resource, layer)    
        expect_result = [[1, 1, 1], [1, 1, 1], [1, 1, 6], [1, 1, 6], [1, 1, 1], [1, 1, 1], [1, 1, 1]]
        self.assertEqual(next(tile_generator), expect_result)
        expect_result = [[1, 1, 1], [1, 1, 1], [1, 1, 6], [1, 2, 3], [1, 1, 1], [1, 1, 1], [1, 1, 1]]
        self.assertEqual(next(tile_generator), expect_result)
        expect_result = [[1, 1, 1], [1, 1, 1], [1, 1, 6], [1, 3, 2], [1, 1, 1], [1, 1, 1], [1, 1, 1]]
        self.assertEqual(next(tile_generator), expect_result)
        expect_result = [[1, 1, 1], [1, 1, 1], [1, 1, 6], [1, 6, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1]]
        self.assertEqual(next(tile_generator), expect_result)
    
    def test_tile_generator_hint(self):    
        capacity_list = [512, 8192, 2097152]
        access_cost_list = [1, 6, 64]
        static_cost_list = [0.2, 32*0.2, 4096*0.2] 
        para_count_list = [8, 1, 1]

        schedule_hint = {cm.le.FX: [[0, 3, 1], None, None], cm.le.IC: [[1, 4, 2], None, None],
                         cm.le.FY: [[2, 3, 1], None, None], cm.le.OY: [[3, 1, 4], None, None],
                         cm.le.OX: [[4, 1, 1], None, None], cm.le.OC: [[5, 1, 1], None, None],
                         cm.le.ON: [[6, 1, 1], None, None]}

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list)
        layer = cm.Layer(8, 4, 8, 8, 3, 3, 1)
        tile_generator = cm.mapping_point_generator.blocking_generator_function(resource, layer, schedule_hint)    
        expect_result = [[3, 1, 1], [3, 1, 1], [1, 8, 1], [4, 1, 2], [1, 1, 4], [8, 1, 1], [1, 1, 1]]
        self.assertEqual(next(tile_generator), expect_result)
        expect_result = [[3, 1, 1], [3, 1, 1], [1, 8, 1], [4, 1, 2], [1, 2, 2], [8, 1, 1], [1, 1, 1]]
        self.assertEqual(next(tile_generator), expect_result)
        expect_result = [[3, 1, 1], [3, 1, 1], [1, 8, 1], [4, 1, 2], [1, 4, 1], [8, 1, 1], [1, 1, 1]]
        self.assertEqual(next(tile_generator), expect_result)
        expect_result = [[3, 1, 1], [3, 1, 1], [1, 8, 1], [4, 2, 1], [1, 1, 4], [8, 1, 1], [1, 1, 1]]
        self.assertEqual(next(tile_generator), expect_result)
        expect_result = [[3, 1, 1], [3, 1, 1], [1, 8, 1], [4, 2, 1], [1, 2, 2], [8, 1, 1], [1, 1, 1]] 
        self.assertEqual(next(tile_generator), expect_result)
 
    
    def test_tile_generator_hint1(self):
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
        tile_generator = cm.mapping_point_generator.blocking_partitioning_generator_function_with_hint(resource, layer, schedule_hint)    
        expect_result = [[(3, 1), (1, 1), (1, 8), (1, 2), (1, 32), (8, 8), (1, 1)], [(1, 1), (3, 1), (1, 1), (4, 1), (1, 1), (1, 1), (1, 1)]]
        self.assertEqual(next(tile_generator), expect_result)

    def test_tile_generator_hint2(self):
        capacity_list = [512, 131072, 2097152]
        access_cost_list = [1, 6, 64]
        static_cost_list = [0.2, 32*0.2, 4096*0.2]
        para_count_list = [12, 1, 1]

        # {loop: [level, order, blocking, partitioning]}
        schedule_hint = {cm.le.FX: [[0, 3, 1], None, None], cm.le.IC: [[1, 8, 1], None, None],
                         cm.le.FY: [[2, 1, 3], None, None], cm.le.OY: [[3, 1, 4], None, None],
                         cm.le.OX: [[4, 1, 1], None, None], cm.le.OC: [[5, 1, 1], None, None],
                         cm.le.ON: [[6, 1, 1], None, None]}

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0, 0], [2])
        layer = cm.Layer(64, 32, 8, 8, 3, 3, 1)
        tile_generator = cm.mapping_point_generator.blocking_partitioning_generator_function_with_hint(resource, layer, schedule_hint)    
        expect_result = [[(3, 1, 1), (1, 1, 1), (1, 8, 1), (1, 1, 2), (1, 32, 1), (8, 8, 1), (1, 1, 1)], [(1, 1, 1), (3, 1, 1), (1, 1, 1), (4, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1)]]
        self.assertEqual(next(tile_generator), expect_result)
        #tile_generator = cm.mapping_point_generator.blocking_generator_function(layer,3, schedule_hint)    
        #self.assertEqual(next(tile_generator), expect_result)
        #for tile in tile_generator:
        #    print  tile 

    def test_tile_generator_hint3(self):
        capacity_list = [512, 131072, 2097152]
        access_cost_list = [1, 6, 64]
        static_cost_list = [0.2, 32*0.2, 4096*0.2]
        para_count_list = [12, 1, 1]

        # {loop: [level, order, blocking, partitioning]}
        schedule_hint = {cm.le.FX: [[0, 3, 1], None, None], 
                         cm.le.FY: [[1, 1, 3], None, None], cm.le.OY: [[2, None, 4], None, None]}

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0, 0], [2])
        layer = cm.Layer(64, 32, 8, 8, 3, 3, 1)
        tile_generator = cm.mapping_point_generator.blocking_partitioning_generator_function_with_hint(resource, layer, schedule_hint)
        expect_result = [[(3, 1, 1), (1, 1, 1), (8, 1, 1), (2, 1, 1), (1, 32, 1), (1, 64, 1), (1, 1, 1)], [(1, 1, 1), (3, 1, 1), (1, 1, 1), (4, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1)]]
        self.assertEqual(next(tile_generator), expect_result)

    def test_tile_generator_hint4(self):

        # {loop: [level, order, blocking, partitioning]}
        schedule_hint = {cm.le.FX: [None, [0, 3, 1], None],
                         cm.le.IC: [None, [1, 1, 4], None], cm.le.OC: [None, [2, 1, 4], None]}

        tile_per = []
        cm.mapping_point_generator.loop_tile_with_hint(tile_per, 32, 3, schedule_hint[cm.le.IC])
        self.assertEqual(tile_per[0], [8, 4, 1])
        self.assertEqual(tile_per[1], [1, 4, 8])
        self.assertEqual(tile_per[2], [2, 4, 4])
        self.assertEqual(tile_per[3], [4, 4, 2])

        tile_per = []
        cm.mapping_point_generator.loop_tile_with_hint(tile_per, 42, 3, schedule_hint[cm.le.OC])
        self.assertEqual(tile_per[0], [1, 4, 11])
        self.assertEqual(tile_per[1], [11, 4, 1])
 
        tile_per = []
        schedule_hint = {cm.le.IC: [None, [1, 2, 4], None, None], cm.le.OC: [None, [2, 1, 4], None, None]}
        cm.mapping_point_generator.loop_tile_with_hint(tile_per, 64, 4, schedule_hint[cm.le.IC])
        self.assertEqual(tile_per[0], [8, 8, 1, 1])
        self.assertEqual(tile_per[1], [1, 8, 8, 1])
        self.assertEqual(tile_per[3], [1, 8, 2, 4])
        self.assertEqual(tile_per[9], [4, 8, 2, 1])

        tile_per = []
        schedule_hint = { cm.le.IC: [[1, 1, 4], None, None], cm.le.OC: [[2, 1, 4], None, None]}
        cm.mapping_point_generator.loop_tile_with_hint(tile_per, 64, 3, schedule_hint[cm.le.IC])
        self.assertEqual(tile_per[0], [4, 16, 1])
        self.assertEqual(tile_per[2], [4, 2, 8])
        self.assertEqual(tile_per[4], [4, 8, 2])

        tile_per = []
        schedule_hint = { cm.le.IC: [[0, None, 4], None, None], cm.le.OC: [[2, 1, 4], None, None]}
        cm.mapping_point_generator.loop_tile_with_hint(tile_per, 64, 3, schedule_hint[cm.le.IC])
        self.assertEqual(tile_per[0], [64, 1, 1])
        self.assertEqual(tile_per[3], [4, 2, 8])
        self.assertEqual(tile_per[14], [16, 4, 1])

        tile_per = []
        schedule_hint = { cm.le.IC: [None, [0, None, 4], None], cm.le.OC: [None, [2, 1, 4], None]}
        cm.mapping_point_generator.loop_tile_with_hint(tile_per, 64, 3, schedule_hint[cm.le.IC])
        self.assertEqual(tile_per[0], [16, 4, 1])
        self.assertEqual(tile_per[4], [1, 8, 8])
        self.assertEqual(tile_per[14], [8, 4, 2])
 
    def test_tile_generator_hint5(self):
        capacity_list = [32, 512, 2097152]
        access_cost_list = [1, 6, 64]
        static_cost_list = [0.2, 32*0.2, 4096*0.2]
        para_count_list = [1, 16, 1]

        # {loop: [level, order, blocking, partitioning]}
        schedule_hint = {cm.le.FX: [None, [0, 3, 1], None],
                         cm.le.IC: [None, [1, None, 4], None], cm.le.OC: [None, [2, None, 4], None]}

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [0, 1, 0], [2])
        layer = cm.Layer(64, 32, 8, 8, 3, 3, 1)
        #tile_per = []
        #cm.mapping_point_generator.loop_tile_with_hint(tile_per, 32, 3, schedule_hint[cm.le.IC])
        #for tile in tile_per:
       #     print tile
        #tile_generator = cm.mapping_point_generator.blocking_partitioning_generator_function_with_hint(resource, layer, schedule_hint)
        #for tile in tile_generator:
        #    print  tile 

    def test_parallel_blocking(self):
        capacity_list = [512, 131072, 2097152]
        access_cost_list = [1, 6, 64]
        static_cost_list = [0.2, 32*0.2, 4096*0.2]
        para_count_list = [12, 1, 1]

        # {loop: [level, order, blocking, partitioning]}
        schedule_hint = {cm.le.FX: [[0, 3, 1], None, None], 
                         cm.le.FY: [[1, None, 3], None, None], cm.le.OY: [[2, None, 4], None, None]}

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0, 0], [2])
        layer = cm.Layer(32, 32, 16, 16, 3, 3, 4)
        loop_blocking = [(3, 1, 1), (3, 1, 1), (1, 16, 1), (4, 4, 1), (8, 2, 2), (2, 4, 8), (4, 1, 1)]

        parallel_generator = cm.mapping_point_generator.parallel_blocking_generator_function(zip(*loop_blocking), resource, layer) 
        self.assertEqual(next(parallel_generator), ([1, 1, 1, 1, 2, 2, 3], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1]))
        self.assertEqual(next(parallel_generator), ([1, 1, 1, 1, 3, 1, 4], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1]))
        self.assertEqual(next(parallel_generator), ([1, 1, 1, 1, 3, 2, 2], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1]))

        parallel_generator = cm.mapping_point_generator.parallel_blocking_generator_function(zip(*loop_blocking), resource, layer, schedule_hint) 
        self.assertEqual(next(parallel_generator), ([1, 3, 1, 4, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1]))
    
    def test_parallel_blocking_partial_hint(self):
        capacity_list = [512, 131072, 2097152]
        access_cost_list = [1, 6, 64]
        static_cost_list = [0.2, 32*0.2, 4096*0.2]
        para_count_list = [48, 1, 1]

        # {loop: [level, order, blocking, partitioning]}
        schedule_hint = {cm.le.FX: [[0, 3, 1], None, None], 
                         cm.le.FY: [[1, None, 3], None, None], cm.le.OY: [[2, None, 4], None, None]}

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0, 0], [2], [cm.le.OC, cm.le.IC, cm.le.ON])
        layer = cm.Layer(32, 32, 16, 16, 3, 3, 4)
        loop_blocking = [(3, 1, 1), (3, 1, 1), (1, 16, 1), (4, 4, 1), (8, 2, 2), (2, 4, 8), (4, 1, 1)]

        parallel_generator = cm.mapping_point_generator.parallel_blocking_generator_function(zip(*loop_blocking), resource, layer, schedule_hint) 
        self.assertEqual(next(parallel_generator), ([1, 3, 1, 4, 1, 1, 4], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1]))
        self.assertEqual(next(parallel_generator), ([1, 3, 1, 4, 1, 2, 2], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1]))
        self.assertEqual(next(parallel_generator), ([1, 3, 1, 4, 2, 1, 2], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1]))
        self.assertEqual(next(parallel_generator), ([1, 3, 1, 4, 2, 2, 1], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1]))
        self.assertEqual(next(parallel_generator), ([1, 3, 1, 4, 4, 1, 1], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1]))
    
    def test_parallel_blocking_partial_hint1(self):
        capacity_list = [512, 131072, 2097152]
        access_cost_list = [1, 6, 64]
        static_cost_list = [0.2, 32*0.2, 4096*0.2]
        para_count_list = [48, 1, 1]

        # {loop: [level, order, blocking, partitioning]}
        schedule_hint = {cm.le.FX: [[0, 3, 1], None, None], 
                         cm.le.FY: [[1, None, 3], None, None], cm.le.OC: [[2, None, 4], None, None]}

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [1, 0, 0], [2], [cm.le.OC, cm.le.IC, cm.le.ON])
        layer = cm.Layer(32, 32, 16, 16, 3, 3, 4)
        loop_blocking = [(3, 1, 1), (3, 1, 1), (1, 16, 1), (4, 4, 1), (8, 2, 2), (2, 4, 8), (4, 1, 1)]

        parallel_generator = cm.mapping_point_generator.parallel_blocking_generator_function(zip(*loop_blocking), resource, layer, schedule_hint) 
        self.assertEqual(next(parallel_generator), ([1, 3, 1, 1, 4, 1, 4], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1]))
        self.assertEqual(next(parallel_generator), ([1, 3, 1, 1, 4, 2, 2], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1]))
        self.assertEqual(next(parallel_generator), ([1, 3, 1, 1, 8, 1, 2], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1]))
        self.assertEqual(next(parallel_generator), ([1, 3, 1, 1, 8, 2, 1], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1]))


    def test_parallel_blocking_partial_hint2(self):
        capacity_list = [512, 131072, 2097152]
        access_cost_list = [1, 6, 64]
        static_cost_list = [0.2, 32*0.2, 4096*0.2]
        para_count_list = [1, 64, 1]

        # {loop: [level, order, blocking, partitioning]}
        schedule_hint = {cm.le.IC: [None, [1, None, 4], None], cm.le.OC: [None, [2, None, 4], None]}

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [0, 1, 0], [2], [cm.le.OC, cm.le.IC, cm.le.ON])
        layer = cm.Layer(32, 32, 16, 16, 3, 3, 4)
        loop_blocking = [(3, 1, 1), (3, 1, 1), (1, 16, 1), (4, 4, 1), (2, 8, 2), (2, 4, 8), (1, 4, 1)]

        parallel_generator = cm.mapping_point_generator.parallel_blocking_generator_function(zip(*loop_blocking), resource, layer, schedule_hint) 
        self.assertEqual(next(parallel_generator), ([1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 4, 4, 4], [1, 1, 1, 1, 1, 1, 1]))
        self.assertEqual(next(parallel_generator), ([1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 8, 4, 2], [1, 1, 1, 1, 1, 1, 1]))      
        

    def test_parallel_blocking_partial_hint3(self):
        capacity_list = [512, 131072, 2097152]
        access_cost_list = [1, 6, 64]
        static_cost_list = [0.2, 32*0.2, 4096*0.2]
        para_count_list = [1, 64, 1]

        # {loop: [level, order, blocking, partitioning]}
        schedule_hint = {cm.le.OX: [None, [1, None, 4], None], cm.le.OC: [None, [2, None, 4], None]}

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list, 0, [0, 1, 0], [2], [cm.le.OC, cm.le.IC, cm.le.ON])
        layer = cm.Layer(32, 32, 16, 16, 3, 3, 4, 4, 4)
        loop_blocking = [(3, 1, 1), (3, 1, 1), (1, 16, 1), (4, 4, 1), (2, 8, 2), (2, 4, 8), (1, 4, 1)]

        parallel_generator = cm.mapping_point_generator.parallel_blocking_generator_function(zip(*loop_blocking), resource, layer, schedule_hint) 
        self.assertEqual(next(parallel_generator), ([1, 1, 1, 1, 1, 1, 1], [1, 1, 4, 1, 4, 1, 2], [1, 1, 1, 1, 1, 1, 1]))
        self.assertEqual(next(parallel_generator), ([1, 1, 1, 1, 1, 1, 1], [1, 1, 4, 1, 4, 2, 1], [1, 1, 1, 1, 1, 1, 1]))
        self.assertEqual(next(parallel_generator), ([1, 1, 1, 1, 1, 1, 1], [1, 1, 4, 1, 8, 1, 1], [1, 1, 1, 1, 1, 1, 1]))
 

    '''
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
        capacity_list = [128, 665536] 
        access_cost_list = [1, 23] 
        static_cost_list = [0.2, 512*0.2]  
        para_count_list = [4, 4] 

        resource = cm.Resource(capacity_list, access_cost_list, static_cost_list, para_count_list)
        layer = cm.Layer(64, 32, 8, 8, 3, 3, 1)
        bp_generator = cm.mapping_point_generator.blocking_partitioning_generator_function(resource, layer)

        for bp in bp_generator:
            print bp[0], bp[1] 
    '''
if __name__ == '__main__':
    unittest.main()
