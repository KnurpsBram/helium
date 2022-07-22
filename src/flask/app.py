import os 
import sys 
sys.path.append(os.getcwd())

import librosa
import soundfile as sf

from flask import Flask, send_file, render_template

# from core.helium import helium, pitch_shift, time_stretch

### from the helium/src directory, run:
# FLASK_APP=flask/app.py FLASK_ENV=development flask run --port 8000

app = Flask(__name__)

 # paths are relative to helium/src
local_audio_path = "p243_001.wav"
tempfile_path = "temp_audio.wav"

@app.route("/")
def hello_world():
    return "Hello World!"

@app.route("/up")
def up():
    return "Service is up!"

@app.route("/upload")
def upload():
    return render_template('templates/upload.html')

@app.route("/helium")
def route_helium():
    audio, sr = librosa.load(local_audio_path, sr=None)

    audio = helium(audio, sr, f=2)

    sf.write(file=tempfile_path, data=audio, samplerate=sr)

    return send_file(
        f"{os.getcwd()}/{tempfile_path}", 
        mimetype="audio/wav",
        as_attachment=True,
        attachment_filename="latest.wav"
    )

@app.route("/pitch_shift")
def route_pitch_shift():
    audio, sr = librosa.load(local_audio_path, sr=None)

    audio = pitch_shift(audio, sr, x=100)

    sf.write(file=tempfile_path, data=audio, samplerate=sr)

    return send_file(
        f"{os.getcwd()}/{tempfile_path}", 
        mimetype="audio/wav",
        as_attachment=True,
        attachment_filename="latest.wav"
    )

@app.route("/time_stretch")
def route_time_stretch():
    audio, sr = librosa.load(local_audio_path, sr=None)

    audio = time_stretch(audio, sr, f=1.8)

    sf.write(file=tempfile_path, data=audio, samplerate=sr)

    return send_file(
        f"{os.getcwd()}/{tempfile_path}", 
        mimetype="audio/wav",
        as_attachment=True,
        attachment_filename="latest.wav"
    )

@app.route("/get_file")
def get_file():
    return send_file(
        f"{os.getcwd()}/{local_audio_path}", # paths are relative to helium/src, but this function doesn't work like that, so we give absolute paths
        mimetype="audio/wav",
        as_attachment=True,
        attachment_filename="latest.wav"
    )