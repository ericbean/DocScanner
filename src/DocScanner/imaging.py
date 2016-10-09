
# Copyright (C) 2016 Eric Beanland <eric.beanland@gmail.com>

import array
import shutil
import os
import sys

import sane
import cairocffi as cairo
from PIL import Image, ImageFilter, ImageChops

#Workaround for missing cairo.ImageSurface.create_for_data implementation
#save to temp png then load into Gtk image widget
TEMPFILENAME = '.docscanner.png'

def scan(devid):
    dev = sane.open(devid)

    # start device and get an image
    dev.start()
    im = dev.snap()
    dev.close()

    # find edges
    im2 = im.filter(ImageFilter.FIND_EDGES)
    # use difference to create bounding box
    diff = ImageChops.difference(im, im2)
    bbox = diff.getbbox()
    if bbox:
        # crop to bounding box
        im3 = im.crop(bbox)
        im = im3

    return image_to_surface(im)


def image_to_surface(pil_image):
    """Convert PIL image to Cairo surface."""
    if pil_image.mode == 'L':
        pil_image = pil_image.convert('RGBA')

    if sys.byteorder == 'little':
        # swap red and blue channels for little-endians
        r,g,b,a = pil_image.split()
        pil_image = Image.merge("RGBA", (b,g,r,a))
    else:
        # swap channels for big-endians
        r,g,b,a = pil_image.split()
        pil_image = Image.merge("RGBA", (a,r,g,b))

    # covert image to writable buffer / array
    img_bytes = pil_image.tobytes()
    arr = array.array('B', img_bytes)

    width, height = pil_image.size
    # get stride for width
    stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_RGB24,
            width)

    # create cairo surface from array; will fail with NotImplementedError
    # if using the pycairo module
    surface = cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_RGB24,
            width, height, stride)

    return surface


def save_file(filename):
    print(filename)
    shutil.move(TEMPFILENAME, filename)

