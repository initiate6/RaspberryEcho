#! /usr/bin/env python

import cherrypy
import os
from cherrypy.process import servers
import requests
import json
#from creds import *
import urllib
import argparse
import ConfigParser
import netifaces

class Start(object):

	def __init__(self, cfg):
		self.cfg = cfg
		self.urls = ["https://www.amazon.com/ap/oa", "https://api.amazon.com/auth/o2/token"]
		self.callback = cherrypy.url()  + "/code"
		self.scope="alexa_all"
		self.sd = json.dumps({
		    "alexa:all": {
		        "productID": cfg['product_id'],
		        "productInstanceAttributes": {
		            "deviceSerialNumber": "001"
		        }
		    }
		})
		self.payload = {"client_id" : cfg['client_id'], "scope" : "alexa:all", "scope_data" : self.sd, "response_type" : "code", "redirect_uri" : self.callback }

	@cherrypy.expose
	def index(self):
		req = requests.Request('GET', self.urls[0], params=self.payload)
		p = req.prepare()
		raise cherrypy.HTTPRedirect(p.url)

	@cherrypy.expose
	def code(self, var=None, **params):
		code = urllib.quote(cherrypy.request.params['code'])
		callback = cherrypy.url()
		payload = {"client_id" : cfg['client_id'], "client_secret" : cfg['client_secret'], "code" : code, "grant_type" : "authorization_code", "redirect_uri" : callback }

		r = requests.post(self.urls[1], data=payload)
		resp = r.json()
		print(resp)

		update_token(cfg['config_file'], resp['refresh_token'])

		return "Success!, refresh token has been added to your %s file, you may now reboot the Pi <br>" % (cfg['config_file'])

def update_token(config_file, token):

	config = ConfigParser.RawConfigParser()
	config.read(config_file)

	if not config.has_section('TOKEN'):
		config.add_section('TOKEN')

	config.set('TOKEN', 'refresh_token', token)
	with open(config_file, 'w') as configfile:
		config.write(configfile)

def parse_config(cfg):
	ret = {}

	try:
		config = ConfigParser.ConfigParser()
		fp = open(cfg)
		config.readfp(fp)

		ret['product_id'] = config.get("SETTINGS", "ProductID")
		ret['security_profile_desc'] = config.get("SETTINGS", "Security_Profile_Description")
		ret['security_profile_id'] = config.get("SETTINGS", "Security_Profile_ID")
		ret['client_id'] = config.get("SETTINGS", "Client_ID")
		ret['client_secret'] = config.get("SETTINGS", "Client_Secret")

		ret['port'] = config.getint("CHERRY", "port")
		ret['host'] = config.get("CHERRY", "host")

	except Exception as e:
		print("Failed to parse config %s: Error: %s" % ( cfg, e ) )
		sys.exit()

	return ret

def setup(config_file):
	config = ConfigParser.RawConfigParser()
	#config.read("echo.cfg")

	if not config.has_section('SETTINGS'):
		config.add_section('SETTINGS')

	if not config.has_section('CHERRY'):
		config.add_section('CHERRY')

	product_id = raw_input("Please enter your ProductID: ")
	sec_profile_desc = raw_input("Please enter your Security Profile Description: ")
	sec_profile_id = raw_input("Please enter your Security Profile ID: ")
	client_id = raw_input("Please enter your Security Client ID: ")
	client_secret = raw_input("Please enter your Security Client Secret: ")
	print('The following are the current IP address setup: ')
	interfaces = netifaces.interfaces()
	for i in interfaces:
	    if i == 'lo':
	        continue
	    iface = netifaces.ifaddresses(i).get(netifaces.AF_INET)
	    if iface != None:
	        for j in iface:
	            print('IP Address: %s\n' % (j['addr']) )

	ip = raw_input("Please enter the IP address you would like to use: ")
	port = int(raw_input("Please enter the port number you would like to use: "))

	config.set('SETTINGS', 'productid', product_id)
	config.set('SETTINGS', 'security_profile_description', sec_profile_desc)
	config.set('SETTINGS', 'security_profile_id', sec_profile_id)
	config.set('SETTINGS', 'client_id', client_id)
	config.set('SETTINGS', 'client_secret', client_secret)

	config.set('CHERRY', 'host', ip)
	config.set('CHERRY', 'port', port)

	with open(config_file, 'w') as configfile:
		config.write(configfile)

if __name__ == '__main__':

	config_file = 'echo.cfg'
	parser = argparse.ArgumentParser(description="Auth web Service",epilog=None)
	parser.add_argument("-c","--config",help="Configuration file",type=str,required=False)
	parser.add_argument("-n","--new",help="Create new config file",action="store_true",required=False)

	opt = parser.parse_args()

	if not opt.config:
		opt.config = config_file

	if not os.path.isfile(config_file) or opt.new:
		setup(config_file)

	try:
		cfg = parse_config(opt.config)
		cfg['config_file'] = config_file

	except Exception as e:
		print(e)

	try:
		if not os.path.isfile('vlc.py'):
			r = requests.get("http://git.videolan.org/?p=vlc/bindings/python.git;a=blob_plain;f=generated/vlc.py;hb=HEAD")
			if r.status_code == 200:
				with open('vlc.py', 'wb') as f:
					f.write(r.content)
			else:
				raise

	except Exception as e:
		print("Unable to download vlc.py. Error: %s" % (e))

	try:
		cherrypy.config.update({'server.socket_host': cfg['host'],
								'server.socket_port': cfg['port'],
		})
		cherrypy.quickstart(Start(cfg))

	except Exception as e:
		print(e)
