
# Copyright (C) 2016 Eric Beanland <eric.beanland@gmail.com>

import shutil
import os

import sane
import numpy
import cairo
from PIL import Image, ImageFilter, ImageChops

#Workaround for missing cairo.ImageSurface.create_for_data implementation
#save to temp png then load into Gtk image widget
TEMPFILENAME = '.docscanner.png'

def scan(devid):
    dev = sane.open(devid)
    params = dev.get_parameters()

    dev.start()
    im = dev.snap()
    dev.close()

    im2 = im.filter(ImageFilter.FIND_EDGES)
    diff = ImageChops.difference(im, im2)
    bbox = diff.getbbox()
    if bbox:
        im3 = im.crop(bbox)
        im3.save(TEMPFILENAME)
    else:
        im.save(TEMPFILENAME)

    surface = cairo.ImageSurface.create_from_png(TEMPFILENAME)
    return surface


def np_to_surface(arr):
    height, width, channels = arr.shape
    # cairo.ImageSurface.create_for_data isn't implemented. WTF
    surface = cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_A8, width, height)
    return surface

def save_file(filename):
    print(filename)
    shutil.move(TEMPFILENAME, filename)
