#!/usr/bin/python3
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
import gi
gi.require_version('Gtk', '3.0') 
from gi.repository import Gtk, GdkPixbuf, Gdk, Pango, Gio, GObject
from gi.repository.GdkPixbuf import Pixbuf, InterpType
import cairo
from io import StringIO
from VideoImport import *
from VideoExport import *



class MultiCamSync(Gtk.Application):
	def __init__(self):
		Gtk.Application.__init__(self)
		self.video_init_cv()
		self.vi = VideoImport()
		self.ve = VideoExport(self.vi)
		self.cw = 1600
		self.ch = 200
		self.stat = 0
		self.update = 0
		self.streams = {}
		self.thumbs = {}
		self.project = self.vi.new()
		self.filename = ""

	def do_activate(self):
		self.window = Gtk.ApplicationWindow(application=self)
		self.window.connect("destroy", Gtk.main_quit)
		titlebar = self.create_titlebar()
		self.window.set_titlebar(titlebar)
		mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.window.add(mainbox)
		videobox = self.create_videobox()
		mainbox.pack_start(videobox, False, False, 0)
		infobox = self.create_infobox()
		mainbox.pack_start(infobox, False, False, 10)
		timeline = self.create_timeline()
		mainbox.pack_start(timeline, True, True, 0)
		sliders = self.create_sliders()
		mainbox.pack_start(sliders, False, False, 0)
		button_startstop = Gtk.Button.new_with_label("Start/Stop")
		button_startstop.connect("clicked", self.start_stop)
		mainbox.pack_start(button_startstop, False, False, 0)
		self.window.show_all()
		self.video_loop()
		if len(sys.argv) > 1:
			if sys.argv[1].endswith(".multicamsync"):
				if os.path.isfile(sys.argv[1]):
					self.file_load_projectfile(sys.argv[1])
				else:
					print("argument is not a file: " + sys.argv[1])
			elif os.path.isdir(sys.argv[1]):
				self.project = self.vi.load(self.vi.new(), sys.argv[1])
				self.filename = ""
				self.ajustment_pos.configure(0, 0, (self.project["frm_last"] - self.project["frm_first"]), 1, 25, 0)
				self.ajustment_offset.configure(0, 0, (self.project["frm_last"] - self.project["frm_first"]), 1, 25, 0)
				self.treview_update()
				self.video_pos_cv()
				self.video_update_cv()

			if len(sys.argv) > 2:
				if sys.argv[2].endswith(".osp"):
					print("export to " + sys.argv[2] + " as Openshot-Project")
					self.ve.openshot(sys.argv[2], self.project)
					sys.exit(0)
				elif sys.argv[2].endswith(".kdenlive"):
					print("export to " + sys.argv[2] + " as Kdenlive-Project")
					self.ve.kdenlive(sys.argv[2], self.project)
					sys.exit(0)
				elif sys.argv[2].endswith(".xmeml") or sys.argv[2].endswith(".xml"):
					print("export to " + sys.argv[2] + " as Xmeml-Project")
					self.ve.xmeml(sys.argv[2], self.project)
					sys.exit(0)
				else:
					print("argument is not a known fileformat: " + sys.argv[2])
					sys.exit(0)


	def start_stop(self, button):
		self.stat = 1 - self.stat

	def import_folder(self, action, parameter):
		dialog = Gtk.FileChooserDialog("Please choose a folder", self.window, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK))
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			print("Folder selected: " + dialog.get_filename())
			self.project = self.vi.load(self.vi.new(), dialog.get_filename())
			self.filename = ""
			self.ajustment_pos.configure(0, 0, (self.project["frm_last"] - self.project["frm_first"]), 1, 25, 0)
			self.ajustment_offset.configure(0, 0, (self.project["frm_last"] - self.project["frm_first"]), 1, 25, 0)
			self.treview_update()
			self.video_pos_cv()
			self.video_update_cv()
		elif response == Gtk.ResponseType.CANCEL:
			print("Cancel clicked")
		dialog.destroy()

	def poject_new(self, action, parameter):
		self.project = self.vi.new()
		self.filename = ""
		self.ajustment_pos.configure(0, 0, 10000, 1, 25, 0)
		self.ajustment_offset.configure(0, 0, 10000, 1, 25, 0)
		self.video_l.set_from_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "empty.png"))
		self.video_r.set_from_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "empty.png"))
		self.treview_update()
		self.video_pos_cv()
		self.video_update_cv()

	def file_save_project(self, action, parameter):
		if self.filename == "":
			file_save_project_as(action, parameter)
		else:
			print("MultiCamSync project save to " + self.filename)
			self.project["pos"] = self.slider_pos.get_value()
			self.project["scale"] = self.slider_scale.get_value()
			self.project["offset"] = self.slider_offset.get_value()
			jsondata = json.dumps(self.project, indent=4, separators=(',', ': '))
			file = open(self.filename, "w") 
			file.write(jsondata) 
			file.close() 

	def file_save_project_as(self, action, parameter):
		dialog = Gtk.FileChooserDialog("Please choose a file", self.window, Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
		filter_xmeml = Gtk.FileFilter()
		filter_xmeml.set_name("MultiCamSync project")
		filter_xmeml.add_pattern("*.multicamsync")
		dialog.add_filter(filter_xmeml)
		filter_any = Gtk.FileFilter()
		filter_any.set_name("Any files")
		filter_any.add_pattern("*")
		dialog.add_filter(filter_any)
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			print("MultiCamSync project save to " + dialog.get_filename())
			self.project["pos"] = self.slider_pos.get_value()
			self.project["scale"] = self.slider_scale.get_value()
			self.project["offset"] = self.slider_offset.get_value()
			jsondata = json.dumps(self.project, indent=4, separators=(',', ': '))
			file = open(dialog.get_filename(), "w") 
			file.write(jsondata) 
			file.close() 
		elif response == Gtk.ResponseType.CANCEL:
			print("Cancel clicked")
		dialog.destroy()

	def file_load_projectfile(self, path):
		file = open(path, "r") 
		self.project = json.load(file)
		file.close()
		self.project = self.vi.load(self.project, self.project["folder"])
		self.filename = path
		self.ajustment_pos.configure(0, 0, (self.project["frm_last"] - self.project["frm_first"]), 1, 25, 0)
		self.ajustment_offset.configure(0, 0, (self.project["frm_last"] - self.project["frm_first"]), 1, 25, 0)
		self.slider_pos.set_value(self.project["pos"])
		self.slider_scale.set_value(self.project["scale"])
		self.slider_offset.set_value(self.project["offset"])
		self.treview_update()
		self.video_pos_cv()
		self.video_update_cv()

	def file_load_project(self, action, parameter):
		dialog = Gtk.FileChooserDialog("Please choose a file", self.window, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		filter_xmeml = Gtk.FileFilter()
		filter_xmeml.set_name("MultiCamSync project")
		filter_xmeml.add_pattern("*.multicamsync")
		dialog.add_filter(filter_xmeml)
		filter_any = Gtk.FileFilter()
		filter_any.set_name("Any files")
		filter_any.add_pattern("*")
		dialog.add_filter(filter_any)
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			print("MultiCamSync project load from " + dialog.get_filename())
			self.file_load_projectfile(dialog.get_filename())
		elif response == Gtk.ResponseType.CANCEL:
			print("Cancel clicked")
		dialog.destroy()

	def file_save_xmeml(self, action, parameter):
		dialog = Gtk.FileChooserDialog("Please choose a file", self.window, Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
		filter_xmeml = Gtk.FileFilter()
		filter_xmeml.set_name("Xmeml project")
		filter_xmeml.add_pattern("*.xml")
		dialog.add_filter(filter_xmeml)
		filter_any = Gtk.FileFilter()
		filter_any.set_name("Any files")
		filter_any.add_pattern("*")
		dialog.add_filter(filter_any)
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			print("Xmeml project export to " + dialog.get_filename())
			self.ve.xmeml(dialog.get_filename(), self.project)
		elif response == Gtk.ResponseType.CANCEL:
			print("Cancel clicked")
		dialog.destroy()

	def file_save_openshot(self, action, parameter):
		dialog = Gtk.FileChooserDialog("Please choose a file", self.window, Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
		filter_openshot = Gtk.FileFilter()
		filter_openshot.set_name("openshot project")
		filter_openshot.add_pattern("*.osp")
		dialog.add_filter(filter_openshot)
		filter_any = Gtk.FileFilter()
		filter_any.set_name("Any files")
		filter_any.add_pattern("*")
		dialog.add_filter(filter_any)
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			print("openshot project export to " + dialog.get_filename())
			self.ve.openshot(dialog.get_filename(), self.project)
		elif response == Gtk.ResponseType.CANCEL:
			print("Cancel clicked")
		dialog.destroy()

	def file_save_kdenlive(self, action, parameter):
		dialog = Gtk.FileChooserDialog("Please choose a file", self.window, Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
		filter_kdenlive = Gtk.FileFilter()
		filter_kdenlive.set_name("Kdenlive project")
		filter_kdenlive.add_pattern("*.kdenlive")
		dialog.add_filter(filter_kdenlive)
		filter_any = Gtk.FileFilter()
		filter_any.set_name("Any files")
		filter_any.add_pattern("*")
		dialog.add_filter(filter_any)
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			print("Kdenlive project export to " + dialog.get_filename())
			self.ve.kdenlive(dialog.get_filename(), self.project)
		elif response == Gtk.ResponseType.CANCEL:
			print("Cancel clicked")
		dialog.destroy()

	def medialist_l_changed(self, selection):
		(model, iter) = selection.get_selected()
		if iter is not None:
			self.set_video1_path(model[iter][3])

	def medialist_r_changed(self, selection):
		(model, iter) = selection.get_selected()
		if iter is not None:
			self.set_video2_path(model[iter][3])

	def get_mov_by_path(self, path):
		for fid in self.project["files"]:
			mov = self.project["files"][fid]
			if mov["path"] == path:
				return mov
		return {}

	def get_num_by_path(self, path):
		n = 0
		for fid in self.project["files"]:
			mov = self.project["files"][fid]
			if mov["path"] == path:
				return n
			n += 1
		return {}


	def set_video1_path(self, path):
		mov = self.get_mov_by_path(path)
		if mov == {}:
			return
		self.project["path1"] = path
		self.meta_l.set_text(str(mov["camname"]) + " - " + str(mov["lens"]))
		num = self.get_num_by_path(mov["path"])
		self.medialist_l.set_cursor(num)
		## jump to media start/middle
		pos = self.slider_pos.get_value()
		begin = mov["frm_begin"] + self.project["tracks"][mov["trackid"]]["frm_trim"] + mov["frm_trim"]
		end = mov["frm_end"] + self.project["tracks"][mov["trackid"]]["frm_trim"] + mov["frm_trim"]
		if pos < begin:
			pos = begin
			self.slider_pos.set_value(pos)
		elif pos > end:
			pos = (begin + (mov["frm_length"] / 2))
			self.slider_pos.set_value(pos)
		## redraw
		self.video_pos_cv()
		self.video_update_cv()

	def set_video2_path(self, path):
		mov = self.get_mov_by_path(path)
		if mov == {}:
			return
		self.project["path2"] = path
		self.meta_r.set_text(str(mov["camname"]) + " - " + str(mov["lens"]))
		num = self.get_num_by_path(mov["path"])
		self.medialist_r.set_cursor(num)
		## update diff scale
		self.slider_diff.set_value(-mov["frm_trim"])
		self.slider_difft.set_value(self.project["tracks"][mov["trackid"]]["frm_trim"])
		## redraw
		self.video_pos_cv()
		self.video_update_cv()

	def set_list_l(self, event):
		item = self.tree.selection()[0]
		value = self.tree.item(item,"text")
		self.set_video1_path(value)

	def set_list_r(self, event):
		item = self.tree.selection()[0]
		value = self.tree.item(item,"text")
		self.set_video2_path(value)

	def video_loop_reset(self):
		self.update = 0

	def video_loop(self):
		if self.stat == 1 or self.update == 1:
			if self.stat == 1:
				self.slider_pos.set_value(self.slider_pos.get_value() + 1)
			if self.stat != 1:
				self.video_pos_cv()
			self.video_update_cv()
			self.timeline.queue_draw()
			GObject.timeout_add(5, self.video_loop_reset)

		if self.stat == 1:
			GObject.timeout_add(1000 / self.project["fps"], self.video_loop)
		else:
			GObject.timeout_add(10, self.video_loop)


	def video_init_cv(self):
		#print("video_init")
		return


	def video_pos_cv(self):
		#print("video_pos")
		pos = self.slider_pos.get_value()
		if self.project["path1"] != "":
			mov1 = self.get_mov_by_path(self.project["path1"])
			if mov1 != {}:
				if not mov1["path"] in self.streams:
					print("loading media file: " + mov1["path"])
					self.streams[mov1["path"]] = cv2.VideoCapture(mov1["path"])
				begin1 = pos - mov1["frm_begin"] - self.project["tracks"][mov1["trackid"]]["frm_trim"] - mov1["frm_trim"]
				if begin1 >= 0:
					self.streams[mov1["path"]].set(1, begin1 * mov1["fps"] / self.project["fps"]);
				else:
					self.streams[mov1["path"]].set(1, 0);
		if self.project["path2"] != "":
			mov2 = self.get_mov_by_path(self.project["path2"])
			if mov2 != {}:
				if not mov2["path"] in self.streams:
					print("loading media file: " + mov1["path"])
					self.streams[mov2["path"]] = cv2.VideoCapture(mov2["path"])
				begin2 = pos - mov2["frm_begin"] - self.project["tracks"][mov2["trackid"]]["frm_trim"] - mov2["frm_trim"]
				if begin2 >= 0:
					self.streams[mov2["path"]].set(1, begin2 * mov2["fps"] / self.project["fps"]);
				else:
					self.streams[mov2["path"]].set(1, 0);


	def video_update_cv(self):
		#print("video_update")
		pos = self.slider_pos.get_value()
		if self.project["path1"] != "":
			mov1 = self.get_mov_by_path(self.project["path1"])
			begin1 = pos - mov1["frm_begin"] - self.project["tracks"][mov1["trackid"]]["frm_trim"] - mov1["frm_trim"]
			if mov1 != {}:
				# hack 50fps
				if self.stat == 1 and mov1["fps"] == 50:
					ok1, frame1 = self.streams[mov1["path"]].read()
					ok1, frame1 = self.streams[mov1["path"]].read()
				else:
					ok1, frame1 = self.streams[mov1["path"]].read()
				if begin1 < 0:
					self.video_l.set_from_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "empty.png"))
				elif begin1 > mov1["frm_length"]:
					self.video_l.set_from_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "empty.png"))
				elif ok1:
					frame_l = cv2.resize(frame1, (480,270))
					iml = cv2.cvtColor(frame_l, cv2.COLOR_BGR2RGB)
					pbl = GdkPixbuf.Pixbuf.new_from_data(iml.tostring(),
					GdkPixbuf.Colorspace.RGB, False, 8, iml.shape[1], iml.shape[0], iml.shape[2] * iml.shape[1])
					self.video_l.set_from_pixbuf(pbl.copy())
					self.video_l.show()
				else:
					self.video_l.set_from_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "empty.png"))
		if self.project["path2"] != "":
			mov2 = self.get_mov_by_path(self.project["path2"])
			begin2 = pos - mov2["frm_begin"] - self.project["tracks"][mov2["trackid"]]["frm_trim"] - mov2["frm_trim"]
			if mov2 != {}:
				# hack 50fps
				if self.stat == 1 and mov2["fps"] == 50:
					ok2, frame2 = self.streams[mov2["path"]].read()
					ok2, frame2 = self.streams[mov2["path"]].read()
				else:
					ok2, frame2 = self.streams[mov2["path"]].read()
				if begin2 < 0:
					self.video_r.set_from_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "empty.png"))
				elif begin2 > mov2["frm_length"]:
					self.video_r.set_from_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "empty.png"))
				elif ok2:
					frame_r = cv2.resize(frame2, (480,270))
					imr = cv2.cvtColor(frame_r, cv2.COLOR_BGR2RGB)
					pbr = GdkPixbuf.Pixbuf.new_from_data(imr.tostring(),
					GdkPixbuf.Colorspace.RGB, False, 8, imr.shape[1], imr.shape[0], imr.shape[2] * imr.shape[1])
					self.video_r.set_from_pixbuf(pbr.copy())
					self.video_r.show()
				else:
					self.video_r.set_from_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "empty.png"))


	def on_update_diff(self, event):
		#print("update_diff")
		mov = self.get_mov_by_path(self.project["path2"])
		mov["frm_trim"] = -self.slider_diff.get_value()
		self.timeline.queue_draw()
		self.update = 1


	def on_update_difft(self, event):
		#print("update_diff")
		mov = self.get_mov_by_path(self.project["path2"])
		self.project["tracks"][mov["trackid"]]["frm_trim"] = self.slider_difft.get_value()
		self.timeline.queue_draw()
		self.update = 1


	def on_update_pos(self, event):
		self.timeline.queue_draw()
		if self.stat != 1 and self.update != 1:
			#print("update_pos")
			self.update = 1


	def on_update_slider(self, event):
		#print("update_slider")
		self.timeline.queue_draw()


	def timeline_configure_event(self, da, event):
		allocation = da.get_allocation()
		self.surface = da.get_window().create_similar_surface(cairo.CONTENT_COLOR, allocation.width, allocation.height)
		cairo_ctx = cairo.Context(self.surface)
		cairo_ctx.set_source_rgb(1, 1, 1)
		cairo_ctx.paint()
		return True


	def timeline_draw_event(self, da, cairo_ctx):
		if len(self.project["tracks"]) == 0:
			return
		self.thumbs = {}
		self.cw = self.timeline.get_allocation().width
		self.ch = self.timeline.get_allocation().height
		scale_x = self.slider_scale.get_value() / 200.0
		pos = self.slider_pos.get_value()
		offset_x = 100 - self.slider_offset.get_value() * scale_x
		step_y = (self.ch - 20) / len(self.project["tracks"])
		self.info_frame.set_markup("<span size=\"x-large\">Frame: " + str(int(pos)) + "</span>");
		self.info_timepos.set_markup("<span size=\"x-large\">Time: " + datetime.datetime.fromtimestamp(int((self.project["frm_first"] + pos) / self.project["fps"])).strftime('%Y-%m-%d %H:%M:%S') + "</span>")
		self.info_timestart.set_markup("<span size=\"large\"> Begin: " + datetime.datetime.fromtimestamp(int((self.project["frm_first"]) / self.project["fps"])).strftime('%Y-%m-%d %H:%M:%S') + "</span>")
		self.info_timestop.set_markup("<span size=\"large\">End: " + datetime.datetime.fromtimestamp(int((self.project["frm_last"]) / self.project["fps"])).strftime('%Y-%m-%d %H:%M:%S') + " " + "</span>")
		self.info_stamp.set_markup("<span size=\"x-large\">Stamp: " + str(pos / self.project["fps"]) + " s" + "</span>")
		cairo_ctx.set_line_width(0.1)
		## tracks background
		cairo_ctx.set_source_rgb(0.15, 0.15, 0.15)
		cairo_ctx.rectangle(100, 20, self.cw, self.ch - 20)
		cairo_ctx.fill()

		## top frame ruler
		cairo_ctx.set_source_rgb(0.7, 0.7, 0.7)
		cairo_ctx.rectangle(100, 0, self.cw, 20)
		cairo_ctx.fill()
		cairo_ctx.set_line_width(0.5)
		cairo_ctx.set_source_rgb(0.0, 0.0, 0.0)
		cairo_ctx.select_font_face("Times")
		cairo_ctx.set_font_size(12)
		for frm in range(0, int(self.project["frm_last"] - self.project["frm_first"]), int(self.project["fps"] * 60)):
			cairo_ctx.new_path()
			cairo_ctx.move_to((frm * scale_x) + offset_x, 15)
			cairo_ctx.rel_line_to(0, 5)
			cairo_ctx.stroke()
		for frm in range(0, int(self.project["frm_last"] - self.project["frm_first"]), int(self.project["fps"] * 60 * 10)):
			cairo_ctx.new_path()
			cairo_ctx.move_to((frm * scale_x) + offset_x, 10)
			cairo_ctx.rel_line_to(0, 10)
			cairo_ctx.stroke()
			cairo_ctx.move_to((frm * scale_x) + offset_x, 10)
			cairo_ctx.show_text(str(frm))
		cairo_ctx.set_line_width(0.1)
		## draw tracks
		y = 20
		n = 0
		for cid in self.project["tracks"]:
			cam = self.project["tracks"][cid]
			## split tracks
			cairo_ctx.set_source_rgb(0.7, 0.7, 0.7)
			cairo_ctx.new_path()
			cairo_ctx.move_to(0, y)
			cairo_ctx.rel_line_to(self.cw, 0)
			cairo_ctx.stroke()
			## draw media on track
			for fid in self.project["files"]:
				mov = self.project["files"][fid]
				if mov["trackid"] == cam["id"]:
					begin = mov["frm_begin"] + self.project["tracks"][mov["trackid"]]["frm_trim"] + mov["frm_trim"]
					end = mov["frm_end"] + self.project["tracks"][mov["trackid"]]["frm_trim"] + mov["frm_trim"]
					## set colors (left/right/in range/other)
					lg1 = cairo.LinearGradient((begin * scale_x) + offset_x, y + 1, (end * scale_x) + offset_x, y + step_y - 1)
					if mov["path"] == self.project["path1"]:
						cairo_ctx.set_source_rgb(0.9, 0.4, 0.4)
						lg1.add_color_stop_rgb(0, 0.9, 0.4, 0.4)
					elif mov["path"] == self.project["path2"]:
						cairo_ctx.set_source_rgb(0.4, 0.9, 0.4)
						lg1.add_color_stop_rgb(0, 0.4, 0.9, 0.4)
					elif pos >= begin and pos <= end:
						cairo_ctx.set_source_rgb(0.5, 0.5, 0.9)
						lg1.add_color_stop_rgb(0, 0.5, 0.5, 0.9)
					else:
						cairo_ctx.set_source_rgb(0.5, 0.5, 0.6)
						lg1.add_color_stop_rgb(0, 0.5, 0.5, 0.6)
					lg1.add_color_stop_rgb(1, 0.2, 0.2, 0.2)
					## draw media block
					cairo_ctx.rectangle((begin * scale_x) + offset_x, y + 1, ((end - begin) * scale_x), step_y - 2)
					cairo_ctx.set_source(lg1)
					cairo_ctx.fill()
					cairo_ctx.set_source_rgb(0, 0, 0)
					cairo_ctx.rectangle((begin * scale_x) + offset_x, y + 1, ((end - begin) * scale_x), step_y - 2)
					cairo_ctx.stroke()
					## load thumbnail
					if not mov["path"] in self.thumbs:
						if os.path.isfile(os.path.splitext(mov["path"])[0] + ".THM"):
							w = (step_y - 2) * 1.777
							if w > (end - begin) * scale_x:
								w = (end - begin) * scale_x
							pixbuf = Pixbuf.new_from_file(os.path.splitext(mov["path"])[0] + ".THM")
							self.thumbs[mov["path"]] = pixbuf.scale_simple(w, step_y - 2, InterpType.BILINEAR)
						else:
							self.thumbs[mov["path"]] = ""
					## draw thumbnail
					if self.thumbs[mov["path"]] != "":
						Gdk.cairo_set_source_pixbuf(cairo_ctx, self.thumbs[mov["path"]], (begin * scale_x) + offset_x, y + 1)
						cairo_ctx.paint()
					## draw media label
					if (end * scale_x) - (begin * scale_x) > 60:
						cairo_ctx.set_source_rgb(1, 1, 1)
						cairo_ctx.select_font_face("Times")
						cairo_ctx.set_font_size(12)
						cairo_ctx.move_to((begin * scale_x) + offset_x + 2, y + 12)
						cairo_ctx.show_text(mov["name"])
			y += step_y
			n += 1
		## draw track titles
		cairo_ctx.rectangle(0, 0, 100, self.ch)
		lg1 = cairo.LinearGradient(0, 0, 100, 0)
		lg1.add_color_stop_rgb(0, 0.1, 0.1, 0.1)
		lg1.add_color_stop_rgb(1, 0.7, 0.7, 0.7)
		cairo_ctx.set_source(lg1)
		cairo_ctx.fill()
		cairo_ctx.set_source_rgb(0.0, 0.0, 0.0)
		cairo_ctx.new_path()
		cairo_ctx.move_to(100, 0)
		cairo_ctx.rel_line_to(0, self.ch)
		cairo_ctx.close_path()
		cairo_ctx.stroke()
		cairo_ctx.select_font_face("Times")
		cairo_ctx.set_font_size(12)
		y = 20
		for cid in self.project["tracks"]:
			cam = self.project["tracks"][cid]
			cairo_ctx.set_source_rgba(0.1, 0.1, 0.1, 1.0)
			cairo_ctx.move_to(10 + 1, y + step_y - 12 + 1)
			cairo_ctx.show_text(cam["name"])
			cairo_ctx.set_source_rgba(0.9, 0.9, 0.9, 1.0)
			cairo_ctx.move_to(10, y + step_y - 12)
			cairo_ctx.show_text(cam["name"])
			## split tracks
			cairo_ctx.new_path()
			cairo_ctx.move_to(0, y)
			cairo_ctx.rel_line_to(self.cw, 0)
			cairo_ctx.stroke()
			y += step_y
		## pos
		cairo_ctx.set_line_width(0.5)
		cairo_ctx.set_source_rgb(1, 1, 1)
		cairo_ctx.new_path()
		cairo_ctx.move_to((pos * scale_x) + offset_x, 10)
		cairo_ctx.rel_line_to(0, self.ch)
		cairo_ctx.close_path()
		cairo_ctx.stroke()
		## end of sequenz
		cairo_ctx.new_path()
		cairo_ctx.move_to(((self.project["frm_last"] - self.project["frm_first"]) * scale_x) + offset_x, 10)
		cairo_ctx.rel_line_to(0, self.ch)
		cairo_ctx.close_path()
		cairo_ctx.stroke()
		## draw track thumbnails
		w = (step_y - 2) * 1.777
		cairo_ctx.rectangle(self.cw - w, 0, self.cw, self.ch)
		lg1 = cairo.LinearGradient(0, 0, w, 0)
		lg1.add_color_stop_rgb(0, 0.1, 0.1, 0.1)
		lg1.add_color_stop_rgb(1, 0.7, 0.7, 0.7)
		cairo_ctx.set_source(lg1)
		cairo_ctx.fill()
		cairo_ctx.set_source_rgb(0.0, 0.0, 0.0)
		cairo_ctx.new_path()
		cairo_ctx.move_to(self.cw - w, 0)
		cairo_ctx.rel_line_to(0, self.ch)
		cairo_ctx.close_path()
		cairo_ctx.stroke()
		y = 20
		n = 0
		for cid in self.project["tracks"]:
			cam = self.project["tracks"][cid]
			for fid in self.project["files"]:
				mov = self.project["files"][fid]
				if mov["trackid"] == cam["id"]:
					begin = mov["frm_begin"] + self.project["tracks"][mov["trackid"]]["frm_trim"] + mov["frm_trim"]
					end = mov["frm_end"] + self.project["tracks"][mov["trackid"]]["frm_trim"] + mov["frm_trim"]
					if pos >= begin and pos <= end:
						cairo_ctx.set_source_rgb(0.5, 0.5, 0.9)
						lg1.add_color_stop_rgb(0, 0.5, 0.5, 0.9)
						if os.path.isfile(os.path.splitext(mov["path"])[0] + ".THM"):
							pixbuf = Pixbuf.new_from_file(os.path.splitext(mov["path"])[0] + ".THM")
							self.thumbs[mov["path"]] = pixbuf.scale_simple(w, step_y - 2, InterpType.BILINEAR)
						else:
							self.thumbs[mov["path"]] = ""
						## draw thumbnail
						if self.thumbs[mov["path"]] != "":
							Gdk.cairo_set_source_pixbuf(cairo_ctx, self.thumbs[mov["path"]], self.cw - w, y + 1)
							cairo_ctx.paint()
			y += step_y
			n += 1
		## timeline-border
		cairo_ctx.set_source_rgb(0.5, 0.5, 0.5)
		cairo_ctx.rectangle(0, 0, self.cw, self.ch)
		cairo_ctx.stroke()

		return False


	def timeline_clicked(self, widget, event):
		scale_x = self.slider_scale.get_value() / 200.0
		offset_x = 100 - self.slider_offset.get_value() * scale_x
		step_y = (self.ch - 20) / len(self.project["tracks"])
		## draw all tracks
		y = 20
		for cid in self.project["tracks"]:
			cam = self.project["tracks"][cid]
			for fid in self.project["files"]:
				mov = self.project["files"][fid]
				if mov["trackid"] == cam["id"]:
					begin = mov["frm_begin"] + self.project["tracks"][mov["trackid"]]["frm_trim"] + mov["frm_trim"]
					end = mov["frm_end"] + self.project["tracks"][mov["trackid"]]["frm_trim"] + mov["frm_trim"]
					if event.x >= (begin * scale_x) + offset_x and event.x <= (end * scale_x) + offset_x:
						if event.y >= y and event.y <= y + step_y:
							if event.button == 1:
								# mousebutton
								self.set_video1_path(mov["path"])
								self.timeline.queue_draw()
								return
							if event.button == 3:
								self.set_video2_path(mov["path"])
								self.timeline.queue_draw()
								return
			y += step_y

		frame = int((event.x - offset_x) / scale_x)
		self.slider_pos.set_value(frame)
		self.timeline.queue_draw()


	def treview_update(self):
		self.listmodel_l.clear(); 
		self.listmodel_r.clear(); 
		n = 0
		for fid in self.project["files"]:
			mov = self.project["files"][fid]
			begin = mov["frm_begin"] + self.project["tracks"][mov["trackid"]]["frm_trim"] + mov["frm_trim"]
			end = mov["frm_end"] + self.project["tracks"][mov["trackid"]]["frm_trim"] + mov["frm_trim"]
			comment = "Name: " + mov["name"] + "\n"
			comment += "Track: " + str(mov["track"]) + "\n"
			comment += "Cam: " + mov["camname"] + "\n"
			comment += "Lens: " + mov["lens"] + "\n"
			comment += "FPS: " + str(mov["fps"]) + "\n"
			comment += "Length: " + str(mov["frm_length"])
			if n % 2 == 0:
#				background_color = "#333"
				background_color = "#666"
			else:
#				background_color = "#444"
				background_color = "#777"
			self.listmodel_l.append([comment, str(mov["frm_trim"]), background_color, mov["path"]])
			self.listmodel_r.append([comment, str(mov["frm_trim"]), background_color, mov["path"]])
			n += 1

	def create_sliders(self):
		sliderbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)


		## pos slider
		posbox = Gtk.Box()
		sliderbox.pack_start(posbox, False, False, 0)
		label = Gtk.Label("Position:")
		posbox.pack_start(label, False, False, 0)
		self.ajustment_pos = Gtk.Adjustment.new(0, 0, 10000, 1, 25, 0);
		self.slider_pos = Gtk.Scale.new(Gtk.Orientation.HORIZONTAL, self.ajustment_pos)
		posbox.pack_start(self.slider_pos, True, True, 0)
		self.slider_pos.connect("value-changed", self.on_update_pos)


		diffbox = Gtk.Box()
		sliderbox.pack_start(diffbox, False, False, 0)
		## media-diff slider
		label = Gtk.Label("Media-Diff: ")
		diffbox.pack_start(label, False, False, 0)
		self.slider_diff = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, -300, 300, 1.0)
		diffbox.pack_start(self.slider_diff, True, True, 0)
		self.slider_diff.connect("value-changed", self.on_update_diff)
		## track-diff spinner
		label = Gtk.Label("Track-Diff: ")
		diffbox.pack_start(label, False, False, 0)
		self.ajustment_difft = Gtk.Adjustment(0, -10000000, 10000000, 1, 25, 0)
		self.slider_difft = Gtk.SpinButton(adjustment=self.ajustment_difft, climb_rate=1, digits=0)
		diffbox.pack_start(self.slider_difft, True, True, 0)
		self.slider_difft.connect("value-changed", self.on_update_difft)


		viewbox = Gtk.Box()
		sliderbox.pack_start(viewbox, False, False, 0)
		## scale slider
		label = Gtk.Label("Scaler: ")
		viewbox.pack_start(label, False, False, 0)
		self.slider_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.0, 30.0, 0.25)
		viewbox.pack_start(self.slider_scale, True, True, 0)
		self.slider_scale.connect("value-changed", self.on_update_slider)

		## offset slider
		label = Gtk.Label("Offset: ")
		viewbox.pack_start(label, False, False, 0)
		self.ajustment_offset = Gtk.Adjustment.new(0, 0, 10000, 1, 25, 0);
		self.slider_offset = Gtk.Scale.new(Gtk.Orientation.HORIZONTAL, self.ajustment_offset)
		viewbox.pack_start(self.slider_offset, True, True, 0)
		self.slider_offset.connect("value-changed", self.on_update_slider)
		self.slider_scale.set_value(2)
		self.slider_diff.set_value(0)
		self.slider_difft.set_value(0)
		return sliderbox

	def create_timeline(self):
		self.timeline = Gtk.DrawingArea()
		self.timeline.set_size_request(800, 200)
		self.timeline.add_events(Gdk.EventMask.EXPOSURE_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.BUTTON_PRESS_MASK|Gdk.EventMask.POINTER_MOTION_MASK|Gdk.EventMask.SCROLL_MASK)
		self.timeline.connect('draw', self.timeline_draw_event)
		self.timeline.connect('configure-event', self.timeline_configure_event)
		self.timeline.connect('button-press-event', self.timeline_clicked)
		return self.timeline

	def create_infobox(self):
		infobox = Gtk.Box()
		self.info_timestart = Gtk.Label("00:00:00.00")
		infobox.pack_start(self.info_timestart, False, False, 0)
		self.info_timestart.set_justify(Gtk.Justification.LEFT)
		self.info_timepos = Gtk.Label("00:00:00.00")
		infobox.pack_start(self.info_timepos, True, False, 0)
		self.info_timepos.set_justify(Gtk.Justification.LEFT)
		self.info_frame = Gtk.Label("00:00:00.00")
		infobox.pack_start(self.info_frame, True, False, 0)
		self.info_frame.set_justify(Gtk.Justification.LEFT)
		self.info_stamp = Gtk.Label("00:00:00.00")
		infobox.pack_start(self.info_stamp, True, False, 0)
		self.info_stamp.set_justify(Gtk.Justification.LEFT)
		self.info_timestop = Gtk.Label("00:00:00.00")
		infobox.pack_start(self.info_timestop, False, False, 0)
		self.info_timestart.set_justify(Gtk.Justification.RIGHT)
		return infobox

	def create_titlebar(self):
		hb = Gtk.HeaderBar()
		hb.set_show_close_button(True)
		hb.props.title = "Multicam-Sync-Tool"
		button = Gtk.Button()
		icon = Gio.ThemedIcon(name="mail-send-receive-symbolic")
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		button.add(image)
		hb.pack_end(button)
		box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		Gtk.StyleContext.add_class(box.get_style_context(), "linked")
		hb.pack_start(box)
		## Menuheader
		menubutton = Gtk.MenuButton.new()
		menumodel = Gio.Menu()
		menumodel.append("New", "app.new")
		menumodel.append("Open", "app.load")
		menumodel.append("Save", "app.save")
		menumodel.append("Save as", "app.save_as")
		menumodel.append("Import", "app.import")
		submenu = Gio.Menu()
		submenu.append("Xmeml", "app.export_xmeml")
		submenu.append("Kdenlive", "app.export_kdenlive")
		submenu.append("Openshot", "app.export_openshot")
		submenu.append("CSV", "app.export_csv")
		menumodel.append_submenu("Export", submenu)
		menumodel.append("Quit", "app.quit")
		menumodel.append("About", "app.about")
		menubutton.set_menu_model(menumodel)
		box.add(menubutton)
		quit_action = Gio.SimpleAction.new("quit", None)
		quit_action.connect("activate", self.quit_callback)
		self.add_action(quit_action)
		about_action = Gio.SimpleAction.new("about", None)
		about_action.connect("activate", self.about_callback)
		self.add_action(about_action)


		file_save_xmeml = Gio.SimpleAction.new("export_xmeml", None)
		file_save_xmeml.connect("activate", self.file_save_xmeml)
		self.add_action(file_save_xmeml)

		export_openshot = Gio.SimpleAction.new("export_openshot", None)
		export_openshot.connect("activate", self.file_save_openshot)
		self.add_action(export_openshot)

		export_kdenlive = Gio.SimpleAction.new("export_kdenlive", None)
		export_kdenlive.connect("activate", self.file_save_kdenlive)
		self.add_action(export_kdenlive)

		import_action = Gio.SimpleAction.new("import", None)
		import_action.connect("activate", self.import_folder)
		self.add_action(import_action)

		import_action = Gio.SimpleAction.new("new", None)
		import_action.connect("activate", self.poject_new)
		self.add_action(import_action)

		file_save_project = Gio.SimpleAction.new("save", None)
		file_save_project.connect("activate", self.file_save_project)
		self.add_action(file_save_project)

		file_save_project_as = Gio.SimpleAction.new("save_as", None)
		file_save_project_as.connect("activate", self.file_save_project_as)
		self.add_action(file_save_project_as)

		file_load_project = Gio.SimpleAction.new("load", None)
		file_load_project.connect("activate", self.file_load_project)
		self.add_action(file_load_project)

		return hb


	def video_widget_cv(self):
		video_w = Gtk.Image()
		video_w.set_from_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "empty.png"))
		return video_w


	def create_videobox(self):
		videobox = Gtk.Box()
		## List-Box
		self.listmodel_l = Gtk.ListStore(str, str, str, str)
		self.medialist_l = Gtk.TreeView(model=self.listmodel_l)
		scroll = Gtk.ScrolledWindow () # 1
		scroll.add (self.medialist_l)         # 2
		scroll.set_policy (Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
		videobox.pack_start(scroll, False, False, 0)
		## Video Image
		video_lbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.video_l = self.video_widget_cv()
		self.video_l.show()
		video_lbox.pack_start(self.video_l, False, False, 0)
		self.meta_l = Gtk.Label("----")
		video_lbox.pack_start(self.meta_l, False, False, 0)
		videobox.pack_start(video_lbox, True, True, 0)
		## Video Image
		video_rbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.video_r = self.video_widget_cv()
		self.video_r.show()
		video_rbox.pack_start(self.video_r, False, False, 0)
		self.meta_r = Gtk.Label("----")
		video_rbox.pack_start(self.meta_r, False, False, 0)
		videobox.pack_start(video_rbox, True, True, 0)
		## List-Box
		self.listmodel_r = Gtk.ListStore(str, str, str, str)
		self.medialist_r = Gtk.TreeView(model=self.listmodel_r)
		scroll = Gtk.ScrolledWindow () # 1
		scroll.add (self.medialist_r)         # 2
		scroll.set_policy (Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
		videobox.pack_start(scroll, False, False, 0)

		columns = ['Comment', 'FrmTrim']
		for i, column in enumerate(columns):
			treeviewcolumn = Gtk.TreeViewColumn(column)
			cellrenderertext = Gtk.CellRendererText()
			treeviewcolumn.pack_start(cellrenderertext, True)
			treeviewcolumn.add_attribute(cellrenderertext, "text", i)
			treeviewcolumn.add_attribute(cellrenderertext, "background", 2)
			self.medialist_l.append_column(treeviewcolumn)

			treeviewcolumn = Gtk.TreeViewColumn(column)
			cellrenderertext = Gtk.CellRendererText()
			treeviewcolumn.pack_start(cellrenderertext, True)
			treeviewcolumn.add_attribute(cellrenderertext, "text", i)
			treeviewcolumn.add_attribute(cellrenderertext, "background", 2)
			self.medialist_r.append_column(treeviewcolumn)


		self.selection = self.medialist_l.get_selection()
		self.selection.connect("changed", self.medialist_l_changed)

		self.selection = self.medialist_l.get_selection()
		self.selection.connect("changed", self.medialist_l_changed)


		return videobox

	def about_callback(self, action, parameter):
		print("You clicked \"About\"")

	def quit_callback(self, action, parameter):
		self.quit()



app = MultiCamSync()

exit_status = app.run()
sys.exit(exit_status)

