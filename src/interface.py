#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk
import multiprocessing
from collections import namedtuple

from main import Main, parse_time

class Interface():
    def __init__(self):
        gladeFile = 'main.glade'
        self.builder = gtk.Builder()
        self.builder.add_from_file(gladeFile)

        enable = self.builder.get_object('enable')

        enable.connect('notify::active', self.toggle)

        window = self.builder.get_object('Main')
        window.connect('delete-event', gtk.main_quit)
        window.show()

    def toggle(self, switch, gparam):
        if switch.get_active():
            self.main = multiprocessing.Process(target=self.start, args=[])
            self.main.start()
        else:
            if not self.main is None and self.main.is_alive():
                self.main.terminate()

    def start(self):
        start = self.builder.get_object('start')
        end = self.builder.get_object('end')
        voices_path = self.builder.get_object('voices_path')
        music_path = self.builder.get_object('music_path')
        music_vol_adj = self.builder.get_object('music_vol_adj')
        total_vol_adj = self.builder.get_object('total_vol_adj')
        max_duration = self.builder.get_object('max_duration')
        fade_duration = self.builder.get_object('fade_duration')
        probability_adj = self.builder.get_object('probability_adj')

        try:
            max_duration = int(max_duration.get_text()) * 60
        except:
            return 'Please check if max_duration is a valid number'

        try:
            fade_duration = int(fade_duration.get_text()) * 60
        except:
            return 'Please check if fade_duration is a valid number'

        args = {
            'start': parse_time(start.get_text()),
            'end': parse_time(end.get_text()),
            'voices_path': voices_path.get_filename(),
            'music_path': music_path.get_filename(),
            'max_volume': total_vol_adj.get_value(),
            'music_volume': music_vol_adj.get_value(),
            'max_duration': max_duration,
            'fade_duration': fade_duration,
            'probability': probability_adj.get_value(),
            'effect': 100,
            'pause': 3
        }

        Main(args)

if __name__ == '__main__':
    main = Interface()
    gtk.main()
