import os 
import sys 
sys.path.append(os.getcwd())
import io
import base64
import numpy as np
import shutil
import random
import string

import librosa
import soundfile as sf
import scipy.io.wavfile

from flask import Flask, flash, send_file, render_template, request, redirect, url_for
from flask import Response

import helium_lib.modify_audio

app = Flask(__name__)
app.secret_key = os.urandom(32)

 # paths are relative to helium/src
example_audio_path = "example_audio/p243_001.wav"
incoming_audio_path_template = "/tmp/{tmp_subfolder}/incoming_audio.wav"
outgoing_audio_path_template = "/tmp/{tmp_subfolder}/outgoing_audio.wav"

@app.route("/")
def home():
    return render_template('index.html')   


@app.route("/up")
def up():
    return "Service is up!"


@app.route("/api", methods=["POST", "GET"])
def modify_audio():

    formant_multiplier = float(request.form['formant_multiplier'])
    pitch_multiplier = float(request.form['pitch_multiplier'])
    tempo_multiplier = float(request.form['tempo_multiplier'])

    tmp_subfolder = generate_random_string(length=4)
    incoming_audio_path = incoming_audio_path_template.format(tmp_subfolder=tmp_subfolder)
    outgoing_audio_path = outgoing_audio_path_template.format(tmp_subfolder=tmp_subfolder)

    file = request.files['audio_data']
    file.save(incoming_audio_path)

    audio, sr = librosa.load(incoming_audio_path, sr=None)

    audio = helium_lib.modify_audio.modify_audio(
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

    os.remove(incoming_audio_path)
    os.remove(outgoing_audio_path)

    return resp

def generate_random_string(length=4):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

if __name__ == "__main__":
    # app.run(host="0.0.0.0")
    app.run(debug=True)