from flask import Flask, request
import json
import webbrowser, random, threading
import base64
import io
import matplotlib.image as mpimg                        # TODO: remove matplotlib dependency
import numpy as np
from laserCAM import Project, Image, Engraving, Laser

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
        return request.get_data()
    return json.dumps([{'project': 'settings'}])


if __name__ == "__main__":
    port = 5000 + random.randint(0, 999)
    url = "http://127.0.0.1:{0}".format(port)

    threading.Timer(1.25, lambda: webbrowser.open(url)).start()

    app.run(port=port, debug=False)

