from flask import Flask, request, send_from_directory
app = Flask(__name__, static_url_path='')

app._static_folder = ''

@app.route("/")
def hello():
    return app.send_static_file('index.html')

if __name__ == "__main__":
    app.run()