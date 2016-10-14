
# -*- coding: utf-8 -*-
"""
@autor: Yev
"""

from client import *

"""
Script run after the main_windows.py has been run... esure that host and port are correct between client and server
Client will attempt to connect to server and the file to server for calculations to be done there
"""

if __name__ == '__main__':

	client = SocketClient("operations.txt", 'localhost', port = 2323)

