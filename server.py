from flask import Flask, request, send_from_directory
import json
app = Flask(__name__, static_url_path='')

app._static_folder = ''

@app.route("/")
def hello():
    return app.send_static_file('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print 'hey, here'

        received = json.loads(request.get_data())
        encoded = received['the_file'].split(',')

        imgData = encoded[1]
        ext = encoded[0].split('/')[1].split(';')[0]

        # or, more concisely using with statement
        with open("imageToSave." + ext, "wb") as fh:
            fh.write(imgData.decode('base64'))


        return json.dumps([{'hey2': 'hey'}])
    return json.dumps([{'hey': 'hey'}])

if __name__ == "__main__":
    app.run()
