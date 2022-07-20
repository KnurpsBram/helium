import numpy as np
import librosa
import cv2
import pyworld as pw

def pitch_shift(audio, sr, x):
    """
    Shift the pitch of the audio by _x_ Hz
    """
    f0, sp, ap = pw.wav2world(audio, sr)

    f0[f0!=0] += x

    audio = pw.synthesize(f0, sp, ap, sr)

    return audio

def helium(audio, sr, f):
    """
    Raise the formants of the audio by factor _f_
    """
    f0, sp, ap = pw.wav2world(audio, sr)

    n_rows = sp.shape[-2]

    sp = cv2.resize(sp, fx=0, fy=f, interpolation=cv2.INTER_LINEAR)

    if sp.shape[-2] > n_rows:
        sp = sp[:n_rows, :]
    if sp.shape[-2] < n_rows:
        sp = np.concatenate([sp, np.zeros(n_rows-sp.shape[-2], sp.shape[-1])], axis=-2)

    audio = pw.synthesize(f0, sp, ap, sr)

    return audio

def time_stretch(audio, sr, f):
    """
    Stretch the duration of the audio by a factor _f_ without changing pitch or formant characteristics
    """
    f0, sp, ap = pw.wav2world(audio, sr)

    sp = cv2.resize(sp, fx=f, fy=0, interpolation=cv2.INTER_LINEAR)

    audio = pw.synthesize(f0, sp, ap, sr)

    return audio