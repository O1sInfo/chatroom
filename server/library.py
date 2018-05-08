#!/usr/bin/env python3

from socket import error
import random
import sys


colors = {"pink": '\033[95m',
          "white": '\033[97m',
          "blue": '\033[94m',
          "green": '\033[92m',
          "yellow": '\033[93m',
          "red": '\033[91m',
          "sky": '\033[96m'
          }

ENDC = "\033[0m"
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


def color_msg(msg):
    return colors["sky"] + msg + ENDC


def color_private(msg):
    return UNDERLINE + colors["blue"] + msg + ENDC + ENDC


def color_warning(msg):
    return colors["yellow"] + msg + ENDC


def color_error(msg):
    return colors["red"] + msg + ENDC


def color_success(msg):
    return colors["green"] + msg + ENDC


def color_info(msg):
    return colors["pink"] + msg + ENDC


def color_welcome(msg):
    return BOLD + UNDERLINE + colors["yellow"] + msg + ENDC + ENDC + ENDC


def client_send(s, data):
    """
    Try send data to server using socket s.
    """
    try:
        s.sendall(data)
    except error:
        print('**[Error]** sendall data socket.error')


def client_recv(s):
    """
    Receive 4KB data from server and decode and return message after splitting using delimiter '|'
    """
    try:
        recv = s.recv(4096)
        recv = str(recv, 'utf-8')
    except UnicodeDecodeError:
        print('**[Warning]** Unexpected byte stream in received data')
    except error:
        print('**[Warning]** recv_data socket.error')
    if recv[-1:] == '\n':
        recv = recv[:-1]
    print(recv)
    return recv


def send_data(s, data):
    """
    Send data to client via socket s
    """
    try:
        s.send(bytes(data, 'utf-8'))
    except error:
        print('**[Error]** send_data socket.error')


def recv_data(s):
    """
    Receive up to 4KB data into socket s and return the data
    """
    try:
        recv_buf = s.recv(4096)
    except error:
        print('**[Warning]** recv_data socket.error')
    return recv_buf


def decode_data(recv_buf):
    """
    Remove trailing \r\n added
    """
    try:
        recv_buf = str(recv_buf, 'utf-8')
        if recv_buf[-2:] == '\r\n':
            recv_buf = recv_buf[:-2]
        elif recv_buf[-1:] == '\n':
            recv_buf = recv_buf[:-1]
    except UnicodeDecodeError:
        print('**[Warning]** Unexpected byte stream in received data')
    return recv_buf


def bind_to_port(s, port):
    """
    :param s: Socket to bind
    :param port: Port to bind to
    :return: True on success, False otherwise
    """
    try:
        s.bind(('', port))
    except error:
        return False
    return True


def bind_to_random(s, tries=10, start=40000, stop=50000):
    """
    Try to bind to random port from start to stop port numbers, tries number of times.
    :param tries:
    :param start:
    :param stop:
    """
    while tries > 0:
        port = random.randint(start, stop - 1)
        tries = -1 if bind_to_port(s, port) else tries - 1
    if tries is 0:
        print("Couldn't bind to data port. Aborting...")
        sys.exit()
    return port


def send_help(s):
    help_menu = """-----------------------------------------
    Usage: /<command>[params] OR @<username> [messages]
    Prefixion:
        /[command]\t\tRun a command.
        @[username]\t\tSend a private messages to a user by it's username.
    Option commands:
        who\t\t\tList other users in the room.
        list\t\t\tList the available chatroom.
        create roomname [password]\tCreate a chatroom named roomname. You can also use a password to protect, default None.
        join roomname [password]\tJoin a exited chatroom named roomname. Maybe you need a password if it's privated.
        exit\t\t\tExit the current.
        bye\t\t\tDisconnect the server.
    ---------------------------------------------------
    """
    send_data(s, color_info(help_menu))
