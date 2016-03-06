#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2, cookielib
from xml.etree.ElementTree import Element, SubElement, tostring
from hashlib import md5
import json
from xml.dom import minidom
import datetime

#TODO список файлов для сериала, его сортировка, возврат отсортированных непросмотренных серий

user_input = ""
username = ""
password = ""
shows_list = []

class Show(object):
	"""class for shows from myShows.ru"""
	def __init__(self, id, title, watchStatus, watchedEpisodes, totalEpisodes):
		self.id = id
		self.title = title
		self.watchStatus = watchStatus
		self.watchedEpisodes = int(watchedEpisodes)
		self.totalEpisodes = int(totalEpisodes)
		self.ruTitle = None
		self.lastWatched = None
		self.seasons = []

	def set_ruTitle(self, ruTitle):
		self.ruTitle = ruTitle

	def set_lastWatched(self, lastWatched):
		self.lastWatched = lastWatched

# 	def addSeason(self, season):
# 		self.seasons.append(season)

# class Season(object):
# 	"""class for every Season"""
# 	def __init__(self, show):
# 		self.show = show
# 		show.addSeason(self)
		
class Episode(object):
	"""docstring for Episode"""
	def __init__(self, id, show, season, number, title, airDate):
		self.id = id
		self.show = show
		self.season = season
		self.number = number
		self.title = title
		self.airDate = airDate
		

def open_connection(login, password):
	md5_password = md5(password)
	cj=cookielib.CookieJar()
	# print "http://api.myshows.ru/profile/login?login=%(login)s&password=%(passwd)s" % {"login" :username, "passwd": my_password_md5.hexdigest()}
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	auth = opener.open("http://api.myshows.ru/profile/login?login=%(login)s&password=%(passwd)s " % \
		{"login":login, "passwd": md5_password.hexdigest()} )

	# print auth.getcode() #надо бы его тоже возвращать

	return opener

def last_watched(connection, show):
	url = "http://api.myshows.ru/profile/shows/" + str(show.id) + "/"
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

connection = open_connection(username, password)
create_structure(connection)
items = Element('items')
user_input = "{query}"
if user_input == "":
	for show in shows_list:
		if show.watchStatus == "watching":
			item = SubElement(items, "item", {'arg': str(show.id), "valid":"no", "autocomplete":show.title, "type":"default"})
			title = SubElement(item, "title")
			title.text = show.title
			subtitle = SubElement(item, "subtitle")
			if show.ruTitle == None:
				subtitle.text = show.lastWatched.strftime("%d.%m.%Y")
			else:
				subtitle.text = show.ruTitle + " " + show.lastWatched.strftime("%d.%m.%Y")
			icon = SubElement(item, "icon")
			icon.text = "myshows.ico"
else:
	for show in shows_list:
		if user_input.lower() == str(show.title.lower().encode("utf-8")):
			#введеное имя полностью совпадает с именем сериала - надо выводить самые старые непрсмотренные серии
			unwatched_episodes = []
			unwatched_json=json.load(connection.open("http://api.myshows.ru/profile/episodes/unwatched/"))
			for episode_id in unwatched_json:
				if unwatched_json[episode_id]["showId"]==show.id:
					unwatched_episodes.append(Episode(unwatched_json[episode_id]["episodeId"], show, unwatched_json[episode_id]["seasonNumber"], unwatched_json[episode_id]["episodeNumber"], unwatched_json[episode_id]["title"], datetime.datetime.strptime(unwatched_json[episode_id]["airDate"], "%d.%m.%Y")))

			unwatched_sorted = 	sorted(unwatched_episodes, key = lambda episode: episode.airDate, reverse=False)
			for episode in unwatched_sorted:
				item = SubElement(items, "item", {'arg': str(episode.id), "valid": "yes", "autocomplete":"s"+str(episode.season)+"e"+str(episode.number),"type":"default"})
				title = SubElement(item, "title")
				title.text = episode.title
				subtitle = SubElement(item, "subtitle")
				subtitle.text = "s" + str(episode.season)+"e"+str(episode.number)
				icon = SubElement(item, "icon")
				icon.text = "myshows.ico"
				cmd_subtitle = SubElement(item, "subtitle", {"mod": "cmd"})
				cmd_subtitle.text = "Mark as watched"
		elif (str(show.title.encode("utf-8")).lower().startswith(user_input.lower()) == True or user_input.lower() in str(show.title.encode("utf-8")).lower()) and show.watchStatus == "watching":
			item = SubElement(items, "item", {'arg': str(show.id), "valid":"no", "autocomplete":show.title, "type":"default"})
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