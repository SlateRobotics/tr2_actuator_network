#!/usr/bin/env python

import time
import socketserver

from server_state import server_state
from server_html import server_html
from server_ethernet import server_ethernet
from server_actuators import server_actuators

socketserver.TCPServer.allow_reuse_address = True

state = server_state()
server_actuators(state)
server_ethernet(state)
server_html(state)
