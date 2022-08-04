import os 
import sys 
sys.path.append(os.getcwd())

import librosa
import soundfile as sf

from flask import Flask, flash, send_file, render_template, request, redirect

from core.helium import helium, pitch_shift, time_stretch

### from the helium/src directory, run:
# FLASK_APP=flask/app.py FLASK_ENV=development flask run --port 8000

app = Flask(__name__)
app.secret_key = os.urandom(24)

 # paths are relative to helium/src
local_audio_path = "p243_001.wav"
tempfile_path = "temp_audio.wav"

@app.route("/gui")
def hello_world():
    return render_template('welcome_to_the_gui.html')

@app.route("/up")
def up():
    return "Service is up!"

@app.route("/gui/helium", methods=["GET", "POST"])
def gui_helium():
    if request.method == "POST":

        try:
            factor = float(request.form['factor'])
        except:
            flash('Factor must be a number')
            return redirect(request.url)

        if 'file' not in request.files or request.files['file'].filename == "":
            flash('No file was selected')
            return redirect(request.url)
    
        file = request.files['file']
        file.save(tempfile_path)

        audio, sr = librosa.load(tempfile_path, sr=None)
        audio = helium(audio, sr, factor=factor)
        sf.write(file=tempfile_path, data=audio, samplerate=sr)

        return send_file(
            f"{os.getcwd()}/{tempfile_path}", 
            mimetype="audio/wav",
            as_attachment=True,
            attachment_filename="latest.wav"
        )

    return render_template("helium_gui.html")

@app.route("/gui/pitch_shift", methods=["GET", "POST"])
def gui_pitch_shift():
    if request.method == "POST":

        try:
            shift = float(request.form['shift'])
        except:
            flash('Shift must be a number')
            return redirect(request.url)

        if 'file' not in request.files or request.files['file'].filename == "":
            flash('No file was selected')
            return redirect(request.url)
    
        file = request.files['file']
        file.save(tempfile_path)

        audio, sr = librosa.load(tempfile_path, sr=None)
        audio = pitch_shift(audio, sr, shift=shift)
        sf.write(file=tempfile_path, data=audio, samplerate=sr)

        return send_file(
            f"{os.getcwd()}/{tempfile_path}", 
            mimetype="audio/wav",
            as_attachment=True,
            attachment_filename="latest.wav"
        )

    return render_template("pitch_shift_gui.html")

@app.route("/gui/time_stretch", methods=["GET", "POST"])
def gui_time_stretch():
    if request.method == "POST":

        try:
            factor = float(request.form['factor'])
        except:
            flash('Factor must be a number')
            return redirect(request.url)

        if 'file' not in request.files or request.files['file'].filename == "":
            flash('No file was selected')
            return redirect(request.url)

        file = request.files['file']
        file.save(tempfile_path)

        audio, sr = librosa.load(tempfile_path, sr=None)
        audio = time_stretch(audio, sr, factor=factor)
        sf.write(file=tempfile_path, data=audio, samplerate=sr)

        return send_file(
            f"{os.getcwd()}/{tempfile_path}", 
            mimetype="audio/wav",
            as_attachment=True,
            attachment_filename="latest.wav"
        )

    return render_template("time_stretch_gui.html")

# @app.route("/api/helium")
# def api_helium():

#     audio, sr = librosa.load(local_audio_path, sr=None)

#     audio = helium(audio, sr, f=2)

#     sf.write(file=tempfile_path, data=audio, samplerate=sr)

#     return send_file(
#         f"{os.getcwd()}/{tempfile_path}", 
#         mimetype="audio/wav",
#         as_attachment=True,
#         attachment_filename="latest.wav"
#     )

# @app.route("/api/pitch_shift")
# def api_pitch_shift():
#     audio, sr = librosa.load(local_audio_path, sr=None)

#     audio = pitch_shift(audio, sr, x=100)

#     sf.write(file=tempfile_path, data=audio, samplerate=sr)

#     return send_file(
#         f"{os.getcwd()}/{tempfile_path}", 
#         mimetype="audio/wav",
#         as_attachment=True,
#         attachment_filename="latest.wav"
#     )

# @app.route("/api/time_stretch")
# def route_time_stretch():
#     audio, sr = librosa.load(local_audio_path, sr=None)

#     audio = time_stretch(audio, sr, f=1.8)

#     sf.write(file=tempfile_path, data=audio, samplerate=sr)

#     return send_file(
#         f"{os.getcwd()}/{tempfile_path}", 
#         mimetype="audio/wav",
#         as_attachment=True,
#         attachment_filename="latest.wav"
#     )

# @app.route("/get_file")
# def get_file():
#     return send_file(
#         f"{os.getcwd()}/{local_audio_path}", # paths are relative to helium/src, but this function doesn't work like that, so we give absolute paths
#         mimetype="audio/wav",
#         as_attachment=True,
#         attachment_filename="latest.wav"
#     )

if __name__ == "__main__":
    app.config['DEBUG'] = True
    # app.run(port=8000)
    app.run(host='0.0.0.0', port=8000)