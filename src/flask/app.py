import os 
import sys 
sys.path.append(os.getcwd())
import shutil

import librosa
import soundfile as sf

from flask import Flask, flash, send_file, render_template, request, redirect

from core.helium import modify_audio

### from the helium/src directory, run: #TODO: this currently does not work. The best way is to run this as a python file. How can I run a flask app properly?
# FLASK_APP=flask/app.py FLASK_ENV=development flask run --port 8000

app = Flask(__name__)
app.secret_key = os.urandom(32)

 # paths are relative to helium/src
example_audio_path = "p243_001.wav"
tempfile_path = "temp_audio.wav"

@app.route("/up")
def up():
    return "Service is up!"

@app.route("/gui")
def gui_modify_audio():

    def get_factor_from_form(key):
        try:
            factor = float(request.form[key])
            if factor < 0:
                flash("Sorry, can't do negative numbers")
        except:
            flash('Factor must be a number')
            return redirect(request.url)
        return factor

    if request.method == "POST":

        helium_factor       = get_factor_from_form('helium_factor')
        change_pitch_factor = get_factor_from_form('change_pitch_factor')
        time_stretch_factor = get_factor_from_form('time_stretch_factor')

        if 'file' not in request.files or request.files['file'].filename == "":
            shutil.copy(example_audio_path, tempfile_path)
        else:
            file = request.files['file']
            file.save(tempfile_path)                

        audio, sr = librosa.load(tempfile_path, sr=None)

        audio = modify_audio(
            audio,
            sr,
            helium_factor       = helium_factor,
            change_pitch_factor = change_pitch_factor,
            time_stretch_factor = time_stretch_factor,
        )

        sf.write(file=tempfile_path, data=audio, samplerate=sr)

        return send_file(
            f"{os.getcwd()}/{tempfile_path}", 
            mimetype="audio/wav",
            as_attachment=True,
            attachment_filename="latest.wav"
        )

    return render_template("helium_gui.html")

if __name__ == "__main__":
    app.config['DEBUG'] = True
    # app.run()
    
    app.run(host="0.0.0.0")