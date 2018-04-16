import struct
import time

from collections import defaultdict

from DNS_Query import Query
from DNS_Record import Record


class DNS_Message:
    def __init__(self, bytes_message):
        self.id = 0
        self.flags = 0
        self.qdcount = 0
        self.ancount = 0
        self.nscount = 0
        self.arcount = 0
        self.queries = []
        self.a_answers = defaultdict(list)
        self.ns_answers = defaultdict(list)
        self.parse_message(bytes_message)

    def parse_message(self, message):
        self.id, self.flags, self.qdcount, self.ancount, self.nscount, self.arcount \
            = struct.unpack_from('!HHHHHH', message)
        offset = 12
        for i in range(self.qdcount):
            name, new_offset = self.parse_name(message, offset)
            type, cls = struct.unpack_from('!HH', message, new_offset)
            self.queries.append(Query(name, type, cls, message[offset:new_offset]))
            offset = new_offset + 4
        for i in range(self.ancount + self.nscount + self.arcount):
            parsed_name, offset = self.parse_name(message, offset)
            type, cls, ttl, length = struct.unpack_from('!HHIH', message, offset)
            offset += 10
            if type == 1:
                self.a_answers[parsed_name].append(Record(b'\xc0\x0c', type, cls, int(time.time()) + ttl,
                                                          length, message[offset:offset+length]))
            if type == 2:
                self.ns_answers[parsed_name].append(Record(b'\xc0\x0c', type, cls, int(time.time()) + ttl,
            offset += length

    def parse_name(self, bytes, offset):
        bytes_count = bytes[offset]
        name = ''
        while bytes_count != 0:
            name += '.'
            if bytes_count >= 64:
                new_offset = struct.unpack_from('!H', bytes, offset)[0] - (2**14 + 2**15)
                part_name, _ = self.parse_name(bytes, new_offset)
                offset += 1
                name += part_name
                break
            else:
                offset += 1
                for i in range(bytes_count):
                    name += struct.unpack_from('!c', bytes, offset)[0].decode()
                    offset += 1
                    i += 1
            bytes_count = bytes[offset]
        offset += 1
        return name[1:], offset

    def pack_answer(self, query, answers):
        self.ancount = len(answers)
        answer = struct.pack('!HHHHHH', self.id, self.flags + 2**15, self.qdcount,
                             self.ancount, self.nscount, self.arcount)
        answer += query.pack()
        for answ in answers:
            answer += answ.pack()
        return answer
