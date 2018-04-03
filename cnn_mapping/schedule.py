'''
Schedule hint
'''

import loop_enum as le

class Schedule(object):

    def __init__(self, schedule_hint, partition_loops=None):

        self.schedule_hint = schedule_hint
        if partition_loops != None:
            self.partition_loops = []
            for l in partition_loops:
                self.partition_loops.append(le.loop_table[l])
        else:
            self.partition_loops = partition_loops       

        num_levels = len(schedule_hint.values()[0])
        hint_para_index = {}
        for loop in schedule_hint:
            for level in xrange(num_levels):
                if schedule_hint[loop][level] != None and schedule_hint[loop][level][2] != None:
                    if level not in hint_para_index:
                        hint_para_index[level] = [loop]
                    else:
                        hint_para_index[level].append(loop)
        self.hint_para_index = hint_para_index

    @classmethod
    def schedule(cls, info):
        return cls(info["schedule_hint"], info["partition_loops"]) 
