import urllib2
import hashlib

my_password='6$1KnH0xARI3VdI3=;6Q!h|r"'
username = 'Toshyak'

my_password_md5 = hashlib.md5(my_password)

print "http://api.myshows.ru/profile/login?login=%(login)s&password=%(passwd)s" % {"login" :username, "passwd": my_password_md5.hexdigest()}
auth = urllib2.urlopen("http://api.myshows.ru/profile/login?login=%(login)s&password=%(passwd)s " % \
	{"login":username, "passwd": my_password_md5.hexdigest()} )

print auth.code
try:
	profile = urllib2.urlopen("http://api.myshows.ru/profile/ ")
except urllib2.HTTPError as err:
	print err


