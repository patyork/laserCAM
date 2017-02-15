import numpy as np

class Project(object):
    def __init__(self,
                 name=None,
                 image=None,
                 engraving=None,
                 laser=None,
                 machine=None,
                 preproccessing=None):
        self.name = name if name else 'Project'

        self.image = image
        self.engraving = engraving
        self.laser = laser
        self.machine = machine
        self.preproccessing = preproccessing


class Image(object):
    def __init__(self, image_data, original_extension='jpg'):
        self.image_data = image_data
        self.original_extension = original_extension


class Engraving(object):
    def __init__(self, pixel_width, pixel_height):
        self.pixel_width = pixel_width
        self.pixel_height = pixel_height


class Laser(object):
    def __init__(self, power_low, power_high, off_speed, power_band, power_band_fn=None):
        self.power_low = power_low
        self.power_high = power_high
        self.off_speed = off_speed
        self.power_band = power_band
        self.power_band_fn = power_band_fn

        if power_band_fn is None:
            # build function
            pass
