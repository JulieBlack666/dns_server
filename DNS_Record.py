import struct

import time


class Record:
    def __init__(self, raw_name, type, cls, del_time, data_length, data):
        self.raw_name = raw_name
        self.type = type
        self.cls = cls
        self.del_time = del_time
        self.data_length = data_length
        self.raw_data = data

    def pack(self):
        return self.raw_name + struct.pack('!HHIH', self.type, self.cls, self.del_time - int(time.time()),
                                           self.data_length) + self.raw_data
