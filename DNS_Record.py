import struct


class Record:
    def __init__(self, raw_name, type, cls, ttl, data_length, data):
        self.raw_name = raw_name
        self.type = type
        self.cls = cls
        self.ttl = ttl
        self.data_length = data_length
        self.raw_data = data

    def pack(self):
        return self.raw_name + struct.pack('!HHIH', self.type, self.cls, self.ttl, self.data_length) + self.raw_data
