import numpy as np
import re


class Function(object):
    def __init__(self, string=''):
        self.string = string
        self.equation = []

        if self.string != '':
            self.str_to_equation()

    def str_to_equation(self):
        string = self.string
        regex = ur"(\s*((-|\+)*\s*\d+\.\d+)\s*((\*x)*\s*(\^\s*\d+)*))"

        matches = re.finditer(regex, string)

        equation = []

        for matchNum, match in enumerate(matches):

            coeff = match.group(2)
            str_rank = match.group(4)

            coeff = float(coeff.replace(' ', ''))
            str_rank = str_rank.replace('*', '').replace(' ', '')

            rank = 0
            if len(str_rank) == 0:
                rank = 0
            elif len(str_rank) == 1:
                rank = 1
            else:
                rank = int(str_rank.split('^')[1])

            equation.append((coeff, rank))
        self.equation = equation

    def eval_equation(self, x):
        equation = self.equation
        sumTotal = []
        for term in equation:
            coeff, rank = term

            total = 1.0
            for i in range(rank):
                total *= x
            total *= coeff

            sumTotal.append(total)

        return np.sum(np.asarray(sumTotal))


class Project(object):
    def __init__(self,
                 name=None,
                 image=None,
                 engraving=None,
                 laser=None,
                 machine=None,
                 preprocessor=None):
        self.name = name if name else 'Project'

        self.image = image
        self.engraving = engraving
        self.laser = laser
        self.machine = machine
        self.preprocessor = preprocessor


class Image(object):
    def __init__(self, image_data, original_extension='jpg'):
        self.image_data = image_data
        self.original_extension = original_extension


class Engraving(object):
    def __init__(self, pixel_width, pixel_height):
        self.pixel_width = pixel_width
        self.pixel_height = pixel_height


class Laser(object):
    def __init__(self, power_low, power_high, power_off, power_band, power_band_fn=None):
        self.power_low = power_low
        self.power_high = power_high
        self.power_off = power_off
        self.power_band = power_band
        self.power_band_fn = power_band_fn

        if power_band_fn is None:
            # build function
            function = Function(self.power_band)

            def power_fn(x):
                return function.eval_equation(x) * self.power_low + (self.power_high-self.power_low)

            self.power_band_fn = np.vectorize(power_fn)


class Machine(object):
    def __init__(self, units, feed_rate, overrun):
        self.units = units
        self.feed_rate = feed_rate
        self.overrun = overrun


class Preprocessor(object):
    def __init__(self, ignore_white, split_white, split_white_value=np.inf, white_cuttoff=255):
        self.ignore_white = ignore_white
        self.split_white = split_white
        self.split_white_value = split_white_value
        self.white_cuttoff = white_cuttoff
