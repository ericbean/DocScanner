
# Copyright (C) 2016 Eric Beanland <eric.beanland@gmail.com>

import atexit

import sane

def init_sane():
    """Initialize the sane module and return (sane_version, devices_list)."""
    sane_version = sane.init()
    devices = sane.get_devices()
    atexit.register(sane.exit)

    return sane_version, devices

