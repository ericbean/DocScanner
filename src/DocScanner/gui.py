
from datetime import date
import os

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
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


class MainWindow:
    def __init__(self, devices):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(UIDIR+'/DocScanner.ui')
        self.builder.connect_signals(self)
        self.w = BuilderHelper(self.builder)
        self.device_liststore = self.builder.get_object('device_liststore')
        
        for dev in devices:
            self.device_liststore.append(dev)
        else:
            cb = self.builder.get_object('device_combobox')
            cb.set_active(0)
        
        window = self.builder.get_object('window1')
        window.show_all()


    def on_window1_delete_event(self, *args):
        Gtk.main_quit(*args)

    
    def on_scan_action_activate(self, *args): #FIXME *args
        print("scan activated")
        cb = self.builder.get_object('device_combobox')
        aid = cb.get_active_id()
        surface = imaging.scan(aid)
        self.set_image_helper()


    def on_save_action_activate(self, *args):
        filename = self.w.fn_entry.get_text()
        imaging.save_file(filename)
        self.w.image1.clear()


    def on_window1_configure_event(self, *args):
        self.set_image_helper()


    def on_image1_configure_event(self, *args):
        print("image1")
        print(args)


    def set_image_helper(self):
        path = imaging.HIDDENFILENAME
        if os.path.exists(path):
            im = self.builder.get_object('image1')
            rect = im.get_allocation()
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, -1,
                rect.height, True)
            im.set_from_pixbuf(pixbuf)


    def on_title_entry_changed(self, *args):
        self.update_fn_entry()


    def update_fn_entry(self):
        title = self.w.title_entry.get_text()
        if not title:
            title = "Scanned"
        date_text = self.w.date_entry.get_text()
        if not date_text:
            date_text = str(date.today())
        fn = date_text + '-' + title + ".png"
        
        i = 1
        while os.path.exists(fn):
            fn = date_text + '-' + title + "_" + i +".png"
        
        self.w.fn_entry.set_text(fn)
        



def guimain(sane_version, devices):
    mw = MainWindow(devices)
    Gtk.main()



