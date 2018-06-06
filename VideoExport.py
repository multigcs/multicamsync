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

class VideoExport:
	def __init__(self, vi):
		self.vi = vi


	def osp_point(self, x, y, interpolation):
		Point = {}
		Point["co"] = {}
		Point["co"]["X"] = x
		Point["co"]["Y"] = y
		Point["interpolation"] = interpolation
		return Point

	def osp_point2(self, x, y, interpolation, handle_type, left_x, left_y, right_x, right_y):
		Point = {}
		Point["co"] = {}
		Point["co"]["X"] = x
		Point["co"]["Y"] = y
		Point["interpolation"] = interpolation
		return Point


	def openshot(self, path, project):
		osp = {}
		osp["id"] = "T0"
		osp["fps"] = {}
		osp["fps"]["num"] = str(project["fps"])
		osp["fps"]["den"] = 1
		osp["width"] = 1920
		osp["height"] = 1080
		osp["sample_rate"] = 44100
		osp["channels"] = 2
		osp["channel_layout"] = 3
		osp["settings"] = {}

		osp["clips"] = []
		layer_n = 0
		for cid in project["tracks"]:
			cam = project["tracks"][cid]
			for fid in project["files"]:
				mov = project["files"][fid]
				if mov["trackid"] == cam["id"]:
					length = mov["duration"] * project["fps"]
					frm_begin = (mov["frm_begin"]) + project["tracks"][mov["trackid"]]["frm_trim"] + mov["frm_trim"]
					frm_end = frm_begin + length
					osp_clip = {}
					osp_clip["alpha"] = {}
					osp_clip["alpha"]["Points"] = []
					osp_clip["alpha"]["Points"].append(self.osp_point(1, 1, 2))
					osp_clip["anchor"] = 0
					osp_clip["channel_filter"] = {}
					osp_clip["channel_filter"]["Points"] = []
					osp_clip["channel_filter"]["Points"].append(self.osp_point(1, -1, 2))
					osp_clip["channel_mapping"] = {}
					osp_clip["channel_mapping"]["Points"] = []
					osp_clip["channel_mapping"]["Points"].append(self.osp_point(1, -1, 2))
					osp_clip["crop_height"] = {}
					osp_clip["crop_height"]["Points"] = []
					osp_clip["crop_height"]["Points"].append(self.osp_point(1, -1, 2))
					osp_clip["crop_wigth"] = {}
					osp_clip["crop_wigth"]["Points"] = []
					osp_clip["crop_wigth"]["Points"].append(self.osp_point(1, -1, 2))
					osp_clip["crop_x"] = {}
					osp_clip["crop_x"]["Points"] = []
					osp_clip["crop_x"]["Points"].append(self.osp_point(1, 0, 2))
					osp_clip["crop_y"] = {}
					osp_clip["crop_y"]["Points"] = []
					osp_clip["crop_y"]["Points"].append(self.osp_point(1, 0, 2))
					osp_clip["display"] = 0
					osp_clip["duration"] = (mov["frm_length"] / mov["fps"])
					osp_clip["effects"] = []
					osp_clip["end"] = (mov["frm_length"] / mov["fps"])
					osp_clip["gravity"] = 4
					osp_clip["has_audio"] = {}
					osp_clip["has_audio"]["Points"] = []
					osp_clip["has_audio"]["Points"].append(self.osp_point(1, -1, 2))
					osp_clip["has_video"] = {}
					osp_clip["has_video"]["Points"] = []
					osp_clip["has_video"]["Points"].append(self.osp_point(1, -1, 2))
					osp_clip["id"] = str(mov["id"])
					osp_clip["layer"] = layer_n
					osp_clip["location_x"] = {}
					osp_clip["location_x"]["Points"] = []
					osp_clip["location_x"]["Points"].append(self.osp_point(1, 0, 2))
					osp_clip["location_y"] = {}
					osp_clip["location_y"]["Points"] = []
					osp_clip["location_y"]["Points"].append(self.osp_point(1, 0, 2))
					osp_clip["perspective_c1_x"] = {}
					osp_clip["perspective_c1_x"]["Points"] = []
					osp_clip["perspective_c1_x"]["Points"].append(self.osp_point(1, -1, 2))
					osp_clip["perspective_c1_y"] = {}
					osp_clip["perspective_c1_y"]["Points"] = []
					osp_clip["perspective_c1_y"]["Points"].append(self.osp_point(1, -1, 2))
					osp_clip["perspective_c2_x"] = {}
					osp_clip["perspective_c2_x"]["Points"] = []
					osp_clip["perspective_c2_x"]["Points"].append(self.osp_point(1, -1, 2))
					osp_clip["perspective_c2_y"] = {}
					osp_clip["perspective_c2_y"]["Points"] = []
					osp_clip["perspective_c2_y"]["Points"].append(self.osp_point(1, -1, 2))
					osp_clip["perspective_c3_x"] = {}
					osp_clip["perspective_c3_x"]["Points"] = []
					osp_clip["perspective_c3_x"]["Points"].append(self.osp_point(1, -1, 2))
					osp_clip["perspective_c3_y"] = {}
					osp_clip["perspective_c3_y"]["Points"] = []
					osp_clip["perspective_c3_y"]["Points"].append(self.osp_point(1, -1, 2))
					osp_clip["perspective_c4_x"] = {}
					osp_clip["perspective_c4_x"]["Points"] = []
					osp_clip["perspective_c4_x"]["Points"].append(self.osp_point(1, -1, 2))
					osp_clip["perspective_c4_y"] = {}
					osp_clip["perspective_c4_y"]["Points"] = []
					osp_clip["perspective_c4_y"]["Points"].append(self.osp_point(1, -1, 2))
					osp_clip["position"] = frm_begin / project["fps"]
					osp_clip["reader"] = {}
					osp_clip["reader"]["acodec"] = "pcm_s16le"
					osp_clip["reader"]["audio_bit_rate"] = 1536000
					osp_clip["reader"]["audio_stream_index"] = 1
					osp_clip["reader"]["audio_timebase"] = {}
					osp_clip["reader"]["audio_timebase"]["den"] = mov["ahz"]
					osp_clip["reader"]["audio_timebase"]["num"] = 1
					osp_clip["reader"]["channel_layout"] = 3
					osp_clip["reader"]["channels"] = 2
					osp_clip["reader"]["display_ratio"] = {}
					osp_clip["reader"]["display_ratio"]["den"] = 9
					osp_clip["reader"]["display_ratio"]["num"] = 16
					osp_clip["reader"]["duration"] = mov["frm_length"] / mov["fps"]
					osp_clip["reader"]["file_size"] =  mov["size"]
					osp_clip["reader"]["fps"] = {}
					osp_clip["reader"]["fps"]["den"] = 1
					osp_clip["reader"]["fps"]["num"] = mov["fps"]
					osp_clip["reader"]["has_audio"] = True
					osp_clip["reader"]["has_single_image"] = False
					osp_clip["reader"]["has_video"] = True
					osp_clip["reader"]["height"] = mov["height"]
					osp_clip["reader"]["interlaced_frame"] = False
					osp_clip["reader"]["path"] = mov["path"]
					osp_clip["reader"]["pixel_format"] = 12
					osp_clip["reader"]["pixel_ratio"] = {}
					osp_clip["reader"]["pixel_ratio"]["den"] = 1
					osp_clip["reader"]["pixel_ratio"]["num"] = 1
					osp_clip["reader"]["sample_rate"] = mov["ahz"]
					osp_clip["reader"]["top_field_first"] = True
					osp_clip["reader"]["type"] = "FFmpegReader"
					osp_clip["reader"]["vcodec"] = "h264"
					osp_clip["reader"]["video_bit_rate"] = 46166220
					osp_clip["reader"]["video_length"] = mov["duration"]
					osp_clip["reader"]["video_stream_index"] = 0
					osp_clip["reader"]["video_timebase"] = {}
					osp_clip["reader"]["video_timebase"]["den"] = (mov["fps"] * 1000)
					osp_clip["reader"]["video_timebase"]["num"] = 1
					osp_clip["reader"]["width"] = mov["width"]
					osp_clip["rotation"] = {}
					osp_clip["rotation"]["Points"] = []
					osp_clip["rotation"]["Points"].append(self.osp_point(1, 0, 2))
					osp_clip["scale"] = 1
					osp_clip["scale_x"] = {}
					osp_clip["scale_x"]["Points"] = []
					osp_clip["scale_x"]["Points"].append(self.osp_point(1, 1, 2))
					osp_clip["scale_y"] = {}
					osp_clip["scale_y"]["Points"] = []
					osp_clip["scale_y"]["Points"].append(self.osp_point(1, 1, 2))
					osp_clip["shear_x"] = {}
					osp_clip["shear_x"]["Points"] = []
					osp_clip["shear_x"]["Points"].append(self.osp_point(1, 1, 2))
					osp_clip["shear_y"] = {}
					osp_clip["shear_y"]["Points"] = []
					osp_clip["shear_y"]["Points"].append(self.osp_point(1, 1, 2))
					osp_clip["start"] = 0
					osp_clip["time"] = {}
					osp_clip["time"]["Points"] = []
					osp_clip["time"]["Points"].append(self.osp_point(1, 1, 2))
					osp_clip["volume"] = {}
					osp_clip["volume"]["Points"] = []
					osp_clip["volume"]["Points"].append(self.osp_point(1, 1, 2))

					osp_clip["wave_color"] = {}
					osp_clip["wave_color"]["alpha"] = {}
					osp_clip["wave_color"]["alpha"]["Points"] = []
					osp_clip["wave_color"]["alpha"]["Points"].append(self.osp_point2(1, 255, 0, 0, 0.5, 1, 0.5, 0))
					osp_clip["wave_color"]["blue"] = {}
					osp_clip["wave_color"]["blue"]["Points"] = []
					osp_clip["wave_color"]["blue"]["Points"].append(self.osp_point2(1, 255, 0, 0, 0.5, 1, 0.5, 0))
					osp_clip["wave_color"]["green"] = {}
					osp_clip["wave_color"]["green"]["Points"] = []
					osp_clip["wave_color"]["green"]["Points"].append(self.osp_point2(1, 123, 0, 0, 0.5, 1, 0.5, 0))
					osp_clip["wave_color"]["red"] = {}
					osp_clip["wave_color"]["red"]["Points"] = []
					osp_clip["wave_color"]["red"]["Points"].append(self.osp_point2(1, 0, 0, 0, 0.5, 1, 0.5, 0))

					osp_clip["waveform"] = False
					osp_clip["file_id"] = str(mov["id"])
					osp_clip["title"] = str(mov["name"])
					if os.path.isfile(os.path.splitext(mov["path"])[0] + ".THM"):
						osp_clip["image"] = os.path.splitext(mov["path"])[0] + ".THM"
					else:
						osp_clip["image"] = "../home/dippel/.openshot_qt/thumbnail/" + str(mov["id"]) + ".png"
					osp["clips"].append(osp_clip)
			layer_n += 1

		osp["effects"] = []
		osp["export_path"] = ""

		osp["files"] = []
		for fid in project["files"]:
			mov = project["files"][fid]
			osp_file = {}
			osp_file["acodec"] = "pcm_s16le"
			osp_file["audio_bit_rate"] = 1536000
			osp_file["audio_stream_index"] = 1
			osp_file["audio_timebase"] = {}
			osp_file["audio_timebase"]["den"] = 48000
			osp_file["audio_timebase"]["num"] = 1
			osp_file["channel_layout"] = 3
			osp_file["channels"] = 2
			osp_file["display_ratio"] = {}
			osp_file["display_ratio"]["den"] = 9
			osp_file["display_ratio"]["num"] = 16
			osp_file["duration"] = (mov["frm_length"] / mov["fps"])
			osp_file["file_size"] = "2131263557"
			osp_file["fps"] = {}
			osp_file["fps"]["den"] = 1
			osp_file["fps"]["num"] = mov["fps"]
			osp_file["has_audio"] = True
			osp_file["has_single_image"] = False
			osp_file["has_video"] = True
			osp_file["height"] = 1080
			osp_file["interlaced_frame"] = False
			osp_file["path"] = mov["path"]
			osp_file["pixel_format"] = 12
			osp_file["pixel_ratio"] = {}
			osp_file["pixel_ratio"]["den"] = 1
			osp_file["pixel_ratio"]["num"] = 1
			osp_file["sample_rate"] = 48000
			osp_file["top_field_first"] = True
			osp_file["type"] = "FFmpegReader"
			osp_file["vcodec"] = "h264"
			osp_file["video_bit_rate"] = 46166220
			osp_file["video_length"] = "9233"
			osp_file["video_stream_index"] = 0
			osp_file["video_timebase"] = {}
			osp_file["video_timebase"]["den"] = 25000
			osp_file["video_timebase"]["num"] = 1
			osp_file["width"] = 1920
			osp_file["media_type"] = "video"
			osp_file["id"] = str(mov["id"])
			osp["files"].append(osp_file)

		osp["duration"] = 99999
		osp["scale"] = 56
		osp["tick_pixels"] = 100
		osp["playhead_position"] = 0
		osp["profile"] = "HDV 1080 25p"

		osp["layers"] = []
		layer_n = 0
		for cid in project["tracks"]:
			cam = project["tracks"][cid]
			osp_layer = {}
			osp_layer["number"] = layer_n
			osp_layer["y"] = 0
			osp_layer["label"] = str(cam["name"])
			osp_layer["lock"] = False
			osp_layer["id"] = str(cam["name"])
			osp["layers"].append(osp_layer)
			layer_n += 1

		osp["markers"] = []
		osp["progress"] = []
		osp["history"] = {}
		osp["version"] = {}
		osp["version"]["openshot-qt"] = "2.4.1"
		osp["version"]["libopenshot"] = "0.1.9"

		jsondata = json.dumps(osp, indent=4, separators=(',', ': '))
		file = open(path, "w") 
		file.write(jsondata) 
		file.close() 



	def kdenlive(self, path, project):
		output = open(path, "w")
		if output:
			output.write("<?xml version='1.0' encoding='utf-8'?>\n")
			output.write("<mlt title=\"Anonymous Submission\" version=\"6.6.0\" root=\"/tmp\" producer=\"main bin\" LC_NUMERIC=\"de_DE.UTF-8\">\n")
			output.write(" <profile width=\"1920\" frame_rate_den=\"1\" height=\"1080\" display_aspect_num=\"16\" display_aspect_den=\"9\" frame_rate_num=\"" + str(project["fps"]) + "\" colorspace=\"709\" sample_aspect_den=\"1\" description=\"HD 1080p " + str(project["fps"]) + " fps\" progressive=\"1\" sample_aspect_num=\"1\"/>\n")
			for fid in project["files"]:
				mov = project["files"][fid]
				output.write(" <producer id=\"" + str(mov["id"]) + "\" out=\"" + str(mov["frm_length"]) + "\" in=\"0\">\n")
				output.write("  <property name=\"length\">" + str(mov["frm_length"]) + "</property>\n")
				output.write("  <property name=\"eof\">pause</property>\n")
				output.write("  <property name=\"resource\">" + mov["path"] + "</property>\n")
				output.write("  <property name=\"seekable\">1</property>\n")
				output.write("  <property name=\"aspect_ratio\">1</property>\n")
				output.write("  <property name=\"audio_index\">1</property>\n")
				output.write("  <property name=\"video_index\">0</property>\n")
				output.write("  <property name=\"mute_on_pause\">1</property>\n")
				output.write("  <property name=\"kdenlive:folderid\">" + str(mov["trackid"]) + "</property>\n")
				output.write("  <property name=\"kdenlive:clipname\">" + mov["track"] + "-" + mov["name"] + "</property>\n")
				output.write("  <property name=\"kdenlive:description\">" + mov["camname"] + "\n" + mov["lens"] + "</property>\n")
				output.write(" </producer>\n")
			output.write(" <playlist id=\"main bin\">\n")
			for cid in project["tracks"]:
				cam = project["tracks"][cid]
				output.write("  <property name=\"kdenlive:folder.-1." + str(cam["id"]) + "\">" + str(cam["name"]) + "</property>\n")
			output.write("  <property name=\"kdenlive:docproperties.audiotargettrack\">2</property>\n")
			output.write("  <property name=\"kdenlive:docproperties.decimalPoint\">,</property>\n")
			output.write("  <property name=\"kdenlive:docproperties.dirtypreviewchunks\"/>\n")
			output.write("  <property name=\"kdenlive:docproperties.disablepreview\">0</property>\n")
			output.write("  <property name=\"kdenlive:docproperties.documentid\">1526288607975</property>\n")
			output.write("  <property name=\"kdenlive:docproperties.enableproxy\">0</property>\n")
			output.write("  <property name=\"kdenlive:docproperties.generateimageproxy\">0</property>\n")
			output.write("  <property name=\"kdenlive:docproperties.generateproxy\">0</property>\n")
			output.write("  <property name=\"kdenlive:docproperties.kdenliveversion\">17.12.3</property>\n")
			output.write("  <property name=\"kdenlive:docproperties.position\">0</property>\n")
			output.write("  <property name=\"kdenlive:docproperties.previewchunks\"/>\n")
			output.write("  <property name=\"kdenlive:docproperties.previewextension\"/>\n")
			output.write("  <property name=\"kdenlive:docproperties.previewparameters\"/>\n")
			output.write("  <property name=\"kdenlive:docproperties.profile\">atsc_1080p_" + str(project["fps"]) + "</property>\n")
			output.write("  <property name=\"kdenlive:docproperties.proxyextension\">mkv</property>\n")
			output.write("  <property name=\"kdenlive:docproperties.proxyimageminsize\">2000</property>\n")
			output.write("  <property name=\"kdenlive:docproperties.proxyminsize\">1000</property>\n")
			output.write("  <property name=\"kdenlive:docproperties.proxyparams\">-vf yadif,scale=960:-2 -qscale 3 -vcodec mjpeg -acodec pcm_s16le</property>\n")
			output.write("  <property name=\"kdenlive:docproperties.version\">0.96</property>\n")
			output.write("  <property name=\"kdenlive:docproperties.verticalzoom\">1</property>\n")
			output.write("  <property name=\"kdenlive:docproperties.videotargettrack\">3</property>\n")
			output.write("  <property name=\"kdenlive:docproperties.zonein\">0</property>\n")
			output.write("  <property name=\"kdenlive:docproperties.zoneout\">100</property>\n")
			output.write("  <property name=\"kdenlive:docproperties.zoom\">7</property>\n")
			output.write("  <property name=\"kdenlive:documentnotes\"/>\n")
			output.write("  <property name=\"kdenlive:clipgroups\"/>\n")
			output.write("  <property name=\"xml_retain\">1</property>\n")
			for fid in project["files"]:
				mov = project["files"][fid]
				output.write("  <entry out=\"" + str(mov["frm_length"]) + "\" producer=\"" + str(mov["id"]) + "\" in=\"0\"/>\n")
			output.write(" </playlist>\n")
			output.write(" <producer id=\"black\" out=\"500\" in=\"0\">\n")
			output.write("  <property name=\"length\">15000</property>\n")
			output.write("  <property name=\"eof\">pause</property>\n")
			output.write("  <property name=\"resource\">black</property>\n")
			output.write("  <property name=\"aspect_ratio\">0</property>\n")
			output.write("  <property name=\"mlt_service\">colour</property>\n")
			output.write("  <property name=\"set.test_audio\">0</property>\n")
			output.write(" </producer>\n")
			output.write(" <playlist id=\"black_track\">\n")
			output.write("  <entry out=\"1\" producer=\"black\" in=\"0\"/>\n")
			output.write(" </playlist>\n")
			for fid in project["files"]:
				mov = project["files"][fid]
				pid = str(mov["id"]) + "_playlist" + str(mov["trackid"])
				output.write(" <producer id=\"" + pid + "\" title=\"Anonymous Submission\" out=\"" + str(mov["frm_length"]) + "\" in=\"0\">\n")
				output.write("  <property name=\"length\">" + str(mov["frm_length"]) + "</property>\n")
				output.write("  <property name=\"eof\">pause</property>\n")
				output.write("  <property name=\"resource\">" + mov["path"] + "</property>\n")
				output.write("  <property name=\"audio_index\">1</property>\n")
				output.write("  <property name=\"video_index\">0</property>\n")
				output.write("  <property name=\"mute_on_pause\">1</property>\n")
				output.write("  <property name=\"mlt_service\">avformat-novalidate</property>\n")
				output.write("  <property name=\"seekable\">1</property>\n")
				output.write("  <property name=\"aspect_ratio\">1</property>\n")
				output.write("  <property name=\"kdenlive:folderid\">" + str(mov["trackid"]) + "</property>\n")
				output.write("  <property name=\"global_feed\">1</property>\n")
				output.write("  <property name=\"xml\">was here</property>\n")
				output.write("  <property name=\"meta.media.nb_streams\">3</property>\n")
				output.write("  <property name=\"meta.media.0.stream.type\">video</property>\n")
				output.write("  <property name=\"meta.media.0.stream.frame_rate\">" + str(mov["fps"]) + "</property>\n")
				output.write("  <property name=\"meta.media.0.stream.sample_aspect_ratio\">0</property>\n")
				output.write("  <property name=\"meta.media.0.codec.width\">1920</property>\n")
				output.write("  <property name=\"meta.media.0.codec.height\">1080</property>\n")
				output.write("  <property name=\"meta.media.0.codec.rotate\">0</property>\n")
				output.write("  <property name=\"meta.media.0.codec.frame_rate\">" + str(mov["fps"]) + "000</property>\n")
				output.write("  <property name=\"meta.media.0.codec.pix_fmt\">yuvj420p</property>\n")
				output.write("  <property name=\"meta.media.0.codec.sample_aspect_ratio\">1</property>\n")
				output.write("  <property name=\"meta.media.0.codec.colorspace\">709</property>\n")
				output.write("  <property name=\"meta.media.0.codec.color_trc\">1</property>\n")
				output.write("  <property name=\"meta.media.0.codec.name\">h264</property>\n")
				output.write("  <property name=\"meta.media.0.codec.long_name\">H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10</property>\n")
				output.write("  <property name=\"meta.media.0.codec.bit_rate\">28006267</property>\n")
				output.write("  <property name=\"meta.attr.0.stream.creation_time.markup\">2018-05-09T23:50:49.000000Z</property>\n")
				output.write("  <property name=\"meta.attr.0.stream.language.markup\">eng</property>\n")
				output.write("  <property name=\"meta.attr.0.stream.timecode.markup\">09:49:22:10</property>\n")
				output.write("  <property name=\"meta.attr.major_brand.markup\">qt  </property>\n")
				output.write("  <property name=\"meta.attr.minor_version.markup\">537331968</property>\n")
				output.write("  <property name=\"meta.attr.compatible_brands.markup\">qt  CAEP</property>\n")
				output.write("  <property name=\"meta.media.sample_aspect_num\">1</property>\n")
				output.write("  <property name=\"meta.media.sample_aspect_den\">1</property>\n")
				output.write("  <property name=\"meta.media.frame_rate_num\">" + str(mov["fps"]) + "</property>\n")
				output.write("  <property name=\"meta.media.frame_rate_den\">1</property>\n")
				output.write("  <property name=\"meta.media.colorspace\">709</property>\n")
				output.write("  <property name=\"meta.media.color_trc\">1</property>\n")
				output.write("  <property name=\"meta.media.width\">1920</property>\n")
				output.write("  <property name=\"meta.media.height\">1080</property>\n")
				output.write("  <property name=\"meta.media.top_field_first\">0</property>\n")
				output.write("  <property name=\"meta.media.progressive\">1</property>\n")
				output.write(" </producer>\n")
			for cid in project["tracks"]:
				cam = project["tracks"][cid]
				output.write(" <playlist id=\"playlist" + str(cam["id"]) + "\">\n")
				output.write("  <property name=\"kdenlive:track_name\">CAM: " + str(cam["name"]) + "</property>\n")
				last_frame = 0
				for fid in project["files"]:
					mov = project["files"][fid]
					if mov["trackid"] == cam["id"]:
						pid = str(mov["id"]) + "_playlist" + str(mov["trackid"])
						length = mov["duration"] * project["fps"]
						frm_begin = (mov["frm_begin"]) + project["tracks"][mov["trackid"]]["frm_trim"] + mov["frm_trim"]
						frm_end = frm_begin + length
						diff = frm_begin - last_frame
						output.write("  <blank length=\"" + str(int(diff)) + "\"/>\n")
						output.write("  <entry out=\"" + str(length) + "\" producer=\"" + pid + "\" in=\"0\"/>\n")
						last_frame = frm_end
				output.write(" </playlist>\n")
			output.write(" <tractor id=\"maintractor\" title=\"Anonymous Submission\" global_feed=\"1\" out=\"1\" in=\"0\">\n")
			output.write("  <track producer=\"black_track\"/>\n")
			for cid in project["tracks"]:
				cam = project["tracks"][cid]
				output.write("  <track producer=\"playlist" + str(cam["id"]) + "\"/>\n")
			output.write("  <transition id=\"transition0\">\n")
			output.write("   <property name=\"a_track\">0</property>\n")
			output.write("   <property name=\"b_track\">1</property>\n")
			output.write("   <property name=\"mlt_service\">mix</property>\n")
			output.write("   <property name=\"always_active\">1</property>\n")
			output.write("   <property name=\"sum\">1</property>\n")
			output.write("   <property name=\"internal_added\">237</property>\n")
			output.write("  </transition>\n")
			output.write("  <transition id=\"transition1\">\n")
			output.write("   <property name=\"a_track\">0</property>\n")
			output.write("   <property name=\"b_track\">2</property>\n")
			output.write("   <property name=\"mlt_service\">mix</property>\n")
			output.write("   <property name=\"always_active\">1</property>\n")
			output.write("   <property name=\"sum\">1</property>\n")
			output.write("   <property name=\"internal_added\">237</property>\n")
			output.write("  </transition>\n")
			output.write("  <transition id=\"transition2\">\n")
			output.write("   <property name=\"a_track\">0</property>\n")
			output.write("   <property name=\"b_track\">3</property>\n")
			output.write("   <property name=\"mlt_service\">mix</property>\n")
			output.write("   <property name=\"always_active\">1</property>\n")
			output.write("   <property name=\"sum\">1</property>\n")
			output.write("   <property name=\"internal_added\">237</property>\n")
			output.write("  </transition>\n")
			output.write("  <transition id=\"transition3\">\n")
			output.write("   <property name=\"a_track\">0</property>\n")
			output.write("   <property name=\"b_track\">3</property>\n")
			output.write("   <property name=\"compositing\">0</property>\n")
			output.write("   <property name=\"distort\">0</property>\n")
			output.write("   <property name=\"rotate_center\">0</property>\n")
			output.write("   <property name=\"mlt_service\">qtblend</property>\n")
			output.write("   <property name=\"internal_added\">237</property>\n")
			output.write("  </transition>\n")
			output.write("  <transition id=\"transition4\">\n")
			output.write("   <property name=\"a_track\">0</property>\n")
			output.write("   <property name=\"b_track\">4</property>\n")
			output.write("   <property name=\"mlt_service\">mix</property>\n")
			output.write("   <property name=\"always_active\">1</property>\n")
			output.write("   <property name=\"sum\">1</property>\n")
			output.write("   <property name=\"internal_added\">237</property>\n")
			output.write("  </transition>\n")
			output.write("  <transition id=\"transition5\">\n")
			output.write("   <property name=\"a_track\">0</property>\n")
			output.write("   <property name=\"b_track\">4</property>\n")
			output.write("   <property name=\"compositing\">0</property>\n")
			output.write("   <property name=\"distort\">0</property>\n")
			output.write("   <property name=\"rotate_center\">0</property>\n")
			output.write("   <property name=\"mlt_service\">qtblend</property>\n")
			output.write("   <property name=\"internal_added\">237</property>\n")
			output.write("  </transition>\n")
			output.write("  <transition id=\"transition6\">\n")
			output.write("   <property name=\"a_track\">0</property>\n")
			output.write("   <property name=\"b_track\">5</property>\n")
			output.write("   <property name=\"mlt_service\">mix</property>\n")
			output.write("   <property name=\"always_active\">1</property>\n")
			output.write("   <property name=\"sum\">1</property>\n")
			output.write("   <property name=\"internal_added\">237</property>\n")
			output.write("  </transition>\n")
			output.write("  <transition id=\"transition7\">\n")
			output.write("   <property name=\"a_track\">0</property>\n")
			output.write("   <property name=\"b_track\">5</property>\n")
			output.write("   <property name=\"compositing\">0</property>\n")
			output.write("   <property name=\"distort\">0</property>\n")
			output.write("   <property name=\"rotate_center\">0</property>\n")
			output.write("   <property name=\"mlt_service\">qtblend</property>\n")
			output.write("   <property name=\"internal_added\">237</property>\n")
			output.write("  </transition>\n")
			output.write(" </tractor>\n")
			output.write("</mlt>\n")
			output.close()

	def xmeml(self, path, project):
		output = open(path, "w")
		if output:
			output.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
			output.write("<xmeml version=\"5\">\n")
			output.write("   <sequence id=\"E70B00O2\">\n")
			output.write("      <name>Sequence #1</name>\n")
			output.write("      <rate>\n")
			output.write("         <ntsc>FALSE</ntsc>\n")
			output.write("         <timebase>" + str(project["fps"]) + "</timebase>\n")
			output.write("      </rate>\n")
			output.write("      <timecode>\n")
			output.write("         <rate>\n")
			output.write("            <ntsc>FALSE</ntsc>\n")
			output.write("            <timebase>25</timebase>\n")
			output.write("         </rate>\n")
			output.write("         <string>00:00:00.00</string>\n")
			output.write("         <frame>0</frame>\n")
			output.write("         <source>source</source>\n")
			output.write("         <displayformat>NDF</displayformat>\n")
			output.write("      </timecode>\n")
			output.write("      <media>\n")
			output.write("         <format>\n")
			output.write("            <samplecharacteristics>\n")
			output.write("               <width>1920</width>\n")
			output.write("               <height>1080</height>\n")
			output.write("            </samplecharacteristics>\n")
			output.write("         </format>\n")
			output.write("         <video>\n")
			for cid in project["tracks"]:
				cam = project["tracks"][cid]
				output.write("            <track>\n")
				for fid in project["files"]:
					mov = project["files"][fid]
					if mov["trackid"] == cam["id"]:
						pid = str(mov["id"]) + "_playlist" + str(mov["trackid"])
						length = mov["frm_length"]
						frm_begin = (mov["frm_begin"]) + project["tracks"][mov["trackid"]]["frm_trim"] + mov["frm_trim"]
						frm_end = frm_begin + length
						output.write("               <clipitem>\n")
						output.write("                  <name>" + str(mov["name"]) + "</name>\n")
						output.write("                  <duration>" + str(length) + "</duration>\n")
						output.write("                  <rate>\n")
						output.write("                     <ntsc>FALSE</ntsc>\n")
						output.write("                     <timebase>" + str(mov["fps"]) + "</timebase>\n")
						output.write("                  </rate>\n")
						output.write("                  <in>0</in>\n")
						output.write("                  <out>" + str(length) + "</out>\n")
						output.write("                  <start>" + str(frm_begin) + "</start>\n")
						output.write("                  <end>" + str(frm_end) + "</end>\n")
						output.write("                  <masterclipid>" + str(cam["name"]) + "-" + str(mov["name"]) + "</masterclipid>\n")
						output.write("                  <file id=\"" + str(cam["name"]) + "-" + str(mov["name"]) + "\">\n")
						output.write("                     <name>" + str(mov["name"]) + "</name>\n")
#						output.write("                     <pathurl>file://localhost/" + str(mov["path"]) + "</pathurl>\n")
						output.write("                     <pathurl>file://localhost" + str(mov["path"]) + "</pathurl>\n")
						output.write("                     <rate>\n")
						output.write("                        <ntsc>FALSE</ntsc>\n")
						output.write("                        <timebase>" + str(mov["fps"]) + "</timebase>\n")
						output.write("                     </rate>\n")
						output.write("                     <duration>" + str(length) + "</duration>\n")
						output.write("                     <timecode>\n")
						output.write("                        <rate>\n")
						output.write("                           <ntsc>FALSE</ntsc>\n")
						output.write("                           <timebase>" + str(mov["fps"]) + "</timebase>\n")
						output.write("                        </rate>\n")
						output.write("                        <string>00:00:00.00</string>\n")
						output.write("                        <frame>0</frame>\n")
						output.write("                        <source>source</source>\n")
						output.write("                        <displayformat>NDF</displayformat>\n")
						output.write("                        <reel>\n")
						output.write("                           <name>" + str(mov["name"]) + "</name>\n")
						output.write("                        </reel>\n")
						output.write("                     </timecode>\n")
						output.write("                     <media>\n")
						output.write("                        <video>\n")
						output.write("                           <duration>" + str(length) + "</duration>\n")
						output.write("                           <samplecharacteristics>\n")
						output.write("                              <width>1920</width>\n")
						output.write("                              <height>1080</height>\n")
						output.write("                           </samplecharacteristics>\n")
						output.write("                        </video>\n")
						output.write("                        <audio>\n")
						output.write("                           <channelcount>2</channelcount>\n")
						output.write("                        </audio>\n")
						output.write("                     </media>\n")
						output.write("                  </file>\n")
						output.write("                  <sourcetrack>\n")
						output.write("                     <mediatype>video</mediatype>\n")
						output.write("                  </sourcetrack>\n")
						output.write("               </clipitem>\n")
				output.write("            </track>\n")
			output.write("         </video>\n")
			output.write("         <audio>\n")
			output.write("         </audio>\n")
			output.write("      </media>\n")
			output.write("   </sequence>\n")
			output.write("</xmeml>\n")

