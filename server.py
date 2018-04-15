import socket
import os.path
import pickle
import time
import argparse

from DNS_Message import DNS_Message


class DNS_Server:
    def __init__(self, forwarder_ip, cache_file):
        self.cache_file = cache_file
        self.cache = {1: {}, 2: {}}
        self.forwarder = (forwarder_ip, 53)
        self.load_cache()

    def load_cache(self):
        if os.path.isfile(self.cache_file):
            with open(self.cache_file, 'rb') as file:
                self.cache = pickle.load(file)

    def save_cache(self):
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.cache, f)

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(('', 53))

            while True:
                try:
                    query, addr = sock.recvfrom(1024)
                    answer = self.get_answer(query)
                    sock.sendto(answer, addr)
                except Exception as e:
                    print(e)

    def get_answer(self, query):
        message = DNS_Message(query)
        answer = b''
        for q in message.queries:
            if q.type in self.cache and q.name in self.cache[q.type]:
                answ_list = self.cache[q.type][q.name]
                if answ_list[0][1] > int(time.time()):
                    answer = message.pack_answer(q, answ_list)
                    print('Answer from cache')
                else:
                    self.cache[q.type].pop(q.name)
            else:
                answer = self.ask_forwarder(query)
                parsed_answer = DNS_Message(answer)
                if parsed_answer.a_answers:
                    self.cache[1][q.name] = parsed_answer.a_answers
                if parsed_answer.ns_answers:
                    self.cache[2][q.name] = parsed_answer.ns_answers
        return answer

    def ask_forwarder(self, query):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(self.forwarder)
            sock.settimeout(2)
            sock.send(query)
            try:
                return sock.recv(1024)
            except socket.timeout:
                print('timeout was 2 seconds')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Caching DNS server maintaining A and NS records')
    parser.add_argument('-f', '--forwarder', type=str, help='forwarding server ip', default='8.8.8.8')
    parser.add_argument('-c', '--cache', type=str, help='cache file name', default='cache')
    args = parser.parse_args()
    server = DNS_Server(args.forwarder, args.cache)
    try:
        server.run()
    except KeyboardInterrupt:
        server.save_cache()
        exit()
