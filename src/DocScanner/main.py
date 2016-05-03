

import sane

def main():
    print("Initializing SANE")
    sane_version = sane.init()
    print(sane_version)
    devices = sane.get_devices()
    print('Available devices:', devices)
    
    # temp call to guimain()
    # in the future add some cli functionality
    from DocScanner import gui
    gui.guimain(sane_version, devices)

    sane.exit()


