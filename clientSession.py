#!/usr/bin/env python3

from time import strftime
from library import *
from chatRoom import ChatRoom


class ClientSession(object):
    """
    Class object for holding client related information
    """
    def __init__(self, server, ip, socket):
        """
        :param ip: IP address of client.
        :param socket: Socket at server used to communicate with client.
        """
        self.server = server
        self.ip = ip
        self.socket = socket
        self.username = None
        self.suspended = False
        self.chatroom = None

    def execute(self):
        """
        This is the main per-client execution thread for the server.
        Enable a client to login and proceed to listen to, and forward, its messages.
        """
        msg = '**[Welcome]** Connected to The Clay ChatROOM @ ' + self.server.ip + ':' + str(self.server.port)
        msg += ' Please enter your username'
        send_data(self.socket, color_welcome(msg))
        self.do_login()
        print(color_info('[' + strftime("%H:%M:%S") + '] ' + 'New user ' +
              color_welcome(self.username + ' @ ' + str(self.ip)) +
              color_info(' has joined the Lobby.')))
        if not self.suspended:
            msg = '**[Info]** You have entered the room: ' + self.chatroom.name + \
                '. You are all set to pass messages.'
            send_data(self.socket, color_success(msg))
            send_help(self.socket)
        while not self.suspended:
            self.accept_message()
        self.socket.close()

    def accept_message(self):
        """
        Check the destination field in a message and unicast it to the destination or,
        broadcast if destination is 'all'.
        """
        msg = decode_data(recv_data(self.socket))
        if msg.startswith('/'):
            msg_list = msg.split(' ', 1)
            cmd = msg_list[0][1:]
            try:
                params = msg_list[1].strip()
            except IndexError:
                params = None
            method_name = 'do_' + cmd
            method = getattr(self, method_name, None)
            try:
                method(params)
            except TypeError as e:
                print(color_error("TypeError caught " + str(e)))
                send_data(self.socket, color_error('**[Error]** Sorry, first field in message is illegal.'))
                return
        elif msg.startswith('@'):
            msg_list = msg.split(' ', 1)
            destination = msg_list[0][1:]
            stamp = '[' + strftime("%H:%M:%S") + '] ' + self.username + ' : '
            try:
                msg = stamp + msg_list[1].strip()
            except IndexError:
                msg = stamp + "\aHi"
            dest_client = self.chatroom.get_client(destination)
            if dest_client is None:
                send_data(self.socket, color_error('**[Error]** Sorry, destination client not present in chatroom.'))
            else:
                send_data(dest_client.socket, color_private(msg))
        else:
            stamp = '[' + strftime("%H:%M:%S") + '] ' + self.username + ' : '
            msg = stamp + msg
            self.chatroom.broadcast(color_msg(msg), self.username)

    def do_login(self, tries=5):
        """
        Try tries number of times to establish the clients username
        """
        name = decode_data(recv_data(self.socket))
        if name in list(self.server.clients) + ['server', 'all', 'root', 'me']:
            if tries > 0:
                send_data(self.socket, color_error('**[Error]** Username taken, kindly choose another.'))
                self.do_login(tries - 1)
            else:
                send_data(self.socket, color_error('**[Error]** Max tries reached, closing connection.'))
                self.suspended = True
        else:
            self.username = name
            self.server.clients[self.username] = self  # Add to dictionary in server.
            self.chatroom = self.server.chatrooms['Lobby']
            self.server.chatrooms['Lobby'].add_client(self.username)
        return

    def do_create(self, params=None):
        """
        Create chatroom - Add client as first user of room when a unique name is received
        """
        if self.suspended:
            return
        room_name = params.split(' ', 1)[0]
        try:
            password = params.split(' ', 1)[1]
        except IndexError:
            password = None
        name, names = room_name, list(self.server.chatrooms)
        if name in names:
            send_data(self.socket, color_error('**[Error]** Sorry, chatroom already taken. Please try again.'))
            return
        else:
            send_data(self.socket, color_success('**[Info]** Chatroom ' + name + ' created.'))
            new_room = ChatRoom(self.server, room_name, self.username, password)
            self.server.chatrooms[room_name] = new_room
            self.chatroom = new_room

    def do_join(self, params=None):
        """
        Join to a chatroom by room_name(/password)
        """
        room_name = params.split(' ', 1)[0]
        try:
            password = params.split(' ', 1)[1]
        except IndexError:
            password = None
        if room_name in list(self.server.chatrooms):
            room = self.server.chatrooms[room_name]
            if room.password != password:
                send_data(self.socket, color_warning('**[Warning]** Sorry, This chatroom is private, incorrect password.'))
                return
            if self.suspended:
                return
            room.broadcast(color_info('**[Info]** New user ' + self.username +
                           ' has joined.'), self.username)
            send_data(self.socket, color_success('**[Info]** You have joined chatroom - ' + room_name))
            self.chatroom = room
            room.add_client(self.username)
            if len(room.clients):
                send_data(self.socket, color_msg('Here is a list of peers in the room. \n'))
                send_data(self.socket, color_warning(self.chatroom.get_usernames()))
            return

    def do_exit(self, params=None):
        """
        Exit the chatroom where you were.
        """
        self.chatroom.remove_client(self.username)
        send_data(self.socket, color_success("**[Info]** You have left room: " + self.chatroom.name))
        if len(self.chatroom.clients) == 0:
            self.server.chatrooms.pop(self.chatroom.name)
        else:
            self.chatroom.broadcast(color_info('**[Info]** ' + self.username + ' has left ' + self.chatroom.name), self.username)
        self.chatroom = self.server.chatrooms['Lobby']

    def do_list(self, params=None):
        """
        Send the list of existed chatrooms.
        """
        if len(self.server.chatrooms):
            send_data(self.socket, color_info('**[Info]** Here is a list of chatrooms you can join.'))
            send_data(self.socket, color_warning(self.server.get_chatrooms()))
        else:
            send_data(self.socket, color_info('**[Info]** There are no chatrooms to join now'))

    def do_who(self, params=None):
        if len(self.chatroom.clients):
            send_data(self.socket, color_info('**[Info]** Here is a list of users in the room.\t'))
            send_data(self.socket, color_warning(self.chatroom.get_usernames()))
        else:
            send_data(self.socket, color_info('**[Info]** There are no peers in the room'))

    def do_bye(self, params=None):
        if self.chatroom.name != 'Lobby':
            self.do_exit()
        send_data(self.socket, 'Bye')
        print(color_info('[' + strftime("%H:%M:%S") + '] ' + 'New user ' +
              color_welcome(self.username + ' @ ' + str(self.ip)) +
              color_info(' has left the Lobby.')))
        self.server.disconnect_client(self.username)
        self.suspended = True
