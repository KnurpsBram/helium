import os 
import sys 
sys.path.append(os.getcwd())
import shutil

import librosa
import soundfile as sf

from flask import Flask, flash, send_file, render_template, request, redirect, url_for

from core.helium import modify_audio

app = Flask(__name__)
app.secret_key = os.urandom(32)

 # paths are relative to helium/src
example_audio_path = "p243_001.wav"
tempfile_path = "temp_audio.wav"
tempfile_path2 = "temp_audio2.wav"

@app.route("/")
def home():
    url = url_for("gui_modify_audio")
    return f"please visit {request.host}{url}"

@app.route("/up")
def up():
    return "Service is up!"

@app.route("/test")
def test():
    return render_template("test.html")

@app.route("/gui", methods=["GET", "POST"])
def gui_modify_audio():
    """
    Returns a html file with a form where the user can upload an audio file and set parameters to modify audio
    If the request method is POST, audio and parameters are parsed from the request form, the audio gets modified and the user receives the modified audio via auto-download

    If no audio is selected, the default example audio file is used

    See `modify_audio()`
    """

    if request.method == "POST":

        try:
            helium_factor       = float(request.form['helium_factor'])
            change_pitch_factor = float(request.form['change_pitch_factor'])
            time_stretch_factor = float(request.form['time_stretch_factor'])
        except:
            flash("Factor must be a number")
            return redirect(request.url)

        if (helium_factor < 0) or (change_pitch_factor < 0) or (time_stretch_factor < 0):
            flash("Sorry, can't do negative numbers")

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

@app.route("/api", methods=["POST"])
def modify_audio():
    """
    
    """
    # try:
    #     helium_factor       = float(request.form['helium_factor'])
    #     change_pitch_factor = float(request.form['change_pitch_factor'])
    #     time_stretch_factor = float(request.form['time_stretch_factor'])
    # except:
    #     flash("Factor must be a number")
    #     return redirect(request.url)

    # if (helium_factor < 0) or (change_pitch_factor < 0) or (time_stretch_factor < 0):
    #     flash("Sorry, can't do negative numbers")

    # if 'file' not in request.files or request.files['file'].filename == "":
    #     shutil.copy(example_audio_path, tempfile_path)
    # else:
    #     file = request.files['file']
    #     file.save(tempfile_path) 

    file = request.files['audio_data']
    file.save(tempfile_path)
    
    os.system(f"yes | ffmpeg -i {tempfile_path} -c:a pcm_s16le {tempfile_path2}") # webm to wav

    # audio, sr = sf.read(tempfile_path)
    audio, sr = librosa.load(tempfile_path2, sr=None)
    # audio, sr = librosa.load(tempfile_path, sr=None)

    print("Got audio!")
    print(len(audio))

    sr = sr * 2 # TEMP: resample

    sf.write(file=tempfile_path, data=audio, samplerate=sr)

    return send_file(
        f"{os.getcwd()}/{tempfile_path}", 
        mimetype="audio/wav",
        as_attachment=True,
        attachment_filename="latest.wav"
    )


if __name__ == "__main__":
    # app.run(host="0.0.0.0")
    app.run(debug=True)