import n4d.responses

import NetworkManager as nm


class EscolesConectades:

	ERROR_NO_WIFI_DEV = -1

	def __init__(self):
		pass


	def scan_network(self):
		wifi = None
		for device in nm.Device.all():
			if (device.DeviceType == nm.NM_DEVICE_TYPE_WIFI):
				wifi = device
				break

		if (not wifi):
			return n4d.responses.build_failed_call_response(EscolesConectades.ERROR_NO_WIFI_DEV,"No wireless device available")

		wifi.RequestScan([])
		aps = []
		for ap in wifi.AccessPoints:
			aps.append([ap.Ssid,ap.Strength])

		return n4d.responses.build_successful_call_response(aps)
