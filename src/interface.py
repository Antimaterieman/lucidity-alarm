#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk
import multiprocessing
from collections import namedtuple
import time

from main import Main, parse_time

class Interface():
    def __init__(self):
        gladeFile = 'main.glade'
        self.builder = gtk.Builder()
        self.builder.add_from_file(gladeFile)
        self.main = None

        enable = self.builder.get_object('enable')
        enable.connect('notify::active', self.toggle)

        test = self.builder.get_object('test')
        test.connect('clicked', self.test)
        test = self.builder.get_object('stop')
        test.connect('clicked', self.stop)

        window = self.builder.get_object('Main')
        window.connect('delete-event', gtk.main_quit)
        window.connect('destroy', gtk.main_quit)
        window.show()

    def test(self, button):
        self.main = multiprocessing.Process(target=self.start, args=[True])
        self.main.start()

    def toggle(self, switch, gparam):
        if switch.get_active():
            self.main = multiprocessing.Process(target=start, args=[])
            self.main.start()
        else:
            self.stop()

    def stop(self, button=None):
        """if the test alarm is running, stop it completely. If the normal alarm is running,
        only stop it until next night"""
        if not self.main is None and self.main.is_alive():
            self.main.terminate()
            self.main.join()

    def start(self, debug=None):
        if debug:
            start = 0
            end = 0
        else:
            start = parse_time(self.builder.get_object('start').get_text())
            end = parse_time(self.builder.get_object('end').get_text())

        voices_path = self.builder.get_object('voices_path')
        music_path = self.builder.get_object('music_path')
        music_vol_adj = self.builder.get_object('music_vol_adj')
        total_vol_adj = self.builder.get_object('total_vol_adj')
        max_duration = self.builder.get_object('max_duration')
        fade_duration = self.builder.get_object('fade_duration')
        probability_adj = self.builder.get_object('probability_adj')

        args = {
            'start': start,
            'end': end,
            'voices_path': voices_path.get_filename(),
            'music_path': music_path.get_filename(),
            'max_volume': total_vol_adj.get_value(),
            'music_volume': music_vol_adj.get_value(),
            'max_duration': float(max_duration.get_text() or 5) * 60,
            'fade_duration': float(fade_duration.get_text() or 0.1) * 60,
            'probability': probability_adj.get_value(),
            'effect': 100,
            'pause': 3,
            'debug': debug
        }

        Main(args)

if __name__ == '__main__':
    Interface()
    gtk.main()
