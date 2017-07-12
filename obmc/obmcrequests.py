#!/usr/bin/python
#################################################################################
# * "THE BEER-WARE LICENSE" (Revision 42):
# * <austenc@us.ibm.com> wrote this file.  As long as you retain this notice you
# * can do whatever you want with this stuff. If we meet some day, and you think
# * this stuff is worth it, you can buy me a beer in return.   Chris Austen
#################################################################################
import requests
import pickle
import os
import json

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

################################################################
# This class will create a connection to the BMC ip
#  Currently it supports the get method.  It would make
#  sense to also support post/put when there comes a need
#
# Note this class supports cacheing.  Great for testing since
# you don't have to go back on to the system all the time.  A
# useful way to recreate with someone elses environment too
################################################################
class obmcConnection:
	def __init__(self, ip, uname, passwd, cache='', port=443):
		self.uname  = uname
		self.passwd = passwd
		self.ip     = ip + ':' + str(port)
		self.cache  = cache
		self.cookie = ''
		self.port   = port

		if self.cache == '':
			self.get_cookie()

	def __del__(self):
		if self.cookie != '':
			task = {"data": []}
			url  = 'https://' + self.ip + '/logout'
			r    = requests.post(url, json=task, verify=False)
			self.cookie = ''

	def get_cookie(self):
		if self.cookie == '':
			task = {"data": [self.uname, self.passwd]}
			url  = 'https://' + self.ip + '/login'
			r    = requests.post(url, json=task, verify=False)
			self.cookie = r.cookies
		return self.cookie
		
	def data(self):
		return self.response['data']

	def get(self, uri):
		# Example 9.x.x.x_org_openbmc_records_events_10.p
		t  = self.ip + uri + '.p'
		t  = t.replace('/','_')
		pf = self.cache + '/' + t

		if self.cache != '' and os.path.isfile(pf) == True:
			self.response = pickle.load( open( pf, "rb" ) )
		else:
			url = 'https://' + self.ip + uri
			cookie = self.get_cookie()

			r = requests.get(url, cookies=cookie, verify=False)
			self.response = r.json()
			print self.response

			if self.cache != '':
				pickle.dump( self.response, open( pf , "wb" ) )

		return self.response['message']

	def put(self, uri, parm):
		# Example 9.x.x.x_org_openbmc_records_events_10.p
		t  = self.ip + uri + '.p'
		t  = t.replace('/','_')
		pf = self.cache + '/' + t

		if self.cache != '' and os.path.isfile(pf) == True:
			self.response = pickle.load( open( pf, "rb" ) )
		else:
			url = 'https://' + self.ip + uri
			cookie = self.get_cookie()

			headers = {'content-Type' :'application/json'}
			putdata = json.dumps({'data' : parm})

			r = requests.put(url, cookies=cookie, data = putdata, headers=headers, verify=False)

			self.response = r.json()

			if self.cache != '':
				pickle.dump( self.response, open( pf , "wb" ) )

		return self.response['message']

	def post(self, uri, parmlist):
		# Example 9.x.x.x_org_openbmc_records_events_10.p
		t  = self.ip + uri + '.p'
		t  = t.replace('/','_')
		pf = self.cache + '/' + t

		if self.cache != '' and os.path.isfile(pf) == True:
			self.response = pickle.load( open( pf, "rb" ) )
		else:
			url      = 'https://' + self.ip + uri
			cookie   = self.get_cookie()
			headers  = {'content-Type' :'application/json'}
			postdata = json.dumps({'data' : parmlist})

			r = requests.post(url, cookies=cookie, data = postdata, headers=headers, verify=False)

			self.response = r.json()

			if self.cache != '':
				pickle.dump( self.response, open( pf , "wb" ) )

		return self.response['message']
