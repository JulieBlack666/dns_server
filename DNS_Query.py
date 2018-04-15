import struct


class Query:
    def __init__(self, domain_name, type, cls, raw_name):
        self.name = domain_name
        self.type = type
        self.cls = cls
        self.raw_name = raw_name

    def pack(self):
        return self.raw_name + struct.pack('!HH', self.type, self.cls)
