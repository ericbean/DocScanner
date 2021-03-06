#!/usr/bin/env python3

#MIT License

#Copyright (c) 2016 Eric Beanland

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import datetime
import tempfile
import threading
import os
import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk, GdkPixbuf, GLib
from DocScanner import imaging

UIDIR = os.path.dirname(os.path.realpath(__file__))

class BuilderHelper:
    def __init__(self, builder):
        self.builder = builder

    def __getattr__(self, name):
        w = self.builder.get_object(name)
        if w is None:
            raise AttributeError

        self.__setattr__(name, w)
        return w

##############################################################################

class MainWindowHandler:
    def __init__(self, gtk_app):
        self.gtk_app = gtk_app
        self.builder = Gtk.Builder()
        self.builder.add_from_file(UIDIR+'/DocScanner.ui')
        self.builder.connect_signals(self)
        #init sane and get devices
        self.load_sane_devices()
        self.w = BuilderHelper(self.builder)
        #set default a working dir for the saved images
        self.w.cwd_filechooserbutton.set_filename(os.path.expanduser('~'))

        # add scan & save actions for main_window and disable them
        for action_name in ('save', 'scan'):
            action = Gio.SimpleAction.new(action_name, None)
            action.set_enabled(False)
            callback = getattr(self, 'on_' + action_name + '_action_activate')
            action.connect('activate', callback)
            self.w.main_window.add_action(action)
            setattr(self.w, action_name + '_action', action)

        # add header seperately since Glade can't do it yet
        self.w.main_window.set_titlebar(self.w.headerbar)
        self.w.main_window.show_all()

        # most recent scanned image
        self._scanned_image = None


    @property
    def scanned_image(self):
        return self._scanned_image


    @scanned_image.setter
    def scanned_image(self, value):
        self._scanned_image = value
        if value is None:
            self.w.image1.clear()
            self.w.save_action.set_enabled(False)
            self.w.image1.clear()
        else:
            self.w.save_action.set_enabled(True)


    def on_main_window_delete_event(self, *args):
        Gtk.main_quit(*args)


    def on_scan_action_activate(self, *args): #FIXME *args
        cb = self.w.device_combobox
        aid = cb.get_active_id()
        # TODO make this asynchronous
        self.scanned_image = imaging.scan(aid)
        # segfaults or aborts here with
        # python3: cairo-surface.c:928: cairo_surface_reference: Assertion
        #   `((*&(&surface->ref_count)->ref_count) > 0)' failed.
        # surface & format doesn't matter
        #self.w.image1.set_from_surface(self.scanned_image)
        # use set_image_helper to dump to a tempfile as a workaround
        self._set_image_helper()


    def on_save_action_activate(self, *args):
        folder = self.w.cwd_filechooserbutton.get_filename()
        spec = self.w.fn_entry.get_text()
        filename = self.make_filename(spec)
        if self.scanned_image:
            self.scanned_image.write_to_png(folder + '/' + filename)


    def on_image1_configure_event(self, *args):
        print("image1")
        print(args)


    def _set_image_helper(self):
        rect = self.w.image1.get_allocation()
        # dump surface to file and load into a GdkPixbuf scaled to fit
        # the Gtk.Image's allocation
        with tempfile.NamedTemporaryFile() as temp:
            self.scanned_image.write_to_png(temp)
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(temp.name, -1,
                rect.height, True)
            self.w.image1.set_from_pixbuf(pixbuf)


    def load_sane_devices(self):
        """Init sane and load device info without blocking the
        main thread.
        """

        def initer():
            sane_version, devices = imaging.init_sane()
            if devices:
                GLib.idle_add(loader, devices)

        def loader(devices):
            for dev in devices:
                self.w.device_liststore.append(dev)

            if devices:
                self.w.device_combobox.set_active(0)
                self.w.scan_action.set_enabled(True)

            return False

        thread = threading.Thread(target=initer)
        thread.daemon = True
        thread.start()


    def make_filename(self, spec):
        """Replace template variables in a string to create a filename.

            spec: str with %title, %date, %time

            returns: str filename
        """
        title = self.w.title_entry.get_text() or 'Scanned'
        name = spec.replace('%title', title)
        now = datetime.datetime.now()
        # date & times are not localized to ensure files can be sorted
        # lexicographically. Mimics ISO 8601 formating
        name = name.replace('%date', now.strftime('%Y-%m-%d'))
        name = name.replace('%time', now.strftime('%H:%M'))

        if name[-4:].lower() != '.png':
            name += '.png'

        return name

##############################################################################

class DocScannerApp(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)


    def do_activate(self):
        main_window = MainWindowHandler(self)
        self.add_window(main_window.w.main_window)


    def do_startup(self):
        Gtk.Application.do_startup(self)

##############################################################################

def main(*args):
    app = DocScannerApp()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)

if __name__ == '__main__':
    main()


