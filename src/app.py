import os 
import sys 
sys.path.append(os.getcwd())
import shutil
import argparse
import random
import string

import librosa
import soundfile as sf

from flask import Flask, send_file, render_template, request
from flask_cors import CORS

import helium_lib

app = Flask(__name__)
cors = CORS(app)
app.secret_key = os.urandom(32)


@app.route("/")
def home():
    return render_template('index.html', api_url=app.config['api_url'])   


@app.route("/up")
def up():
    return "Service is up!"


@app.route("/api", methods=["POST", "GET"])
def modify_audio():

    formant_multiplier = float(request.form['formant_multiplier'])
    pitch_multiplier = float(request.form['pitch_multiplier'])
    tempo_multiplier = float(request.form['tempo_multiplier'])

    tmp_folder = f'/tmp/{generate_random_string(length=4)}'
    os.makedirs(tmp_folder)
    incoming_audio_path = f'{tmp_folder}/incoming_audio.wav'
    outgoing_audio_path = f'{tmp_folder}/outgoing_audio.wav'

    file = request.files['audio_data']
    file.save(incoming_audio_path)

    audio, sr = librosa.load(incoming_audio_path, sr=None)

    audio = helium_lib.modify_audio(
        audio,
        sr,
        formant_multiplier = formant_multiplier,
        pitch_multiplier = pitch_multiplier,
        tempo_multiplier = tempo_multiplier,
    )

    sf.write(file=outgoing_audio_path, data=audio, samplerate=sr)

    resp = send_file(
        outgoing_audio_path, 
        mimetype="audio/wav",
        as_attachment=True,
        download_name="latest.wav"
    )

    shutil.rmtree(tmp_folder)

    return resp

def generate_random_string(length=4):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--api_url', type=str, default='http://localhost:5000/api')
    args = parser.parse_args()
    
    app.config['api_url'] = args.api_url

    app.run(debug=True)

    # I'm having some issue setting up HTTPS
    # Browsers only want to open the microphone of the user for HTTPS websites (or localhost), not for HTTP
    # In order to support HTTPS, you need a certificate and a key
    # See https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https/page/3 for details
    # Using the 'simple' options below you can get some HTTPS-like behaviour, but with a drawback:
    # The user has to click through a warning that the certificate is not valid

    # adhoc keys are generated on the fly, the user must tell the browser to trust this site every time
    ssl_context = 'adhoc'

    # # self-signed certificates are generated once, the user can tell the browser to trust this site once
    # # generate self-certified keys with `openssl req -x509 -newkey rsa:4096 -nodes -out keys/cert.pem -keyout keys/key.pem -days 365`
    # ssl_context = ('keys/cert.pem', 'keys/key.pem') 

    app.run(host="0.0.0.0", ssl_context=ssl_context)
