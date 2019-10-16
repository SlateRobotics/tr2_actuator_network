#!/usr/bin/env python

import time
import socket

a0_cmd = "0,1,2,3,;"
a0_cfg = "0,4810,60,;"

server_ethernet_socket = None
server_actuators_socket = None

def test_server_actuators_state():
	global server_actuators_socket, cfg

	data = "a0:2.0;" + a0_cfg
	server_actuators_socket.send(data.encode())
	data = server_actuators_socket.recv(1024).decode()

	if "cmd" in data and a0_cmd in data:
		print("ACTUATOR STATE TEST\tPASSED\t\t", data.encode())
	else:
		print("ACTUATOR STATE TEST\tFAILED\t\t", data.encode())

def test_server_actuators_cfg():
	global server_actuators_socket, cfg

	data = "a0:?;"
	server_actuators_socket.send(data.encode())
	data = server_actuators_socket.recv(1024).decode()

	if "cfg" in data and a0_cfg in data:
		print("ACTUATOR CFG TEST\tPASSED\t\t", data.encode())
	else:
		print("ACTUATOR CFG TEST\tFAILED\t\t", data.encode())

def test_server_actuators():
	global server_actuators_socket

	TCP_IP = ""
	TCP_PORT = 1738
	server_actuators_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_actuators_socket.connect((TCP_IP, TCP_PORT))

	test_server_actuators_state()
	test_server_actuators_cfg()

	server_actuators_socket.close()

def test_server_ethernet():
	global server_ethernet_socket

	TCP_IP = ""
	TCP_PORT = 12345
	server_ethernet_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_ethernet_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_ethernet_socket.bind((TCP_IP, TCP_PORT))
	server_ethernet_socket.listen(15)

	conn, addr = server_ethernet_socket.accept()
	conn.settimeout(3)

	data_recv = conn.recv(1024).decode()

	data_send = "a0:" + a0_cmd
	conn.send(data_send.encode())
	conn.close()

	if "b0" in data_recv and "a0" in data_recv and "g0" in data_recv:
		print("ETHERNET TEST\t\tPASSED\t\t", data_recv.encode())
	else:
		print("ETHERNET TEST\t\tFAILED\t\t", data_recv.encode())

	server_ethernet_socket.close()

print("TEST\t\t\tRESULT\t\tDATA")
print("----\t\t\t------\t\t----")

test_server_ethernet()
test_server_actuators()
