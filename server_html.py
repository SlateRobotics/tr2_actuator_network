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

class request_handler(BaseHTTPRequestHandler):
	state = None
	indexHtml = ''

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
			self.state.updateConfig(act_id, c)

			self.send_response(200)
			self.send_header('Content-type', 'text/plain')
			self.end_headers()

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

			self.state.editRouteCommand("/cmd/" + act, cmd)
			self.send_response(200)
			self.send_header('Content-type', 'text/plain')
			self.end_headers()

	def do_GET(self):
		if self.path == '/':
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()

			self.setIndexHtml()

			self.wfile.write(self.indexHtml.encode())
		elif self.path.startswith('/cfg'):
			act_id = self.path.split('/cfg/')[1].split('?')[0]
			cfg = self.state.readConfig(act_id)

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
				self.state.updateConfig(act_id, cfg)

			if state != None and len(state) > 0:
				state = state[0]
				for i in range(self.state.numRoutes):
					if self.state.routeNames[i] in self.path:
						self.state.setActuatorState(self.state.routeNames[i], state)

			for i in range(self.state.numRoutes):
				if self.state.routeNames[i] in self.path:
					self.send_response(200)
					self.send_header('Content-type','text/plain')
					self.end_headers()
					msg = "cmd:nc;"
					if self.state.commandsReceived[i] == False:
						msg = "cmd:" + self.getRouteCommand(self.state.routeNames[i])
						print("HTML    : REQ -> " + msg)
						self.state.commandsReceived[i] = True
					self.wfile.write(msg.encode())



	def setIndexHtml(self):
		styleTABLE = "border:1px solid #ccc;border-collapse:collapse;";
		styleTR = "border:1px solid #ccc;";
		styleTH = "border:1px solid #ccc;padding:5px;";
		styleTD = "border:1px solid #ccc;padding:5px;"

		self.indexHtml = "";
		self.indexHtml += "<script>";
		self.indexHtml += "function handleFormSubmit () {";
		self.indexHtml += "	var type = document.getElementById('update_type').value;";
		self.indexHtml += "  var command = document.getElementById('command').value;";
		self.indexHtml += "  var actuatorid = document.getElementById('actuatorid').value;";
		self.indexHtml += "  var xhr = new XMLHttpRequest();";
		self.indexHtml += "  xhr.onreadystatechange = function () {";
		self.indexHtml += "	  if (xhr.readyState == 4 && xhr.status == 200) {";
		self.indexHtml += "		  window.location.reload();";
		self.indexHtml += "	  }";
		self.indexHtml += "  };";
		self.indexHtml += "  xhr.open(\"POST\", \"/\" + type + \"/\" + actuatorid  + \"?c=\"+command+\"&a=\"+actuatorid, true);";
		self.indexHtml += "  xhr.send();";
		self.indexHtml += "}";
		self.indexHtml += "</script>";

		self.indexHtml += "<h2>TR2 Actuator Network State</h2>";
		self.indexHtml += "<p>This is the server in your TR2 that routes serial commands ";
		self.indexHtml += "from your robot's onboard computer to its various wireless actuators. ";
		self.indexHtml += "Actuators set their state using the \"s\" paramter in the url query by ";
		self.indexHtml += "setting it equal to the actuator's angle in radians when visiting the route. Actuators ";
		self.indexHtml += "request the latest commands from the main onboard computer by parsing the ";
		self.indexHtml += "response body using their respective route below.</p>";

		self.indexHtml += "<p>As an example, " + self.state.actuatorNames[0] + " requests it's latest command to be executed by visiting ";
		self.indexHtml += "<i>" + self.state.routeNames[0] + "</i>. It can simultaneously update the actuator's state to the main onboard computer ";
		self.indexHtml += "with the url <i>" + self.state.routeNames[0] + "?s=3.1415</i>, given a state of 3.1415 radians.</p>";

		self.indexHtml += "<table style=\"" + styleTABLE + "\">";
		self.indexHtml += "<tr style=\"" + styleTR + "\">";
		self.indexHtml += "<th style=\"" + styleTH + "\">Actuator</th>";
		self.indexHtml += "<th style=\"" + styleTH + "\">Route</th>";
		self.indexHtml += "<th style=\"" + styleTH + "\">Last Command</th>";
		self.indexHtml += "<th style=\"" + styleTH + "\">Last Command Updated (sec ago)</th>";
		self.indexHtml += "<th style=\"" + styleTH + "\">Last State</th>";
		self.indexHtml += "<th style=\"" + styleTH + "\">Last State Updated (sec ago)</th>";
		self.indexHtml += "</tr>";

		for i in range(self.state.numRoutes):
			commandTS = str(time.time() - self.state.commandsTS[i])
			stateTS = str(time.time() - self.state.statesTS[i])

			self.indexHtml += "<tr style=\"" + styleTR + "\">";
			self.indexHtml += "<td style=\"" + styleTD + "\">" + self.state.actuatorNames[i] + "</td>";
			self.indexHtml += "<td style=\"" + styleTD + "\">" + self.state.routeNames[i] + "</td>";
			self.indexHtml += "<td style=\"" + styleTD + "\">" + self.state.commands[i] + "</td>";
			self.indexHtml += "<td style=\"" + styleTD + "\">" + commandTS + "</td>";
			self.indexHtml += "<td style=\"" + styleTD + "\">" + self.state.states[i] + "</td>";
			self.indexHtml += "<td style=\"" + styleTD + "\">" + stateTS + "</td>";
			self.indexHtml += "</tr>";

		self.indexHtml += "</table>";

		self.indexHtml += "<div style=\"padding:5px;border-top:1px solid #ccc;margin-top:25px;\">";
		self.indexHtml += "<h3>Update command</h3>";
		self.indexHtml += "<span>Type: </span>";
		self.indexHtml += "<select id=\"update_type\"><option>cmd</option><option>cfg</option></select><br>"
		self.indexHtml += "<span>Actuator ID: </span>";
		self.indexHtml += "<input id=\"actuatorid\" type=\"text\" name=\"actuatorid\" value=\"\"><br>";
		self.indexHtml += "<span>New Command: </span>";
		self.indexHtml += "<input id=\"command\" type=\"text\" name=\"command\" value=\"\"><br>";
		self.indexHtml += "<input style=\"margin-top:15px\" type=\"button\" value=\"Send Command\" onclick=\"handleFormSubmit();\">";
		self.indexHtml += "</div>";

class server_html:
	state = None

	def __init__(self, s):
		self.state = s
		request_handler.state = s
		self.run()

	def run(self):
		actuatorNetworkServer = socketserver.TCPServer(("", 80), request_handler)

		try:
			print("HTML    : serving at port 80")
			actuatorNetworkServer.serve_forever()
		except KeyboardInterrupt:
			pass
		except:
			pass
