#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
import os, sys
import vlc
import time
import _thread
import stagger
import io
from PIL import Image

DRAG_ACTION = Gdk.DragAction.COPY

class GUI:
    def __init__(self):
        self.window = Gtk.Window()
        self.window.set_default_size(500, 500)
        self.window.set_keep_above(True)
        self.window.connect("destroy", Gtk.main_quit)
        self.window.set_title("SoundBox")
        self.window.set_resizable(False)
        self.window.set_decorated(False)
        self.window.connect("button-press-event", self.button_press)
        self.window.connect("key-press-event", self.key_press)

        self.overlay = Gtk.Overlay()
        self.overlay.drag_dest_set(Gtk.DestDefaults.ALL, [], DRAG_ACTION)
        self.overlay.drag_dest_add_text_targets()
        self.overlay.drag_source_add_text_targets()
        self.overlay.connect("drag-data-received", self.on_drag_data_received)
        self.window.add(self.overlay)


        self.label = Gtk.Label(label="Please drop your audio file here.")
        self.overlay.add(self.label)

        play_image = Gtk.Image(stock=Gtk.STOCK_OPEN)
        self.button = Gtk.Button(None,image=Gtk.Image(stock=Gtk.STOCK_MEDIA_PAUSE))
        self.button.connect("clicked", self.play_pause)
        self.button.set_valign(Gtk.Align.CENTER)
        self.button.set_halign(Gtk.Align.CENTER)
        self.button.set_focus_on_click(False)

        self.image = Gtk.Image()

        self.p = None

        self.overlay.show_all()
        self.window.show_all()

        if len(sys.argv) > 1:
            self.play_music(sys.argv[1])

    def check_position( player ):
        while 1:
            if player.p.get_position() > 0.99:
                player.p.set_position(0.0)


    def image2pixbuf(fr, im):
        """Convert Pillow image to GdkPixbuf"""
        data = im.tobytes()
        w, h = im.size
        data = GLib.Bytes.new(data)
        pix = GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB,
            False, 8, w, h, w * 3)
        return pix

    def on_drag_data_received(self, widget, drag_context, x,y, data,info, time):
        self.play_music(data.get_text())

    def play_music(widget, path):
        widget.paused = False
        location = path.replace("%20", " ").replace("%C3%B6", "ö").replace("%C3%A4", "ä").strip()
        mp3 = stagger.read_tag(location.replace("file://", ""))
        by_data = mp3[stagger.id3.APIC][0].data
        image = io.BytesIO(by_data)
        image_file = Image.open(image)
        image_crop_x = (image_file.size[0] / 2) - (image_file.size[1] / 2)
        pixbuf = widget.image2pixbuf(image_file.crop( (image_crop_x, 0, image_file.size[1] + image_crop_x, image_file.size[1])).resize( (500, 500)))
        widget.image.set_from_pixbuf(pixbuf)


        widget.window.set_title("SoundBox - " + mp3.title + " by " + mp3.artist)
        if widget.p is None:
            widget.p = vlc.MediaPlayer(location)
            widget.overlay.remove(widget.label)
            widget.overlay.add_overlay(widget.image)
            widget.overlay.add_overlay(widget.button)
            widget.overlay.show_all()
        else:
            media = vlc.Media(location)
            widget.p.set_media(media)
        widget.p.play()
        widget.button.set_image(Gtk.Image(stock=Gtk.STOCK_MEDIA_PAUSE))
        _thread.start_new_thread( widget.check_position, ( ))

    def play_pause(self, widget):
        if self.paused == False:
            self.button.set_image(Gtk.Image(stock=Gtk.STOCK_MEDIA_PLAY))
            self.p.pause()
            self.paused = True
        elif self.paused == True:
            self.button.set_image(Gtk.Image(stock=Gtk.STOCK_MEDIA_PAUSE))
            self.p.play()
            self.paused = False

    def button_press(widget, event, data):
        if (data.button == 1):
            event.begin_move_drag (data.button, data.x_root, data.y_root, data.time)
            return True
        return False

    def key_press(widget, event, data):
        skip = 0.01
        if widget.p != None:
            if data.keyval == 0x020 or data.keyval == 0x06b:
                widget.play_pause(data)
            elif data.keyval == 0x06c:
                widget.p.set_position(widget.p.get_position() + skip)
            elif data.keyval == 0x06a:
                widget.p.set_position(widget.p.get_position() - skip)

def main():
    app = GUI()
    Gtk.main()

if __name__ == "__main__":
    sys.exit(main())
