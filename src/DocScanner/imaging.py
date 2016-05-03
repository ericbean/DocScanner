
# Copyright (C) 2016 Eric Beanland <eric.beanland@gmail.com>

import shutil
import os

import sane
import numpy
import cairo
from PIL import Image, ImageFilter, ImageChops

HIDDENFILENAME = '.docscanner.png'

def scan(devid):
    dev = sane.open(devid)
    params = dev.get_parameters()
#    print('Device parameters:', params) #FIXME

    dev.start()
    im = dev.snap()
    dev.close()

    im2 = im.filter(ImageFilter.FIND_EDGES)
    diff = ImageChops.difference(im, im2)
    bbox = diff.getbbox()
    if bbox:
        im3 = im.crop(bbox)
        im3.save(HIDDENFILENAME)
    else:
        im.save(HIDDENFILENAME)

    surface = cairo.ImageSurface.create_from_png(HIDDENFILENAME)
    return surface


def np_to_surface(arr):
    height, width, channels = arr.shape
    # cairo.ImageSurface.create_for_data isn't implemented. WTF
    surface = cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_A8, width, height)
    return surface

def save_file(filename):
    print(filename)
    shutil.move(HIDDENFILENAME, filename)
