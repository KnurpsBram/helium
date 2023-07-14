import os 
import sys 
sys.path.append(os.getcwd())
import shutil
import random
import string

import librosa
import soundfile as sf

from flask import Flask, send_file, render_template, request

import helium_lib.modify_audio

app = Flask(__name__)
app.secret_key = os.urandom(32)

 # paths are relative to helium/src
example_audio_path = "example_audio/p243_001.wav"

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

    tmp_folder = f'/tmp/{generate_random_string(length=4)}'
    os.makedirs(tmp_folder)
    incoming_audio_path = f'{tmp_folder}/incoming_audio.wav'
    outgoing_audio_path = f'{tmp_folder}/outgoing_audio.wav'

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

    shutil.rmtree(tmp_folder)

    return resp

def generate_random_string(length=4):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

if __name__ == "__main__":
    # app.run(host="0.0.0.0")
    app.run(debug=True)