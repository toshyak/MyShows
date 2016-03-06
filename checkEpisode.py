#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2, cookielib
from hashlib import md5
import json
import sys

username = ""
password = ""

def open_connection(login, password):
	md5_password = md5(password)
	cj=cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	auth = opener.open("http://api.myshows.ru/profile/login?login=%(login)s&password=%(passwd)s " % \
		{"login":login, "passwd": md5_password.hexdigest()} )
	return opener

secure = open('key', 'r')
for line in secure:
	try:
		if line.startswith('username='):
			username=line[line.index("\'")+1:line.rindex("\'")]
		elif line.startswith('password='):
			password=line[line.index("\'")+1:line.rindex("\'")]
		elif line.startswith("#"):
			pass
		else:
			print ('Error! Cannot parse key file!')
	except Exception, e:
		raise e
secure.close()	

episode = "{query}"

connection = open_connection(username, password)
chech_episode = connection.open("http://api.myshows.ru/profile/episodes/check/" + episode)
if chech_episode.getcode() == 200:
	print "OK, episode marked as watched!"
else:
	print chech_episode.getcode()