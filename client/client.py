#!/usr/bin/env python3

import socket
import threading
import argparse
import sys
from library import *


class Client(object):
    """
    Class object that stores peer information
    """
    def __init__(self, sip="127.0.0.1", sport=50000):
        """
        Connect to server
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.suspended = False
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = bind_to_random(self.s)
        #  Try connecting to server. Exit on failure.
        try:
            self.s.connect((sip, sport))
        except socket.error:
            sys.exit(color_error("Can't connect to server."))

    def receive(self):
        """
        Until client is suspended, keep listening to messages from server and perform necessary actions.
        Receive 4KB data from server and decode and return message after splitting using delimiter '|'
        """
        while not self.suspended:
            try:
                recv = self.s.recv(4096)
                recv = str(recv, 'utf-8').rstrip()
            except UnicodeDecodeError:
                print('Unexpected byte stream in received data')
            except socket.error:
                print('recv_data error')
            if recv == 'Bye':
                self.suspended = True
            print(recv)

    def send(self):
        """
        Until client is suspended, keep listening to inputs from user and forward the message to the server.
        """
        while not self.suspended:
            user_input = input()
            try:
                self.s.sendall(bytes(user_input, 'utf-8'))
            except socket.error:
                print('sendall data error')

    def execute(self):
        """
        Keep listening to messages from server and inputs from user in parallel.
        Exit when suspended.
        """
        t1 = threading.Thread(target=self.receive, args=(), daemon=True)
        t1.start()
        t2 = threading.Thread(target=self.send, args=(), daemon=True)
        t2.start()
        t1.join()
        t2.join()
        self.s.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="ChatRoom CLI. Author: claylau")
    parser.add_argument("--host", type=str, dest="ip", default="127.0.0.1",
                        help="Specific the Server's IP. Defalut: 127.0.0.1")
    parser.add_argument("--port", type=int, dest="port", default=50000,
                        help="Specific the Server'IP. Default: 50000")
    args = parser.parse_args()
    c1 = Client(sip=args.ip, sport=args.port)
    c1.execute()
