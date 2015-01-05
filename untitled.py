#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2, cookielib
from xml.etree.ElementTree import Element, SubElement, tostring
from hashlib import md5
import json
from xml.dom import minidom

my_password='xJ":vQ"&%`f!w@T/rixb@q,1l'
username = 'Toshyak'

my_password_md5 = md5(my_password)

def open_connection():
	cj=cookielib.CookieJar()
	# print "http://api.myshows.ru/profile/login?login=%(login)s&password=%(passwd)s" % {"login" :username, "passwd": my_password_md5.hexdigest()}
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	auth = opener.open("http://api.myshows.ru/profile/login?login=%(login)s&password=%(passwd)s " % \
		{"login":username, "passwd": my_password_md5.hexdigest()} )

	# print auth.getcode() #надо бы его тоже возвращать

	return opener

def shows_list(connection):
	try:
		shows = connection.open("http://api.myshows.ru/profile/shows/")
	except urllib2.HTTPError as err:
		print err

	shows_list = []
	shows_json = json.load(shows)
	for show_id in shows_json:
		shows_list.append(shows_json[show_id]["title"])
	return shows_list


# for index, cookie in enumerate(cj):
#         print index, '  :  ', cookie

connection = open_connection()
items = Element('items')
for i in shows_list(connection):
	item = SubElement(items, "item", {'arg': i, "valid":"no", "autocomplete":i, "type":"default"})
	title = SubElement(item, "title")
	title.text = i
	subtitle = SubElement(item, "subtitle")
	subtitle.text = i
	icon = SubElement(item, "icon")
	icon.text = "myshows.ico"

print tostring(items, 'utf-8') 


# print """
# <?xml version="1.0"?>
#     <items>
#         <item arg="The Simpsons" valid="no" autocomplete="The Simpsons" type="default">
#             <title>The Simpsons</title>
#             <subtitle>Симпсоны</subtitle>
#             <icon type="fileicon">~/Desktop</icon>
#         </item>
#         <item arg="Futurama" valid="no" autocomplete="Futurama" type="default">
#             <title>Futurama</title>
#             <subtitle>Футурама</subtitle>
#             <icon type="fileicon">~/Desktop</icon>
#         </item>
#     </items>
# """

