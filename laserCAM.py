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

    def generate_gcode(self):
        pass


class Image(object):
    def __init__(self, image_data, original_extension='jpg'):
        self.image_data = image_data
        self.original_extension = original_extension

        self._normalized = False
        self.normalized_data = None

    def normalize_image(self, white_cutoff):
        """
        Normalize an N-channel image. Resulting array will have values in range [0.0, 1.0]
        where 0.0 is white, and all values under the white_cuttoff will be considered white/0.0.
        The effective origin of the image will be flipped, such that (0,0) is at the bottom left.
        :param white_cutoff: Integer value in range [0, 255] above which is considered as white for white cutoff.
        :return: None
        """
        if not self._normalized:
            image_data = self.image_data
            image_data = np.average(image_data, axis=-1)[::-1]      # Convert to 1 channel, reverse axis
            image_data[image_data>=white_cutoff] = 255              # Change near-white values to white
            image_data = 255. - image_data                          # Reverse colors (simplify power calc: white = less power)
            image_data /= 255.                                      # Normalize [0., 1.]
            self.normalized_data = image_data
            self._normalized = True


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
                return function.eval_equation(x) * (self.power_high-self.power_low) + self.power_low

            self.power_band_fn = np.vectorize(power_fn)


class Machine(object):
    def __init__(self, units, feed_rate, overrun):
        self.units = units
        self.feed_rate = feed_rate
        self.overrun = overrun


class Preprocessor(object):
    def __init__(self, ignore_white, split_white, split_white_value=np.inf, white_cutoff=255):
        self.ignore_white = ignore_white
        self.split_white = split_white
        self.split_white_value = split_white_value
        self.white_cutoff = white_cutoff

    def get_start_stop(self, normalized_image, overrun):
        """
        Return a list of (low, high) pixels positions that the laser must pass through on each row.
        This is sensitive to both the ignore_white & white_cutoff parameters, as well as the overrun lengths.
        :param normalized_image: normalized image data of shape (h, w)
        :param overrun: overrun distance from the Machine
        :return: List of Tuples (low, high)
        """

        terminators =[]

        pass


