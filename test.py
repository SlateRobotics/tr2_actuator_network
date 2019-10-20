#!/usr/bin/env python

import time
from random import shuffle
from random import randrange
import socket

aids = ["b0","b1","a0","a1","a2","a3","a4","g0","h0","h1"]

class test_server_actuators:
	aid = None
	state = 2.0
	cfg = "0,4810,60,;"
	socket = None

	i = 0

	def __init__(self, aid):
		self.aid = aid
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect(("", 1738))
		self.getCfg()

	def getCfg(self):
		data = self.aid + ":?;"
		self.socket.send(data.encode())
		print(self.aid, "->", data)
		data = self.socket.recv(409).decode()
		print(self.aid, "<-", data)

	def setState(self):
		self.state = (randrange(999) + 1.0) / 1000.0 * 6.28

	def setCfg(self):
		self.cfg = str(randrange(255)) + ","
		self.cfg = self.cfg + str(randrange(255)) + ","
		self.cfg = self.cfg + str(randrange(255)) + ",;"

	def step(self):
		data = self.aid + ":" + "{0:.6f}".format(self.state) + ";" + self.cfg
		self.socket.send(data.encode())
		print(self.aid, "->", data)

		data = self.socket.recv(4096).decode()

		self.setState()
		self.setCfg()

		self.i = self.i + 1
		print(self.aid, "<-", data)

	def close(self):
		self.socket.close()

class test_server_ethernet:
	socket = None
	conn = None
	addr = None

	aids = []
	cmds = ""

	def __init__(self, aids):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind(("", 12345))
		self.socket.listen(2)

		self.conn, self.addr = self.socket.accept()
		self.conn.settimeout(3)

		self.aids = aids

	def setCmds(self):
		self.cmds = ""
		for aid in self.aids:
			cmd = str(randrange(255)) + ","
			cmd = cmd + str(randrange(255)) + ","
			cmd = cmd + str(randrange(255)) + ","
			cmd = cmd + str(randrange(255))
			self.cmds = self.cmds + aid + ":" + cmd + ";"

	def step(self):
		self.setCmds()
		data_send = self.cmds
		self.conn.send(data_send.encode())
		print("eth ->", data_send)
		data_recv = self.conn.recv(4096).decode()
		print("eth <-", data_recv)

	def close(self):
		self.conn.close()
		self.socket.close()

def test():
	global aids

	tse = test_server_ethernet(aids)
	tsa = []

	for aid in aids:
		tsa.append(test_server_actuators(aid))

	test_len = 100
	for i in range(test_len):
		tse.step()
		for t in tsa:
			t.step()
		shuffle(tsa)

	tse.close()
	for t in tsa:
		t.close()

test()
