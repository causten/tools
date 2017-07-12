#!/usr/bin/python
import sys
import getpass
import getopt
import obmcrequests
#################################################################################
#  "THE BEER-WARE LICENSE" (Revision 42):
#  <austenc@us.ibm.com> wrote this file.  As long as you retain this notice you
#  can do whatever you want with this stuff. If we meet some day, and you think
#  this stuff is worth it, you can buy me a beer in return.   Chris Austen
#################################################################################

leduri = '/xyz/openbmc_project/led/groups/'

class ledGroups:
	def __init__(self, connection):
		self.connection = connection
		self.refresh_groups()

	def refresh_groups(self):
		self.connection.get(leduri)
		self.db = []
		groups = self.connection.data()
		for uri in groups:
			self.connection.get(uri)
			self.connection.data()
			self.addRec(uri, self.connection.data()['Asserted'])

	def addRec(self, name, state):
		short = name.split(leduri)[1]
		self.db.append([short, state])

	def ledList(self):
		return self.db

	def getName(self, index):
		return self.db[index][0]

	def keys(self):
		return self.db.keys()

	def toggleAssert(self, index):
		s = leduri + self.db[index][0] + '/attr/Asserted'
		val = 0

		if self.db[index][1] == 0:
			val = 1

		self.connection.put(s, val)
		return



def toggleAssert(el, option):
	print 'Attempting to toggle'
	el.toggleAssert(option)
	el.refresh_groups()
	return


def displayLedMenu(el):
	
	print
	print '============================================================================'
	print '{0:^5} {1:20}  {2:1}'.format('LED#', 'LED','State')


	for i, data in enumerate(el.ledList()):
		print '{0:^5} {1:20}  {2:1}'.format(i, data[0], data[1])

	print '--------------------------------------------------------'
	s =   'Options: # (Toggle Assert),  q (quit)  >> '
	response = raw_input(s)

	return response


def runtool(ip, uname, pswd, cache, port=443):

	e  = obmcrequests.obmcConnection(ip, uname, pswd, cache, port)
	el = ledGroups(e)
	
	option = ''
	
	while option != 'q':
	
		option = displayLedMenu(el)

		try:
			val = int(option)
			if val < len(el.ledList()):
				toggleAssert(el, val)

		except:
			pass 



def usage(name):
	print 'Usage: Version 0.1'  
	print name, '[-i] [-u] <-p> <-c dir>'
	print '\t-i | --ip=        : IP / Hostname of the target BMC'
	print '\t-p | --port=      : user name for REST interaction'
	print '\t-c | --cachedir=  : Cache REST interaction directory'


def main(argv):

	cache  = ''
	port 	= '443'
	ip 		= ''
	uname 	= ''


	try:
		opts, args = getopt.getopt(argv[1:],"hc:d:u:p:i:",["ip=","port=","cachedir"])
	except getopt.GetoptError:
		usage(argv[:1])
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			usage(argv[:1])
			sys.exit()
		elif opt in ("-i", "--ip"):
			ip = arg
		elif opt in ("-p", "--port"):
			port = arg
		elif opt in ("-c", "--cachedir"):
			cache = arg

	if '' == ip:
		print ("Error, ip required")
		sys.exit(3)

	runtool(ip, 'root', '0penBmc', cache, port)

if __name__ == "__main__":
	main(sys.argv)