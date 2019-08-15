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

indexHtml = ''

numRoutes = 0
actuatorNames = []
routeNames = []
commands = []
commandsTS = []
commandsReceived = []
states = []
statesTS = []

def getNumRoutes():
	global numRoutes
	return numRoutes

def getRouteName(i):
	global routeNames
	return routeNames[i]

def setActuatorState (routeName, state):
	global numRoutes, actuatorNames, routeNames, commands, commandsTS, commandsReceived, states, statesTS
	for i in range(len(states)):
		if routeNames[i] == routeName:
			states[i] = state
			statesTS[i] = time.time()

def getActuatorState (routeName):
	global numRoutes, actuatorNames, routeNames, commands, commandsTS, commandsReceived, states, statesTS
	s = ''
	for i in range(numRoutes):
		if routeNames[i] == routeName:
			s = states[i] + ',' + str(stateTS[i])
	return s

def addRoute(actuatorName, routeName, cmd):
	global numRoutes, actuatorNames, routeNames, commands, commandsTS, commandsReceived, states, statesTS
	actuatorNames.append(actuatorName)
	routeNames.append(routeName)
	states.append('')
	statesTS.append(time.time())
	commands.append(cmd)
	commandsReceived.append(False)
	commandsTS.append(time.time())
	numRoutes += 1

def getRouteCommand(routeName):
	global numRoutes, actuatorNames, routeNames, commands, commandsTS, commandsReceived, states, statesTS
	for i in range(numRoutes):
		if routeNames[i] == routeName:
			cmd = commands[i]
			commands[i] = ''
			return cmd
	return ''

def editRouteCommand(routeName, cmd):
	global numRoutes, actuatorNames, routeNames, commands, commandsTS, commandsReceived, states, statesTS
	for i in range(numRoutes):
		if routeNames[i] == routeName:
			commands[i] = commands[i] + cmd
			commandsReceived[i] = False
			commandsTS[i] = time.time()

def setIndexHtml():
	global indexHtml, numRoutes, actuatorNames, routeNames, commands, commandsTS, commandsReceived, states, statesTS
	styleTABLE = "border:1px solid #ccc;border-collapse:collapse;";
	styleTR = "border:1px solid #ccc;";
	styleTH = "border:1px solid #ccc;padding:5px;";
	styleTD = "border:1px solid #ccc;padding:5px;"
	
	indexHtml = "";
	indexHtml += "<script>";
	indexHtml += "function handleFormSubmit () {";
	indexHtml += "	var type = document.getElementById('update_type').value;";
	indexHtml += "  var command = document.getElementById('command').value;";
	indexHtml += "  var actuatorid = document.getElementById('actuatorid').value;";
	indexHtml += "  var xhr = new XMLHttpRequest();";
	indexHtml += "  xhr.onreadystatechange = function () {";
	indexHtml += "      if (xhr.readyState == 4 && xhr.status == 200) {";
	indexHtml += "          window.location.reload();";
	indexHtml += "      }";
	indexHtml += "  };";
	indexHtml += "  xhr.open(\"POST\", \"/\" + type + \"/\" + actuatorid  + \"?c=\"+command+\"&a=\"+actuatorid, true);";
	indexHtml += "  xhr.send();";
	indexHtml += "}";
	indexHtml += "</script>";
	
	indexHtml += "<h2>TR2 Actuator Network State</h2>";
	indexHtml += "<p>This is the server in your TR2 that routes serial commands ";
	indexHtml += "from your robot's onboard computer to its various wireless actuators. ";
	indexHtml += "Actuators set their state using the \"s\" paramter in the url query by ";
	indexHtml += "setting it equal to the actuator's angle in radians when visiting the route. Actuators ";
	indexHtml += "request the latest commands from the main onboard computer by parsing the ";
	indexHtml += "response body using their respective route below.</p>";
	
	indexHtml += "<p>As an example, " + actuatorNames[0] + " requests it's latest command to be executed by visiting ";
	indexHtml += "<i>" + routeNames[0] + "</i>. It can simultaneously update the actuator's state to the main onboard computer ";
	indexHtml += "with the url <i>" + routeNames[0] + "?s=3.1415</i>, given a state of 3.1415 radians.</p>";
	
	indexHtml += "<table style=\"" + styleTABLE + "\">";
	indexHtml += "<tr style=\"" + styleTR + "\">";
	indexHtml += "<th style=\"" + styleTH + "\">Actuator</th>";
	indexHtml += "<th style=\"" + styleTH + "\">Route</th>";
	indexHtml += "<th style=\"" + styleTH + "\">Last Command</th>";
	indexHtml += "<th style=\"" + styleTH + "\">Last Command Updated (sec ago)</th>";
	indexHtml += "<th style=\"" + styleTH + "\">Last State</th>";
	indexHtml += "<th style=\"" + styleTH + "\">Last State Updated (sec ago)</th>";
	indexHtml += "</tr>";

	for i in range(numRoutes):
		commandTS = str(time.time() - commandsTS[i])
		stateTS = str(time.time() - statesTS[i])
		
		indexHtml += "<tr style=\"" + styleTR + "\">";
		indexHtml += "<td style=\"" + styleTD + "\">" + actuatorNames[i] + "</td>";
		indexHtml += "<td style=\"" + styleTD + "\">" + routeNames[i] + "</td>";
		indexHtml += "<td style=\"" + styleTD + "\">" + commands[i] + "</td>";
		indexHtml += "<td style=\"" + styleTD + "\">" + commandTS + "</td>";
		indexHtml += "<td style=\"" + styleTD + "\">" + states[i] + "</td>";
		indexHtml += "<td style=\"" + styleTD + "\">" + stateTS + "</td>";
		indexHtml += "</tr>";
	
	indexHtml += "</table>";
	
	indexHtml += "<div style=\"padding:5px;border-top:1px solid #ccc;margin-top:25px;\">";
	indexHtml += "<h3>Update command</h3>";
	indexHtml += "<span>Type: </span>";
	indexHtml += "<select id=\"update_type\"><option>cmd</option><option>cfg</option></select><br>"
	indexHtml += "<span>Actuator ID: </span>";
	indexHtml += "<input id=\"actuatorid\" type=\"text\" name=\"actuatorid\" value=\"\"><br>";
	indexHtml += "<span>New Command: </span>";
	indexHtml += "<input id=\"command\" type=\"text\" name=\"command\" value=\"\"><br>";
	indexHtml += "<input style=\"margin-top:15px\" type=\"button\" value=\"Send Command\" onclick=\"handleFormSubmit();\">";
	indexHtml += "</div>";

class RequestHandler(BaseHTTPRequestHandler):
	def setup(self):
		BaseHTTPRequestHandler.setup(self)
		self.request.settimeout(1)

	def do_POST(self):
		if self.path.startswith('/cfg'):
			c = parse.parse_qs(parse.urlparse(self.path).query).get('c', None)

			if c != None and len(c) > 0:
				c = c[0] + ';'
			else:
				c = ''


			act_id = self.path.split('/cfg/')[1].split('?')[0]
			f = open("/home/pi/tr2/ActuatorNetwork/cfg/" + act_id,"w")
			f.write(c)
			f.close()
			self.send_response(200)
			self.send_header('Content-type', 'text/plain')
			self.end_headers()

#			msg = "OK"
#			self.wfile.write(msg.encode("utf-8"))
		else:
			cmd = parse.parse_qs(parse.urlparse(self.path).query).get('c', None)
			act = parse.parse_qs(parse.urlparse(self.path).query).get('a', None)
			cfg = parse.parse_qs(parse.urlparse(self.path).query).get('a', None)

			if cmd != None and len(cmd) > 0:
				cmd = cmd[0] + ';'
			else:
				cmd = ''

			if act != None and len(act) > 0:
				act = act[0]
			else:
				act = ''

			if cfg != None and len(cfg) > 0:
				cfg = cfg[0]
			else:
				cfg = ''

			editRouteCommand("/cmd/" + act, cmd)
			self.send_response(200)
			self.send_header('Content-type', 'text/plain')
			self.end_headers()
#			msg = "OK"
#			self.wfile.write(msg.encode("UT))

	def do_GET(self):
		global indexHtml, numRoutes, actuatorNames, routeNames, commands, commandsTS, commandsReceived, states, statesTS
		if self.path == '/':
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()

			setIndexHtml()

			self.wfile.write(indexHtml.encode())
		elif self.path.startswith('/cfg'):
			act_id = self.path.split('/cfg/')[1].split('?')[0]
			f = open("/home/pi/tr2/ActuatorNetwork/cfg/" + act_id,"r+")
			cfg = f.read()
			f.close()

			self.send_response(200)
			self.send_header('Content-type','text/plain')
			self.end_headers()
			msg = "cfg:" + cfg
			self.wfile.write(msg.encode())
		else:
			state = parse.parse_qs(parse.urlparse(self.path).query).get('s', None)
			cfg = parse.parse_qs(parse.urlparse(self.path).query).get('cfg', None)

			if cfg != None and len(cfg) > 0:
				cfg = cfg[0] + ';'
				act_id = self.path.split('/cmd/')[1].split('?')[0]
				f = open("/home/pi/tr2/ActuatorNetwork/cfg/" + act_id,"w")
				f.write(cfg)
				f.close()

			if state != None and len(state) > 0:
				state = state[0]
				for i in range(numRoutes):
					if routeNames[i] in self.path:
						setActuatorState(routeNames[i], state)

			for i in range(numRoutes):
				if routeNames[i] in self.path:
					self.send_response(200)
					self.send_header('Content-type','text/plain')
					self.end_headers()
					msg = "cmd:nc;"
					if commandsReceived[i] == False:
						msg = "cmd:" + getRouteCommand(routeNames[i])
						print("REQ -> " + msg)
						commandsReceived[i] = True
					self.wfile.write(msg.encode())

addRoute("Base", "/cmd/b0", "nc;")
addRoute("Arm Actuator 0", "/cmd/a0", "nc;")
addRoute("Arm Actuator 1", "/cmd/a1", "nc;")
addRoute("Arm Actuator 2", "/cmd/a2", "nc;")
addRoute("Arm Actuator 3", "/cmd/a3", "nc;")
addRoute("Arm Actuator 4", "/cmd/a4", "nc;")
addRoute("Gripper Actuator 0", "/cmd/g0", "nc;")
addRoute("Head Actuator Pan", "/cmd/h0", "nc;")
addRoute("Head Actuator Tilt", "/cmd/h1", "nc;")
addRoute("Sensor: Battery Voltage", "/cmd/s0", "nc;")

def handle_tx2():
	while True:
		try:
			tx2 = socket.socket()
			tx2.settimeout(2)
			tx2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

			connected = False
			print("Waiting for connection on 192.168.77.1:12345")
			while connected == False:
				try:
					tx2.connect(('192.168.77.1',12345))
					connected = True
				except:
					pass

			print("Got connection from TX2")

			while True:
				_states = ""
				for i in range(getNumRoutes()):
					aid = getRouteName(i).split("/cmd/")[1]
					state = states[i]
					_states = _states + aid + ":" +  state + ";"
				_states = _states + ";"

				if _states == "":
					_states = "ns;"

				tx2.send(_states.encode())

				res = tx2.recv(4096).decode()
				#if res != "nc;":
					#print(" <- " + res)
				cmds = res.split(';')
				for c in cmds:
					if c and len(c.split(':')) > 1:
						id = c.split(':')[0]
						cmd = c.split(':')[1] + ';'
						editRouteCommand("/cmd/"+id,cmd)
#			tx2.close()
		except Exception as e:
			print(e)
			print('restarting thread')
		else:
			print('exited normally, bad thread; restarting')

t = threading.Thread(target=handle_tx2, args=())
t.daemon = True
t.start()

def actuatorNetwork():
	actuatorNetworkServer = socketserver.TCPServer(("", 80), RequestHandler)

	print("serving at port 80")

	try:
		actuatorNetworkServer.serve_forever()
	except KeyboardInterrupt:
		pass
	except:
		pass

	#actuatorNetworkServer.socket.close()
	#actuatorNetworkServer.shutdown()
	#actuatorNetworkServer.server_close()

#actuatorNetwork()

#print_lock = threading.Lock()

def threaded(c):
	global routeNames, numRoutes, _cmd
	while True:
		try:
			data = c.recv(1024).decode()
			#print(" <- " + data)
			if not data:
				#print_lock.release()
				break

			aid = data.split(':')[0]

			# return cfg if needed
			if data.split(':')[1].split(';')[0] == '?':
				f = open("/home/pi/tr2/ActuatorNetwork/cfg/" + aid, 'r')
				cfg = f.read()
				f.close()

				cfg = cfg.replace('\r','').replace('\n','')

				msg = "cfg:" + cfg + ";\r\n"
				#print(" -> " + msg)
				c.send(msg.encode())
			else:
				state = data.split(':')[1].split(';')[0]
				setActuatorState("/cmd/" + aid, state)

				# update cfg if needed
				if len(data.split(':')[1].split(';')) > 1:
					cfg = data.split(':')[1].split(';')[1]
					if len(cfg.split(',')) == 4:
						f = open("/home/pi/tr2/ActuatorNetwork/cfg/" + aid, 'w')
						f.write(cfg + ";")
						f.close()

				# get and send cmd
				msg = "cmd:nc;"
				for i in range(numRoutes):
					if aid in routeNames[i]:
						cmd = getRouteCommand("/cmd/" + aid)
						if cmd != "":
							msg = "cmd:" + cmd
							commandsReceived[i] = True
				msg = msg + ";\r\n"
				if aid == "a4" and msg != "cmd:nc;;\r\n":
					print(" -> " + msg)
				c.send(msg.encode())
		except Exception as e:
			print(e)
			print('{!r}; exiting thread'.format(e))
			break
			#print_lock.release()
			#c.close()
	c.close()
	#print_lock.release()

def tcpServer():
	while True:
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			s.bind(("", 1738))
			s.listen(15)

			while True:
				c, addr = s.accept()
				c.settimeout(3)
				#print_lock.acquire()
				print('Connected to :', addr[0], ':', addr[1])
				start_new_thread(threaded, (c,))
			s.close()
		except Exception as e:
			print(e)
			print('{!r}; restarting thread'.format(e))

t2 = threading.Thread(target=tcpServer, args=())
t2.daemon = True
t2.start()

actuatorNetwork()
