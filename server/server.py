from flask import Flask, send_from_directory, request, jsonify
import multiprocessing
from main import loop_file
import pathlib
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

process = None

SCRIPTS_FOLDER = str(pathlib.Path(__file__).parent.resolve()) + '/../scripts/'


@app.route('/assets/<path>')
def assets(path):
    return send_from_directory('static', path)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/start', methods=['POST'])
def start_rotation():
    global process

    if process is not None:
        return ''

    data = request.json

    filename = SCRIPTS_FOLDER + data['filename']

    process = multiprocessing.Process(target=loop_file, args=(filename,))
    process.start()

    return ''

@app.route('/stop', methods=['POST'])
def stop_rotation():
    global process
    if process is not None:
        process.terminate()
        process = None

    return ''

@app.route('/get-scripts')
def get_scripts():
    files = [f for f in os.listdir(SCRIPTS_FOLDER) if os.path.isfile(os.path.join(SCRIPTS_FOLDER, f))]

    return jsonify(files)

def main():
    try:
        app.run(host="0.0.0.0", port=5000, debug=True)
    finally:
        if process is not None:
            process.terminate()

if __name__ == '__main__':
    main()
