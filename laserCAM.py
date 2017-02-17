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
        self.image.normalize_image(white_cutoff=self.preprocessor.white_cutoff)
        terminator_pixels = self.preprocessor.get_start_stop(self.image.normalized_data)


        # Simple gCode generator (back and forth method)
        # TODO: handle case of split image (on white)
        distance_fed = 0.0                  # Used for estimated time metric
        distance_overran = 0.0              # Used for estimated time metric

        pw = self.engraving.pixel_width
        ph = self.engraving.pixel_height

        image_data = self.image.normalized_data
        laserPower = self.laser.power_band_fn(image_data)   # Image to laser intensity (S commands)

        steps = []
        steps += self.machine.to_gcode()    # ex. G21 _ F500
        steps += self.laser.to_gcode()      # ex. S2000 _ M3

        # TODO: Add ability to split machining into phases (smaller/shorter gCode files)
        at_start = False
        direction_of_travel = 1
        for row_num, raw_row in enumerate(image_data):
            edges = terminator_pixels[row_num]

            if edges[0] is None or edges[1] is None:     # Row is all "white", no need to traverse it
                continue
            elif not at_start:
                # Get away from start
                start_x = edges[1 - int(direction_of_travel == True)] * pw + (direction_of_travel * self.machine.overrun)

                steps.append('G0 X%.4f Y%.4f' % (start_x, row_num * ph))

            # Traverse pixels in row
            for pixel in raw_row[edges[0] : edges[1]+1][::direction_of_travel]:
                pixelX =



        pass


class Image(object):
    def __init__(self, image_data, original_extension='jpg'):
        self.image_data = image_data
        self.original_extension = original_extension

        print np.min(image_data), np.average(image_data), np.max(image_data)

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

            if np.max(image_data) <= 1.0:                           # already normalized to [0, 1]
                image_data[image_data*255. >= white_cutoff] = 1.0   # Change near-white values to white
                image_data = 1.0 - image_data                       # Reverse colors (simplify power calc: white = less power)
            else:
                image_data[image_data>=white_cutoff] = 255          # Change near-white values to white
                image_data = 255. - image_data                      # Reverse colors (simplify power calc: white = less power)
                image_data /= 255.                                  # Normalize [0., 1.]
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

    def to_gcode(self):
        return ['S%i' % (self.power_off), 'M3']


class Machine(object):
    def __init__(self, units, feed_rate, overrun):
        self.units = units
        self.feed_rate = feed_rate
        self.overrun = overrun

    def to_gcode(self):
        steps = []

        if self.units == 'mm': steps.append('G21')
        else: steps.append('G20')

        steps.append('F%i' % self.feed_rate)

        return steps



class Preprocessor(object):
    def __init__(self, ignore_white, split_white, split_white_value=np.inf, white_cutoff=255):
        self.ignore_white = ignore_white
        self.split_white = split_white
        self.split_white_value = split_white_value
        self.white_cutoff = white_cutoff

        self._terminators = None

    def get_start_stop(self, normalized_image):
        """
        Return a list of (low, high) pixels positions that the laser must pass through on each row.
        This is sensitive to both the ignore_white & white_cutoff parameters
        :param normalized_image: normalized image data of shape (h, w)
        :param overrun: overrun distance from the Machine
        :return: List of Tuples (low, high)
        """

        terminators =[]

        if self.split_white:
            pass                    # TODO: Implement

        if self.ignore_white:
            for row in normalized_image:
                indexes = np.where(row > 0.0)[0]
                if len(indexes) == 0:
                    terminators.append((None, None))    # row is entirely white
                else:
                    terminators.append((indexes[0], indexes[-1]))
        else:
            for row in normalized_image:
                stop = len(row)
                terminators.append((0, stop))
        print 'Terminators:',
        print terminators
        self._terminators = terminators
        return terminators


