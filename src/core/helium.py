import numpy as np

import soundfile as sf
import librosa

import pyworld as pw

import torch
import torch.nn.functional as F

def audio_to_world(audio, sr):
    """
    Maps audio to WORLD parameters

    Assumes audio comes in as a np.float32 array

    WORLD internally requires np.float64 type and returns in shape (n_cols, n_rows) <-- the transpose of what it should be 

    This function returns tensors with an empty batch dimension of BCT
        B is batchsize (usually 1)
        C is amount of channels (amount of spectrogram bins), 
        T amount of time steps (amount of spectrogram columns)
    """
    audio = audio.astype(np.float64)
    f0, sp, ap = pw.wav2world(audio, sr)
    sp = sp.transpose()
    ap = ap.transpose()

    f0 = torch.FloatTensor(f0).unsqueeze(0)
    sp = torch.FloatTensor(sp).unsqueeze(0)
    ap = torch.FloatTensor(ap).unsqueeze(0)

    return f0, sp, ap

def world_to_audio(f0, sp, ap, sr):

    f0 = f0.squeeze(0).numpy().astype(np.float64)
    sp = sp.squeeze(0).numpy().astype(np.float64)
    ap = ap.squeeze(0).numpy().astype(np.float64)

    sp = np.ascontiguousarray(sp.transpose())
    ap = np.ascontiguousarray(ap.transpose())
    audio = pw.synthesize(f0, sp, ap, sr)
    audio = audio.astype(np.float32)
    
    return audio

def pitch_shift(audio, sr, shift):
    """
    Shift the pitch of the audio by _shift_ Hz
    """
    f0, sp, ap = audio_to_world(audio, sr)

    f0[f0!=0] += shift

    audio = world_to_audio(f0, sp, ap, sr)

    return audio

def helium(audio, sr, factor):
    """
    Raise the formants of the audio by factor _factor_
    """
    f0, sp, ap = audio_to_world(audio, sr)

    n_rows = sp.shape[-2]

    sp = F.interpolate(sp.unsqueeze(1), size=(int(n_rows*factor), sp.shape[-1])).squeeze(1)

    if sp.shape[-2] > n_rows:
        sp = sp[:, :n_rows, :]
    if sp.shape[-2] < n_rows:
        # sp = torch.cat([sp, torch.zeros(sp.shape[0], n_rows-sp.shape[-2], sp.shape[-1]).to(sp.device)], dim=-2) # TODO: WORLD doesn't deal well with absolute zeros
        sp = torch.cat([sp, torch.min(sp)*torch.ones(sp.shape[0], n_rows - sp.shape[-2], sp.shape[-1]).to(sp.device)], dim=-2)

    audio = world_to_audio(f0, sp, ap, sr)

    return audio

def time_stretch(audio, sr, factor):
    """
    Stretch the duration of the audio by a factor _factor_ without changing pitch or formant characteristics
    """
    f0, sp, ap = audio_to_world(audio, sr)

    f0 = F.interpolate(f0.unsqueeze(0), size=(int(f0.shape[-1]*factor),)).squeeze(0)
    sp = F.interpolate(sp, size=(int(sp.shape[-1]*factor),))
    ap = F.interpolate(ap, size=(int(ap.shape[-1]*factor),))

    audio = world_to_audio(f0, sp, ap, sr)

    return audio
