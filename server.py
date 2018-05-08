#!/usr/bin/env python3

import sys
import socket
import threading
import argparse
from library import *
from chatRoom import ChatRoom
from clientSession import ClientSession


class Server(object):
    """
    Class object that stores all server related info.
    """
    def __init__(self, ip="0.0.0.0", port=50000):
        """
        self.clients is a list of all client objects instantiated by the server.
        Objects are not deleted once they are disconnected, so that indexing is maintained.
        However, the client object has a self.suspended field to check if the client is active.
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = port
        self.ip = ip
        self.clients = {}
        self.chatrooms = {'Lobby': ChatRoom(self, "Lobby", "Server")}
        self.suspended = False

    def disconnect_client(self, username):
        """
        Remove username from dictionary of clients.
        """
        self.chatrooms['Lobby'].remove_client(username)
        try:
            self.clients.pop(username)
        except KeyError:
            print(color_warning('Client not in Server.clients.'))

    def get_chatrooms(self):
        """
        Return a list of chatroom names.
        """
        return '  '.join([room for room in self.chatrooms])

    def go_online(self, tries=10):
        """
        Bind to a connection port and start listening on it.
        """
        flag = False
        start = self.port
        for listen_port in range(start, start + tries - 1):
            if bind_to_port(self.s, listen_port):
                flag = True
                break
        if not flag:
            print(color_error("Couldn't bind to connection port. Aborting..."))
            sys.exit()
        self.s.listen(25)
        self.port = listen_port
        print(color_success('Server is listening at ' + self.ip + ':' + str(self.port)))

    def broadcast(self, msg):
        """
        Send a message to all clients connected to server
        """
        for client in self.clients:
            try:
                client.socket.send(bytes(msg, 'utf-8'))
            except socket.error:
                print(color_warning("send_data error to ", client.username))

    def execute(self):
        """
        This is the main server thread. Go online and start listening for connections.
        Accept client connections and start a new client thread using its execute method.
        """
        self.go_online()
        while not self.suspended:
            cs, addr = self.s.accept()
            client = ClientSession(self, addr, cs)
            print(color_success('Incoming connection from ' + str(addr)))
            if not self.suspended:
                t1 = threading.Thread(target=client.execute, args=(), daemon=True)
                t1.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="ChatRoom CLI. Author: claylau")
    parser.add_argument("--host", type=str, dest="ip", default="0.0.0.0",
                        help="Specific the Server's IP. Defalut: 0.0.0.0")
    parser.add_argument("--port", type=int, dest="port", default=50000,
                        help="Specific the Server'IP. Default: 50000")
    args = parser.parse_args()
    s1 = Server(args.ip, args.port)
    s1.execute()
