#!/usr/bin/python
#################################################################################
# * "THE BEER-WARE LICENSE" (Revision 42):
# * <austenc@us.ibm.com> wrote this file.  As long as you retain this notice you
# * can do whatever you want with this stuff. If we meet some day, and you think
# * this stuff is worth it, you can buy me a beer in return.   Chris Austen
#################################################################################
import sys
import getpass
import getopt
import errlparser
import obmcrequests
import datetime

loguri = '/xyz/openbmc_project/logging/entry/'

#############################################
# Copied the hexdump function from....
# https://gist.github.com/7h3rAm/5603718
#############################################
def hexdump(src, length=16, sep='.'):
	FILTER = ''.join([(len(repr(chr(x))) == 3) and chr(x) or sep for x in range(256)])

	lines = []
	for c in xrange(0, len(src), length):
		chars = src[c:c+length]

		hex = ' '.join(["%02x" % x for x in chars])
		if len(hex) > 24:
			hex = "%s %s" % (hex[:24], hex[24:])
		printable = ''.join(["%s" % ((x <= 127 and FILTER[x]) or sep) for x in chars])
		lines.append("%08x:  %-*s  |%s|\n" % (c, length*3, hex, printable))
	print ''.join(lines)


#################################################################
# Create a dictionary of all event logs
#################################################################
class eventLogDB:
	def __init__(self, connection):
		self.db = {}
		print loguri
		r = connection.get(loguri)
		print r
		if r == '200 OK':
			print 'logs were found'
			events = connection.data()
		else:
			sys.exit(0)

		for i in events:
			print i
			connection.get(i)
			self.addRec(i, connection.data())

	def addRec(self, rec, data):
		self.db[rec] = data

	def delRec(self, num):
		uri = loguri + num
		if uri in self.db: del self.db[uri]

		
	def recExists(self, num):
		uri = loguri + num

		if uri in self.db.keys():
			return True
		else :
			return False

	def keys(self):
		return self.db.keys()


#################################################################
# Additional Data is a string of bytes converted to ascii.  So
# it is like ... 00 00 df 00 00 00 00 20 00 04 07 5a
# This function will try to interpet
# I'd like this part to get enhanced to try to analyize
# In the mean time a hex dump makes it look good
#################################################################
def displayEsel(s):

	tok = s.split()
	bytelist = [0]

	print 'ESEL Data:'

	for k, v in enumerate(tok):
		bytelist.append(int(v,16))

	hexdump(bytelist)

	return


def displayRecordDetails(eldb, num):
	uri = loguri + num

	if eldb.db[uri]['Resolved'] == 0:
		resolved = 'False'
	else:
		resolved = 'True'

	x =  int(eldb.db[uri]['Timestamp'])/1000
	ts = datetime.datetime.utcfromtimestamp(x)

	print '================================================'
	print 'Event Log     ', uri
	print 'Message:      ', eldb.db[uri]['Message']
	print 'Time:         ', ts.isoformat(' ')
	print 'Severity:     ', eldb.db[uri]['Severity']
	print 'Resolved:     ', resolved
	print 'Associations: '

	for i in eldb.db[uri]['associations']:
		print '              ', i

	print 'AdditionalData: '

	for i in eldb.db[uri]['AdditionalData']:
		if 'ESEL=' in i:
			displayEsel(i[5:])
		else:
			print '              ', i


def displayDetailMenu(eldb, num):

	option = ''
	while option != 'q': 
		displayRecordDetails(eldb, num)
		
		print '-----------------------------------'
		s =  'Options: d (delete), q (back) >> '
		option = raw_input(s)
		

		if option == 'd':
			print 'wanted to delete'
			eldb.delRec(num)
			option = 'q'


def displayRecordsMenu(eldb):

	lines = {}
	print
	print '============================================================================'
	print '{0:4}  {1:12}  {2:20}  {3}'.format('Log#', 'Severity','Date','Message')

	for i in eldb.db:
		num = i.replace(loguri,'')
		sev = eldb.db[i]['Severity'].replace('xyz.openbmc_project.Logging.Entry.Level.','')
		ts =  datetime.datetime.utcfromtimestamp(int (eldb.db[i]['Timestamp'])/1000)

		lines[eldb.db[i]['Timestamp']] = '{0:4}  {1:12}  {2:20}  {3}'. \
			format(num, sev, ts.isoformat(' ') ,eldb.db[i]['Message'])

	for k, v in sorted(lines.iteritems()):
		print v


	print '--------------------------------------------------------'
	s =   'Options: # (details),  a (All details), q (quit)  >> '
	response = raw_input(s)

	return response


def runtool(ip, uname, pswd, cache):

	e  = obmcrequests.obmcConnection(ip, uname, pswd, cache)
	el = eventLogDB(e)
	
	option = ''
	
	while option != 'q':
	
		option = displayRecordsMenu(el)

		if option == 'a':
			for i in el.keys():
				s = i.replace(loguri, '')
				displayRecordDetails(el, s)

		if el.recExists(option):
			displayDetailMenu(el, option)


def usage(name):

	print 'Usage: Version 0.2'  
	print name, '[-i] [-u] <-p> <-c dir>'
	print '\t-i | --ip=        : IP / Hostname of the target BMC'
	print '\t-u | --user=      : user name for REST interaction'
	print '\t-p | --password=  : password for REST interaction'
	print '\t-c | --cachedir=  : Cache REST interaction directory'


def main(argv):

	cache  = ''
	port 	= '443'
	ip 		= ''

	try:
		opts, args = getopt.getopt(argv[1:],"hc:d:u:p:i:",["ip=","user=","password=","cachedir"])
	except getopt.GetoptError:
		usage(argv[0])
		sys.exit(2)

	for opt, arg in opts:

		if opt == '-h':
			usage(argv[0])
			sys.exit()

		elif opt in ("-i", "--ip"):

			# Passing in a port needs to be split out
			ip_port = arg.split(':')
			ip = ip_port[0]
			if len(ip_port) > 1:
				port = ip_port[1]

		elif opt in ("-u", "--user"):
			uname = arg
		elif opt in ("-p", "--password"):
			pswd = arg
		elif opt in ("-c", "--cachedir"):
			cache = arg

	if ip == '' or uname == '':
		usage(argv[0])
		print 'ERROR: ip and user parmeters are required'
		sys.exit(2)

	if pswd == '':
		pswd = getpass.getpass('Password:')


	# Here is where the magic happens
	runtool(ip, uname, paswd, cache, port)


if __name__ == "__main__":
   main(sys.argv)
