import urllib2, cookielib
import hashlib

my_password='6$1KnH0xARI3VdI3=;6Q!h|r"'
username = 'Toshyak'

my_password_md5 = hashlib.md5(my_password)

# print "http://api.myshows.ru/profile/login?login=%(login)s&password=%(passwd)s" % {"login" :username, "passwd": my_password_md5.hexdigest()}
cj=cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
auth = opener.open("http://api.myshows.ru/profile/login?login=%(login)s&password=%(passwd)s " % \
	{"login":username, "passwd": my_password_md5.hexdigest()} )

print auth.getcode()

for index, cookie in enumerate(cj):
        print index, '  :  ', cookie

try:
	profile = urllib2.urlopen("http://api.myshows.ru/profile/ ")
except urllib2.HTTPError as err:
	print err


