import n4d.responses

import NetworkManager as nm

import threading
import time
import dbus
import sys

class EscolesConectades:

	ERROR_NO_WIFI_DEV = -1

	def __init__(self):
		self.semaphore = threading.Semaphore(1)


	def scan_network(self):
		with self.semaphore:
			wifi = None
			for device in nm.Device.all():
				if (device.DeviceType == nm.NM_DEVICE_TYPE_WIFI):
					wifi = device
					break

			if (not wifi):
				return n4d.responses.build_failed_call_response(EscolesConectades.ERROR_NO_WIFI_DEV,"No wireless device available")
			try:
				wifi.RequestScan([])
			except Exception as e:
				#perhaps a scan is going on...
				time.sleep(2.0)

			aps = []
			for ap in wifi.AccessPoints:
				aps.append([ap.Ssid,ap.Strength])

			return n4d.responses.build_successful_call_response(aps)

	def create_connection(self,name,ssid,user,password):
		with self.semaphore:
			connection = {}
			connection["connection"] = {}
			connection["connection"]["id"] = name
			connection["connection"]["type"] = "802-11-wireless"
			connection["connection"]["permissions"] = ["user:{0}:".format(user)]
			#connection["connection"]["interface-name"] = "wlan0"

			connection["802-11-wireless"] = {}
			connection["802-11-wireless"]["ssid"] = dbus.ByteArray(bytes(ssid,'utf-8'))
			connection["802-11-wireless"]["mode"] = "infrastructure"

			connection["802-11-wireless-security"] = {}
			#connection["802-11-wireless-security"]["auth-alg"] = "open"
			connection["802-11-wireless-security"]["key-mgmt"] = "wpa-eap"
			#connection["802-11-wireless-security"]["psk"] = ""

			connection["802-1x"] = {}
			connection["802-1x"]["eap"] = ["peap"]
			connection["802-1x"]["identity"] = user
			connection["802-1x"]["password"] = password
			connection["802-1x"]["phase2-auth"] = "mschapv2"

			connection["ipv4"] = {}
			connection["ipv4"]["method"] = "auto"

			# This magic flag 0x02 renders connection volatile, so it will be destroyed on next boot
			tmp = nm.Settings.AddConnection2(connection,0x02,[])

			return n4d.responses.build_successful_call_response()

	def get_active_connections(self):
		with self.semaphore:
			connections=[]
			for connection in nm.NetworkManager.ActiveConnections:
				connections.append(connection.Id)

			return n4d.responses.build_successful_call_response(connections)

	def disconnect_all(self):
		with self.semaphore:

			for connection in nm.NetworkManager.ActiveConnections:
				nm.NetworkManager.DeactivateConnection(connection)
