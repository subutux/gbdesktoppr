#{u'palette':
#[u'2E3945', u'2E3945', u'A4ABAA', u'A4ABAA', u'B24E3C', u'B34E3C', u'E9BF37', u'E9BF38', u'F4F3E4', u'F4F3E4'],
# u'user_count': 15,
# u'uploader': u'chigusan',
# u'url': u'https://www.desktoppr.co/wallpapers/233651',
# u'created_at': u'2013-01-19T05:50:19.380Z',
# u'bytes': 343517,
# u'height': 1200,
# u'width': 1920,
# u'image': {u'url': u'http://a.desktopprassets.com/wallpapers/0b1837ca91c07695a6afd6f7d10fe2ee09984ff2/x2wurqx.jpg',
# 	u'preview': {u'url': u'http://a.desktopprassets.com/wallpapers/0b1837ca91c07695a6afd6f7d10fe2ee09984ff2/preview_x2wurqx.jpg',
# 		u'width': 960,
# 		u'height': 600},
# 	u'thumb': {u'url': u'http://a.desktopprassets.com/wallpapers/0b1837ca91c07695a6afd6f7d10fe2ee09984ff2/thumb_x2wurqx.jpg',
# 		u'width': 296,
# 		u'height': 185}
# },
# u'review_state': u'safe',
# u'id': 233651,
# u'likes_count': 0
# }
#

import urllib2
try:
	import json
except ImportError:
	import simplejson
class wallpaper(object):
	"""
	A class to contain a wallpaper object, python-style
	"""
	def __init__(self,wpObj):
		self.obj = wpObj
	def palette(self):
		return self.obj['palette']
	def user_count(self):
		return self.obj['user_count']
	def uploader(self):
		return self.obj['uploader']
	def url(self):
		return self.obj['url']
	def created_at(self):
		return self.obj['created_at']
	def bytes(self):
		return self.obj['bytes']
	def width(self):
		return self.obj['width']
	def height(self):
		return self.obj['height']
	def review_state(self):
		return self.obj['review_state']
	def id(self):
		return self.obj['id']
	def likes(self):
		return self.obj['likes_count']
	def image_url(self):
		return self.obj['image']['url']
	def image_preview(self):
		return self.obj['image']['preview']
	def image_thumb(self):
		return self.obj['image']['thumb']
class user(object):
	"""
	a class containing a desktoppr user
	"""
	def __init__(self,userObj,api):
		self.obj = userObj
		self.api = api
	def username(self):
		return self.obj['username']
	def name(self):
		return self.obj['name']
	def avatar_url(self):
		return self.obj['avatar_url']
	def wallpapers_count(self):
		return self.obj['wallpapers_count']
	def uploaded_count(self):
		return self.obj['uploaded_count']
	def followers_count(self):
		return self.obj['followers_count']
	def following_count(self):
		return self.obj['following_count']
	def created_at(self):
		return self.obj['created_at']
	def get_followers(self):
		return self.api.get_followers(self.username())
	def get_following(self):
		return self.api.get_following(self.username())

class api(object):
	"""
	A simple api class for desktoppr. Handles the api calls without authentication
	"""
	def __init__(self):
		self.API_BASE = "https://api.desktoppr.co/1"
	def __get_url(self,url):
		return json.loads(urllib2.urlopen(url).read())
#	def __get_paginated_url(self,url,page=None):

	def get_info(self,username):
		url = "/".join([self.API_BASE,"users",username])
		return user(self.__get_url(url)['response'],self)
	def get_user(self,username):
		return self.get_info(username)

	def get_followers(self,username):
		url = "/".join([self.API_BASE,"users",username,"followers"])
		done = 0
		data = self.__get_url(url)
		followers = []
		while not done:
			for u in data['response']:
				followers.append(user(u,self))
			if data['pagination']['current'] == data['pagination']['pages']:
				done = 1
			else:
				data = self.__get_url(url + "?page=" + str(data['pagination']['next']))
		return followers
	def get_following(self,username):
			url = "/".join([self.API_BASE,"users",username,"following"])
			done = 0
			data = self.__get_url(url)
			following = []
			while not done:
				for u in data['response']:
					following.append(user(u,self))
				if data['pagination']['current'] == data['pagination']['pages']:
					done = 1
				else:
					data = self.__get_url(url + "?page=" + str(data['pagination']['next']))
			return following

	def get_random(self,username=None):
		if username:
			url = "/".join([self.API_BASE,"users",username,"wallpapers","random"])
		else:
			url = "/".join([self.API_BASE,"wallpapers","random"])
		return wallpaper(self.__get_url(url)['response'])

	def get_all_backgrounds(self,username):
		url = "/".join([self.API_BASE,"users",username,"wallpapers"])
		data = self.__get_url(url)
		backgrounds = []
		done = 0
		while not done:
			for b in data['response']:
				backgrounds.append(wallpaper(b))
			if data['pagination']['current'] == data['pagination']['pages']:
				done = 1
			else:
				print"getting %s/%s" % (str(data['pagination']['next']),str(data['pagination']['pages']))
				data = self.__get_url(url + "?page=" + str(data['pagination']['next']))
		return backgrounds