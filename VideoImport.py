#
# copyright by Oliver Dippel o.dippel@gmx.de 2018
#

import os
import copy
import sys
import glob
import datetime
import time
import argparse
import json
import cv2
import PIL
from PIL import Image, ImageTk
import gi
gi.require_version('Gtk', '3.0') 
from gi.repository import Gtk, GdkPixbuf, Gdk, Pango, Gio, GObject
import cairo
import numpy as np
from io import StringIO

class VideoImport:
	def __init__(self):
		self.project = {}
		self.project["fps"] = 25
		file = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cameras.json"), "r") 
		self.cam_calc = json.load(file)
		file.close()
		self.disable_cam = []

	def new (self):
		self.project = {}
		self.project["folder"] = ""
		self.project["path1"] = ""
		self.project["path2"] = ""
		self.project["pos"] = 0
		self.project["tracks"] = {}
		self.project["files"] = {}
		self.project["fps"] = 25
		self.project["frm_first"] = 0
		self.project["frm_last"] = 0
		return self.project

	def load (self, project, path):
		self.project = project
		self.project["folder"] = path
		self.info = Gtk.Window()
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
		self.info.add(vbox)
		self.infotext = Gtk.Label("Loading...")
		vbox.pack_start(self.infotext, True, True, 10)
		self.progressbar = Gtk.ProgressBar()
		vbox.pack_start(self.progressbar, True, True, 10)
		self.info.show_all()
		self.progressbar.set_fraction(0.3)
		self.path = path
		self.fid = 1
		self.cid = 1
		self.start_frm = 1525900000 * self.project["fps"]
		self.stop_frm = 9525899700 * self.project["fps"]
		self.min_length = 100
		self.project["frm_first"] = 999999999999999999
		self.project["frm_last"] = 0
		for camfolder in glob.iglob(path + "/*"):
			self.trackname = os.path.basename(camfolder)
			self.ctrim = 0
			if self.trackname in self.project["tracks"]:
				self.ctrim = self.project["tracks"][self.trackname]["frm_trim"]
			flag = 0
			for root, directories, filenames in os.walk(camfolder):
				for filename in sorted(filenames): 
					if filename.endswith(".MOV") or filename.endswith(".MP4") or filename.endswith(".MTS"):
						if self.add_mov(self.trackname, root + "/" + filename) == 1:
							flag = 1
			if flag == 1:
				track = {"name": self.trackname, "id": self.trackname, "frm_trim": self.ctrim}
				self.project["tracks"][self.trackname] = track

			self.cid += 1
		self.progressbar.set_fraction(0.6)
		## find first stamp
		for fid in self.project["files"]:
			mov = self.project["files"][fid]
			## fix fps (mov/self)
			if mov["frm_start"] + self.project["tracks"][mov["trackid"]]["frm_trim"] < self.project["frm_first"]:
				self.project["frm_first"] = mov["frm_start"] + self.project["tracks"][mov["trackid"]]["frm_trim"]
			if (mov["frm_start"] + self.project["tracks"][mov["trackid"]]["frm_trim"] + mov["frm_length"]) > self.project["frm_last"]:
				self.project["frm_last"] = (mov["frm_start"] + self.project["tracks"][mov["trackid"]]["frm_trim"] + mov["frm_length"])
		#print(self.project["frm_first"])
		#print(self.project["frm_last"])
		#print(self.project["frm_last"] - self.project["frm_first"])
		## calc start and end point for each video
		last_pos = 0
		last_trackid = -1
		for fid in self.project["files"]:
			mov = self.project["files"][fid]
			if last_trackid != mov["trackid"]:
				last_pos = 0
			mov["frm_begin"] = (mov["frm_start"] - self.project["frm_first"])
			mov["frm_end"] = mov["frm_begin"] + mov["frm_length"]
			mov["frm_diff"] = mov["frm_begin"] - last_pos
			last_pos = mov["frm_end"]
			last_trackid = mov["trackid"]
		self.progressbar.set_fraction(1.0)
		self.info.destroy()
		return self.project

	def add_mov (self, cam, filename):
		## get metadata
		if not os.path.isfile(filename + ".info"):
			cap = cv2.VideoCapture(filename)
			length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
			mov_fps = cap.get(cv2.CAP_PROP_FPS)
			file = open(filename + ".info", "w") 
			file.write(str(length) + ";" + str(mov_fps))
			file.close() 
		if not os.path.isfile(filename + ".metadata"):
			print(os.popen("exiftool " + filename + " > " + filename + ".metadata 2>&1").read().strip())
		if not os.path.isfile(os.path.splitext(filename)[0] + ".THM"):
			print(os.path.splitext(filename)[0] + ".THM")
			print(os.popen("ffmpeg -i " + filename + " -vf  \"thumbnail,scale=640:360\" -frames:v 1 " + filename + ".jpg 2>&1").read().strip())
			os.rename(filename + ".jpg", os.path.splitext(filename)[0] + ".THM")
		## read metadata
		length = 0
		mov_fps = 0
		file = open(filename + ".info", "r") 
		for line in file.read().split("\n"):
			length = int(line.split(";")[0])
			mov_fps = float(line.split(";")[1])
		file = open(filename + ".metadata", "r") 
		camname = cam
		lens = "???"
		fstamp = os.stat(filename).st_mtime
		cstamp = 0
		for line in file.read().split("\n"):
			if ":" in line:
				var = line.split(":", 1)[0].strip()
				val = line.split(":", 1)[1].strip()
			else:
				continue
			if val == "":
				continue
			if var == "Media Create Date":
				dt = line.split(":", 1)[1].strip()
				if "." in dt:
					cstamp = datetime.datetime.strptime(dt, "%Y:%m:%d %H:%M:%S.%f").timestamp()
				else:
					cstamp = datetime.datetime.strptime(dt, "%Y:%m:%d %H:%M:%S").timestamp()
			elif var == "Create Date":
				dt = line.split(":", 1)[1].strip()
				if "." in dt:
					cstamp = datetime.datetime.strptime(dt, "%Y:%m:%d %H:%M:%S.%f").timestamp()
				else:
					cstamp = datetime.datetime.strptime(dt, "%Y:%m:%d %H:%M:%S").timestamp()
			elif var == "Date/Time Original":
				dt = line.split(":", 1)[1].split("+", 1)[0].strip()
				if "." in dt:
					cstamp = datetime.datetime.strptime(dt, "%Y:%m:%d %H:%M:%S.%f").timestamp()
				else:
					cstamp = datetime.datetime.strptime(dt, "%Y:%m:%d %H:%M:%S").timestamp()
			elif var == "Canon Model ID":
				camname = line.split(":", 1)[1].strip()
			elif var == "Canon Model Name":
				camname = line.split(":", 1)[1].strip()
			elif var == "Camera Model Name":
				camname = line.split(":", 1)[1].strip()
			elif var == "Model":
				camname = line.split(":", 1)[1].strip()
			elif var == "Make":
				camname = line.split(":", 1)[1].strip()
			elif var == "Lens Type":
				lens = line.split(":", 1)[1].strip()
			elif var == "Lens Model":
				lens = line.split(":", 1)[1].strip()
		## fix timestamps
		if camname in self.cam_calc:
			if self.cam_calc[camname] == "CSTAMP":
				stamp = cstamp
			elif self.cam_calc[camname] == "FSTAMP":
				stamp = fstamp
			elif self.cam_calc[camname] == "CSTAMP_MINUS_LEN":
				stamp = cstamp - (length / mov_fps)
			elif self.cam_calc[camname] == "FSTAMP_MINUS_LEN":
				stamp = fstamp - (length / mov_fps)
			else:
				print ("UNKNOWN")
		elif cstamp != 0:
			stamp = cstamp
		else:
			stamp = fstamp
		## add offset for each cam
		frm_start = stamp * self.project["fps"]
		## add files
		flag = 0
		if frm_start + self.ctrim >= self.start_frm and frm_start + self.ctrim <= self.stop_frm:
			if length >= self.min_length:
				frm_trim = 0
				if filename in self.project["files"]:
					frm_trim = self.project["files"][filename]["frm_trim"]
				mov = {"track": cam, "path": filename, "name": os.path.splitext(os.path.basename(filename))[0], "id": self.fid, "trackid": self.trackname, "frm_length": length * self.project["fps"] / mov_fps, "length": length, "fps": mov_fps, "camname": camname, "lens": lens, "frm_start": frm_start, "stamp": stamp, "cstamp": cstamp, "fstamp": fstamp, "stampdiff": (fstamp - cstamp), "duration": (length / mov_fps), "test": (fstamp - stamp), "frm_trim": frm_trim}
				self.project["files"][filename] = mov
				self.fid += 1
				flag = 1
		return flag




