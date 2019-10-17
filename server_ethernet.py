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

class ethernet_handler:
	state = None

	ethernet_socket = None

	tcp_ip = "192.168.77.1"
	tcp_port = 12345

	def __init__(self, s):
		self.state = s

		if "/home/pi/" not in self.state.cfg_path:
			self.tcp_ip = ""

	def receive(self):
		res = self.ethernet_socket.recv(4096).decode()

		cmds = res.split(';')
		for c in cmds:
			if c and len(c.split(':')) > 1:
				id = c.split(':')[0]
				cmd = c.split(':')[1] + ';'
				self.state.editRouteCommand("/cmd/"+id,cmd)

	def send(self):
		_states = ""
		for i in range(self.state.getNumRoutes()):
			routeName = self.state.getRouteName(i)
			aid = routeName.split("/cmd/")[1]
			if self.state.isStateActive(routeName):
				state = self.state.getActuatorState(routeName)
				_states = _states + aid + ":" +  state + ";"

		if _states == "":
			_states = "ns;"
		else:
			_states = _states + ";"

		print(" -> ", _states)
		self.ethernet_socket.send(_states.encode())

	def run(self):
		while True:
			try:
				self.ethernet_socket = None
				connected = False
				print("ETHERNET: Waiting for connection on " + self.tcp_ip + ":" + str(self.tcp_port))
				while connected == False:
					try:
						self.ethernet_socket = socket.socket()
						self.ethernet_socket.settimeout(2)
						self.ethernet_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
						self.ethernet_socket.connect((self.tcp_ip, self.tcp_port))
						connected = True
					except:
						time.sleep(0.5)

				print("ETHERNET: Got connection from ethernet")

				while connected == True:
					self.receive()
					self.send()

			except Exception as e:
				print("ETHERNET:", e)
				print('ETHERNET: restarting thread')
			else:
				print('ETHERNET: exited normally, bad thread; restarting')


class server_ethernet:
	state = None

	def __init__(self, s):
		self.state = s
		self.run()

	def run(self):
		eh = ethernet_handler(self.state)
		t = threading.Thread(target=eh.run, args=())
		t.daemon = True
		t.start()
