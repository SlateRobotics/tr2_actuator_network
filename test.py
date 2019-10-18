#!/usr/bin/env python

import time
import socket

a0_state = 2.0
a0_cmd = "0,1,2,3,;"
a0_cfg = "0,4810,60,;"

server_ethernet_connection = None
server_ethernet_socket = None
server_actuators_socket = None

def test_server_actuators_state():
	global server_actuators_socket, cfg

	data = "a0:" + "{0:.6f}".format(a0_state) + ";" + a0_cfg
	server_actuators_socket.send(data.encode())
	data = server_actuators_socket.recv(4096).decode()

	if "cmd" in data and a0_cmd in data:
		print("ACTUATOR STATE TEST\tPASSED\t\t", data.encode())
		return True
	else:
		print("ACTUATOR STATE TEST\tFAILED\t\t", data.encode())
		return False

def test_server_actuators_cfg():
	global server_actuators_socket, cfg

	data = "a0:?;"
	server_actuators_socket.send(data.encode())
	data = server_actuators_socket.recv(409).decode()

	if data == "cfg:" + a0_cfg + ";\r\n":
		print("ACTUATOR CFG TEST\tPASSED\t\t", data.encode())
		return True
	else:
		print("ACTUATOR CFG TEST\tFAILED\t\t", data.encode())
		return False

def test_server_ethernet_cmd():
	global server_ethernet_socket, server_ethernet_connection

	data_send = "a0:" + a0_cmd
	server_ethernet_connection.send(data_send.encode())

	data_recv = server_ethernet_connection.recv(4096).decode()

	passed = True

	if ("ns;" in data_recv) or ("a0:" + "{0:.6f}".format(a0_state - 0.1) + ";" in data_recv):
		print("ETHERNET TEST\t\tPASSED\t\t", data_recv.encode())
		passed = True
	else:
		print("ETHERNET TEST\t\tFAILED\t\t", data_recv.encode())
		passed = False

	return passed

def test():
	global server_actuators_socket, server_ethernet_socket, server_ethernet_connection, a0_state, a0_cmd, a0_cfg

	server_ethernet_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_ethernet_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_ethernet_socket.bind(("", 12345))
	server_ethernet_socket.listen(2)

	server_ethernet_connection, addr = server_ethernet_socket.accept()
	server_ethernet_connection.settimeout(3)

	server_actuators_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_actuators_socket.connect(("", 1738))

	print("TEST\t\t\tRESULT\t\tDATA")
	print("----\t\t\t------\t\t----")

	passed = True

	test_len = 2
	for i in range(test_len):
		print(" > Round", i + 1)
		result_ec = test_server_ethernet_cmd()
		result_as = test_server_actuators_state()
		result_ac = test_server_actuators_cfg()
		print("")

		passed = passed and result_ec and result_as and result_ac

		a0_state = a0_state + 0.1
		a0_cmd = str(i + 1) + ",1,2,3,;"
		a0_cfg = str(i + 1) + ",4810,60,;"

	print("----\t\t\t------\t\t----")

	if passed == True:
		print(" > FINAL RESULT\t\tPASSED")
	else:
		print(" > FINAL RESULT\t\tFAILED")

	server_ethernet_connection.close()
	server_ethernet_socket.close()
	server_actuators_socket.close()

test()
