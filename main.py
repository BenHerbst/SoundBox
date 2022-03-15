#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import os, sys
import vlc
import time
import _thread
import stagger

DRAG_ACTION = Gdk.DragAction.COPY

class GUI:
    def __init__(self):
        self.window = Gtk.Window()
        self.window.set_default_size(500, 500)
        self.window.set_keep_above(True)
        self.window.connect("destroy", Gtk.main_quit)
        self.window.set_title("SoundBox")

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

        self.p = None

        self.overlay.show_all()
        self.window.show_all()

    def check_position( player ):
        while 1:
            if player.p.get_position() > 0.99:
                player.p.set_position(0.0)

    def on_drag_data_received(self, widget, drag_context, x,y, data,info, time):
        self.paused = False
        location = data.get_text().replace("%20", " ").replace("%C3%B6", "ö").strip()
        mp3 = stagger.read_tag(location.replace("file://", ""))
        self.window.set_title("SoundBox - " + mp3.title + " by " + mp3.artist)
        if self.p is None:
            self.p = vlc.MediaPlayer(location)
            self.overlay.remove(self.label)
            self.overlay.add(self.button)
            self.overlay.show_all()
        else:
            media = vlc.Media(location)
            self.p.set_media(media)
        self.p.play()
        self.button.set_image(Gtk.Image(stock=Gtk.STOCK_MEDIA_PAUSE))
        _thread.start_new_thread( self.check_position, ( ))

    def play_pause(self, widget):
        if self.paused == False:
            self.button.set_image(Gtk.Image(stock=Gtk.STOCK_MEDIA_PLAY))
            self.p.pause()
            self.paused = True
        elif self.paused == True:
            self.button.set_image(Gtk.Image(stock=Gtk.STOCK_MEDIA_PAUSE))
            self.p.play()
            self.paused = False

def main():
    app = GUI()
    Gtk.main()

if __name__ == "__main__":
    sys.exit(main())
