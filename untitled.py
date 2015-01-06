#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2, cookielib
from xml.etree.ElementTree import Element, SubElement, tostring
from hashlib import md5
import json
from xml.dom import minidom
import datetime

my_password='xJ":vQ"&%`f!w@T/rixb@q,1l'
username = 'Toshyak'

user_input = None

my_password_md5 = md5(my_password)

shows_list = []

class Show(object):
	"""class for shows from myShows.ru"""
	def __init__(self, showId, title, watchStatus, watchedEpisodes, totalEpisodes):
		self.showId = showId
		self.title = title
		self.watchStatus = watchStatus
		self.watchedEpisodes = int(watchedEpisodes)
		self.totalEpisodes = int(totalEpisodes)
		self.ruTitle = None
		self.lastWatched = None

	def set_ruTitle(self, ruTitle):
		self.ruTitle = ruTitle

	def set_lastWatched(self, lastWatched):
		self.lastWatched = lastWatched

def open_connection():
	cj=cookielib.CookieJar()
	# print "http://api.myshows.ru/profile/login?login=%(login)s&password=%(passwd)s" % {"login" :username, "passwd": my_password_md5.hexdigest()}
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	auth = opener.open("http://api.myshows.ru/profile/login?login=%(login)s&password=%(passwd)s " % \
		{"login":username, "passwd": my_password_md5.hexdigest()} )

	# print auth.getcode() #надо бы его тоже возвращать

	return opener

def last_watched(connection, show):
	url = "http://api.myshows.ru/profile/shows/" + str(show.showId) + "/"
	episodes_json = json.load(connection.open(url))
	last_watched = datetime.datetime(1,1,1)
	for episode_id in episodes_json:
		episode_time = datetime.datetime.strptime(episodes_json[episode_id]["watchDate"], "%d.%m.%Y")
		if episode_time > last_watched:
			last_watched = episode_time
	return last_watched


def create_structure(connection):
	global shows_list
	shows_watching = []
	shows_not_watching = []
	shows_json = json.load(connection.open("http://api.myshows.ru/profile/shows/"))
	for show_id in shows_json:
		show = Show(shows_json[show_id]["showId"], shows_json[show_id]["title"], shows_json[show_id]["watchStatus"], 
			shows_json[show_id]["watchedEpisodes"], shows_json[show_id]["totalEpisodes"])
		if shows_json[show_id]["ruTitle"] != "NULL":
			show.set_ruTitle(shows_json[show_id]["ruTitle"])
		if shows_json[show_id]["watchStatus"] == 'watching':
			show.set_lastWatched(last_watched(connection, show))
			shows_watching.append(show)
		else:
			shows_not_watching.append(show)
		# shows_list.append(shows_json[show_id]["title"])
	shows_list = sorted(shows_watching, key = lambda show: show.lastWatched, reverse = True)
	for show in shows_not_watching:
		shows_list.append(show)

# for index, cookie in enumerate(cj):
#         print index, '  :  ', cookie

connection = open_connection()
create_structure(connection)
items = Element('items')
# user_input = "{query}"

# if user_input == "":
for show in shows_list:
	if show.watchStatus == "watching":
		item = SubElement(items, "item", {'arg': str(show.showId), "valid":"no", "autocomplete":show.title, "type":"default"})
		title = SubElement(item, "title")
		title.text = show.title
		subtitle = SubElement(item, "subtitle")
		if show.ruTitle == None:
			subtitle.text = show.lastWatched.strftime("%d.%m.%Y")
		else:
			subtitle.text = show.ruTitle + " " + show.lastWatched.strftime("%d.%m.%Y")
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