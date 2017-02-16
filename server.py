from flask import Flask, request
import json
import webbrowser, random, threading
import base64
import io
import matplotlib.image as mpimg                        # TODO: remove matplotlib dependency
import numpy as np
from laserCAM import Project, Image, Engraving, Laser, Machine, Preprocessor

app = Flask(__name__, static_url_path='')

project = Project()


import cPickle as pickle #TODO: remove


app._static_folder = ''

@app.route("/")
def hello():
    return app.send_static_file('index.html')


@app.route('/project/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print 'hey, here'

        received = json.loads(request.get_data())
        encoded = received['the_file'].split(',')

        with open('receivedImage.pkl', 'wb') as fo:     # TODO: remove
            pickle.dump(received, fo)

        imgData = encoded[1]
        ext = encoded[0].split('/')[1].split(';')[0]

        imgData = base64.b64decode(imgData)
        with open("imageToSave." + ext, "wb") as fh:    # TODO: remove if file never used
            fh.write(imgData)

        imgData = io.BytesIO(imgData)
        imgData = mpimg.imread(imgData, format=ext)     # TODO: check what extensions are valid

        tmp = Image(imgData, ext)
        project.image = tmp
        del(tmp)

        return json.dumps([{'hey2': str(type(project.image.image_data))}])

    return json.dumps([{'hey': 'hey'}])


@app.route("/project/settings", methods=['GET', 'POST'])
def project_settings():
    if request.method == 'POST':

        received = json.loads(request.get_data())

        _engrave = received['engraving']
        _laser = received['laser']
        _machine = received['machine']
        _preproc = received['preprocessing']

        engrave = Engraving(pixel_width=_engrave['width'], pixel_height=_engrave['height'])
        laser = Laser(power_low=_laser['powerLow'], power_high=_laser['powerHigh'], power_off=_laser['powerOff'],
                      power_band=_laser['powerBand'])
        machine = Machine(units=_machine['units'], feed_rate=_machine['feedRate'],
                          overrun=_machine['overrun'])
        preprocessor = Preprocessor(ignore_white=_preproc['ignoreWhite'], split_white=_preproc['splitWhite'],
                                    split_white_value=_preproc['splitMin'], white_cuttoff=_preproc['whiteCutoff'])

        project.engraving = engrave
        project.laser = laser
        project.machine = machine
        project.preprocessor = preprocessor


        return request.get_data()
    return json.dumps([{'project': 'settings'}])


if __name__ == "__main__":
    port = 5000 + random.randint(0, 999)
    url = "http://127.0.0.1:{0}".format(port)

    threading.Timer(1.25, lambda: webbrowser.open(url)).start()

    app.run(port=port, debug=False)

