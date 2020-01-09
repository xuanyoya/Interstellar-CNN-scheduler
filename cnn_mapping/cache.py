from collections import deque

class Cache(object):
    '''
    Helper class for cache computed values to reduce runtime
    '''

    def __init__(self, num_levels, size):
        self.num_levels = num_levels
        self.cache_map = [dict() for x in range(num_levels)]
        self.cache_queue = [deque() for i in range(num_levels)]
        self.size = size

    def read_cache(self, level, data):
        '''
        Only read cache, no change to make
        '''
        if len(self.cache_map[level]) == 0 or data not in self.cache_map[level]:
            return None
        else:
            return self.cache_map[level][data]    

    def write_cache(self, level, data, value):
        '''
        Only write cache, change map and queue
        ''' 
        assert len(self.cache_map[level]) == len(self.cache_queue[level])
        self.cache_map[level][data] = value
        self.cache_queue[level].append(data)

        if len(self.cache_queue[level]) > self.size:
            pop_ele = self.cache_queue[level].popleft()
            del self.cache_map[level][pop_ele] 


       
