#!/usr/bin/env python

from urllib import parse
import re
import time
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
from _thread import *
import threading

socketserver.TCPServer.allow_reuse_address = True

class tcp_server_thread:
	state = None

	def __init__(self, s):
		self.state = s

	def run(self, c):
		while True:
			try:
				data = c.recv(1024).decode()
				if not data:
					break

				aid = data.split(':')[0]

				# return cfg if needed
				if data.split(':')[1].split(';')[0] == '?':
					cfg = self.state.readConfig(aid)
					cfg = cfg.replace('\r','').replace('\n','')
					msg = "cfg:" + cfg + ";\r\n"
					c.send(msg.encode())
				else:
					state = data.split(':')[1].split(';')[0]
					print(" <- ", aid, state)
					self.state.setActuatorState("/cmd/" + aid, state)

					# update cfg if needed
					if len(data.split(':')[1].split(';')) > 1:
						cfg = data.split(':')[1].split(';')[1]
						self.state.updateConfig(aid, cfg + ";")

					# get and send cmd
					msg = "cmd:nc;"
					for i in range(self.state.numRoutes):
						if aid in self.state.routeNames[i]:
							cmd = self.state.getRouteCommand("/cmd/" + aid)
							if cmd != "":
								msg = "cmd:" + cmd
								self.state.commandsReceived[i] = True
					msg = msg + ";\r\n"
					if aid == "a4" and msg != "cmd:nc;;\r\n":
						print("ACTUATOR: -> " + msg)
					c.send(msg.encode())
			except Exception as e:
				print("ACTUATOR:",e)
				print('ACTUATOR: {!r}; exiting thread'.format(e))
				break
		c.close()

class tcp_server:
	state = None

	def __init__(self, s):
		self.state = s

	def run(self):
		while True:
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				s.bind(("", 1738))
				s.listen(15)

				while True:
					conn, addr = s.accept()
					conn.settimeout(3)
					print('ACTUATOR: Connected to :', addr[0], ':', addr[1])
					ts = tcp_server_thread(self.state)
					start_new_thread(tcp_server_thread.run, (ts, conn,))
				s.close()
			except Exception as e:
				print("ACTUATOR:", e)
				print('ACTUATOR: {!r}; restarting thread'.format(e))

class server_actuators:
	state = None

	def __init__(self, s):
		self.state = s
		self.run()

	def run(self):
		ts = tcp_server(self.state)
		t = threading.Thread(target=ts.run, args=())
		t.daemon = True
		t.start()
