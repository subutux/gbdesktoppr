#!/usr/bin/env python
import threading
import os
import argparse
import urllib2
try:
	import json
except ImportError:
	import simplejson

parser = argparse.ArgumentParser()
parser.add_argument("-r","--randomize",help="set a random wallpaper")
args = parser.parse_args()

# change to my dir before import
os.chdir(os.path.split(os.path.abspath(__file__))[0])
from lib import desktoppr
from lib.crontab import CronTab
from gi.repository import Gtk, GObject, Gio, Gdk
from gi.repository.GdkPixbuf import Pixbuf
api = desktoppr.api()
backgroundStorage = os.path.expanduser("~/Pictures/desktoppr/")
if not os.path.isdir(backgroundStorage):
	os.makedirs(backgroundStorage)
localTempStorage = "/tmp/gbdesktoppr/"
if not os.path.isdir(localTempStorage):
	os.makedirs(localTempStorage)

class DownloadWallpaperThumbs(threading.Thread):
	def __init__(self,api,listStore,user,localTempStorage):
		super(DownloadWallpaperThumbs, self).__init__()
		self.api = api
		self.listStore = listStore
		self.user = user
		self.CACHE_DIR = localTempStorage
	def run(self):
		url = "/".join([self.api.API_BASE,"users",self.user,"wallpapers"])
		data = json.loads(urllib2.urlopen(url).read())
		done = 0
		while not done:
			for wallpaper in data['response']:
				# print wallpaper
				if not os.path.isfile(self.CACHE_DIR + str(wallpaper['id'])):
					file = open(self.CACHE_DIR + str(wallpaper['id']),'w')
					file.write(urllib2.urlopen(wallpaper['image']['thumb']['url']).read())
					file.close()
				pxbf = Pixbuf.new_from_file(self.CACHE_DIR + str(wallpaper['id']))
				self.listStore.append([
					str(wallpaper["id"]),
					wallpaper["image"]["url"],
					pxbf])
			if data['pagination']['current'] == data['pagination']['pages']:
				done = 1
			else:
				data = json.loads(urllib2.urlopen(url + "?page=" + str(data['pagination']['next'])).read())

class setWallpaperFromUrl(threading.Thread):
	def __init__(self,url,FromCron=False):
		super(setWallpaperFromUrl, self).__init__()
		self.url = url
		self.FromCron = FromCron

	def run(self):
		filename = backgroundStorage + os.path.basename(self.url)
		if not os.path.isfile(filename):
			file = open(filename,'w')
			file.write(urllib2.urlopen(self.url).read())
			file.close()
		if self.FromCron:
			return True
		gsetWallpaper = Gio.Settings.new('org.gnome.desktop.background')
		gsetWallpaper.set_string('picture-uri',"file://" + filename)

class signals(object):
	def onDeleteWindow(self,*args):
		Gtk.main_quit(*args)
	def on_backgroundsview_selection_changed(self,selection):
		try:
			path = selection.get_selected_items()[0]
			treeiter = store.get_iter(path)
			if treeiter != None:
				print "selected %s" % str(store.get_value(treeiter,1))
				w = setWallpaperFromUrl(str(store.get_value(treeiter,1)))
				w.start()
		except IndexError:
			return 0
	def on_minutes_value_changed(self,input):
		appSettings.set_int("random-minutes",input.get_value_as_int())

	def on_apply_user_clicked(self,button):
		store = builder.get_object("backgrounds_liststore")
		if builder.get_object("username_input").get_text() != appSettings.get_string("username"):
			appSettings.set_string("username",builder.get_object("username_input").get_text())
			store.clear()
			t = DownloadWallpaperThumbs(api,store,builder.get_object("username_input").get_text(),localTempStorage)
			t.start()
		builder.get_object('login_window').hide()
	def on_about_dialog_close(self,dialog):
		dialog.hide()
	def on_settings_button_clicked(self,widget):
		builder.get_object('login_window').show_all()
	def on_switch_randomize_activate(self,switch,gparams):
		cron = CronTab(user=True)
		print "test"
		if cron.find_comment('gbdesktoppr-timer'):
			cron.remove_all(comment="gbdesktoppr-timer")
			cron.write()
		if switch.get_active():
			appSettings.set_boolean("run-random",True)
			job = cron.new(command=os.path.split(os.path.abspath(__file__))[0]+"/App.py -r " + appSettings.get_string("username") + "> /tmp/gbdesktoppr-random.log",
				comment="gbdesktoppr-timer")
			job.minute.every(appSettings.get_int("random-minutes"))
			job.enable()
			cron.write()
		else:
			appSettings.set_boolean("run-random",False)
	def on_about_button_clicked(self,button):
		windowAbout.show()


class guiApp(object):
	def __init__(self):
		self.signals = signals()
		self.window = builder.get_object('window')
		self.dialogSettings = builder.get_object('login_window')
		self.windowAbout = builder.get_object('aboutdialog')
		self.iconview = builder.get_object('backgroundsview')
		self.iconview.set_pixbuf_column(2)


		hb = Gtk.HeaderBar()
		hb.props.show_close_button = True
		hb.props.title = "Gnome Desktoppr"
		self.window.set_titlebar(hb)

		button = Gtk.Button(label="Settings")
		icon = Gio.ThemedIcon(name="preferences-system")
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		button.add(image)
		hb.pack_end(button)


		#buttonabout = Gtk.Button(label="about")
		#hb.pack_start(buttonabout)

		builder.get_object("switch_randomize").connect('notify::active',self.signals.on_switch_randomize_activate)
		button.connect("clicked",self.signals.on_settings_button_clicked)
		#buttonabout.connect("clicked",self.signals.on_about_button_clicked)
		builder.get_object("switch_randomize").set_active(appSettings.get_boolean("run-random"))
		builder.get_object("minutes").set_value(appSettings.get_int("random-minutes"))
		builder.connect_signals(signals())

		self.window.set_wmclass ("Gnome Desktoppr", "Gnome Desktoppr")
		self.window.set_title ("Gnome Desktoppr")
		self.window.connect('delete-event',Gtk.main_quit)
		self.api = desktoppr.api()
		if appSettings.get_string("username") != "":
			builder.get_object("username_input").set_text(appSettings.get_string("username"))
			self.t = DownloadWallpaperThumbs(api,store,appSettings.get_string("username"),localTempStorage)
			self.t.start()
	def run(self):
		self.window.show_all()
		# If no username is defined, show the settings
		if appSettings.get_string("username") == "":
			builder.get_object('login_window').show_all()

		Gtk.main()

if args.randomize:

	wallpaper = api.get_random(args.randomize)
	filename = backgroundStorage + os.path.basename(wallpaper.image_url())
	# Some hackyness [http://stackoverflow.com/a/10390963]
	cmd = "export DBUS_SESSION_BUS_ADDRESS=$(grep -z DBUS_SESSION_BUS_ADDRESS /proc/$(pgrep gnome-session)/environ|cut -d= -f2-);"
	cmd = cmd + "gsettings set org.gnome.desktop.background picture-uri " + "file://" + filename
	w = setWallpaperFromUrl(wallpaper.image_url(),FromCron=True)
	w.start()
	w.join()

	os.system(cmd)

else:

	GObject.threads_init()
	builder = Gtk.Builder()
	builder.add_from_file('ui.glade')
	store = builder.get_object("backgrounds_liststore")
	appSettings = Gio.Settings.new('apps.gbdesktoppr')
	App = guiApp()
	App.run()