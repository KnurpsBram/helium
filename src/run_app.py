import os 
import sys 
sys.path.append(os.getcwd())
import io
import base64
import numpy as np
import shutil

import librosa
import soundfile as sf
import scipy.io.wavfile

from flask import Flask, flash, send_file, render_template, request, redirect, url_for
from flask import Response

from flask_cors import CORS

import helium_lib.modify_audio

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(32)

 # paths are relative to helium/src
example_audio_path = "p243_001.wav"
tempfile_path = "temp_audio.wav"
tempfile_path2 = "temp_audio2.wav"


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

    file = request.files['audio_data']
    file.save(tempfile_path)

    audio, sr = librosa.load(tempfile_path, sr=None)

    audio = helium_lib.modify_audio.modify_audio(
        audio,
        sr,
        formant_multiplier = formant_multiplier,
        pitch_multiplier = pitch_multiplier,
        tempo_multiplier = tempo_multiplier,
    )

    sf.write(file=tempfile_path, data=audio, samplerate=sr)

    resp = send_file(
        f"{os.getcwd()}/{tempfile_path}", 
        mimetype="audio/wav",
        as_attachment=True,
        download_name="latest.wav"
    )

    return resp


if __name__ == "__main__":
    # app.run(host="0.0.0.0")
    app.run(debug=True)