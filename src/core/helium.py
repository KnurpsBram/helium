import numpy as np

import soundfile as sf
import librosa

import pyworld as pw

import torch
import torch.nn.functional as F

def audio_to_world(audio, sr):
    """
    Maps audio to WORLD parameters

    audio: waveform
    sr: samplerate    
    f0: pitch contour. A pitch of 0 Hz denotes an 'unvoiced' frame, in which pitch does not exist
    sp: spectral envelope. This encodes the resonance frequencies (the formants). It's essentially a spectrogram from which pitch information is removed by smoothing
    ap: aperiodicity parameters.

    Assumes audio comes in as a np.float32 array

    This function returns tensors with an empty batch dimension of BCT
        B is batchsize (fixed at 1)
        C is amount of channels (amount of spectrogram bins), 
        T amount of time steps (amount of spectrogram columns)

    WORLD internally requires np.float64 type and returns in shape (n_cols, n_rows) <-- the transpose of what it should be 

    So some reshaping and retyping is required
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
    """
    Maps WORLD parameters to audio.

    See `audio_to_world()`
    """
    f0 = f0.squeeze(0).numpy().astype(np.float64)
    sp = sp.squeeze(0).numpy().astype(np.float64)
    ap = ap.squeeze(0).numpy().astype(np.float64)

    sp = np.ascontiguousarray(sp.transpose())
    ap = np.ascontiguousarray(ap.transpose())
    audio = pw.synthesize(f0, sp, ap, sr)
    audio = audio.astype(np.float32)
    
    return audio

def helium(sp, factor):
    """
    Change the formants of the audio by factor _factor_ by stretching/squashing the spectral envelope in the frequency dimension
    """
    n_rows = sp.shape[-2]

    sp = F.interpolate(sp.unsqueeze(1), size=(int(n_rows*factor), sp.shape[-1])).squeeze(1)

    if sp.shape[-2] > n_rows:
        sp = sp[:, :n_rows, :]
    if sp.shape[-2] < n_rows:
        # sp = torch.cat([sp, torch.zeros(sp.shape[0], n_rows-sp.shape[-2], sp.shape[-1]).to(sp.device)], dim=-2) # TODO: WORLD doesn't deal well with absolute zeros
        sp = torch.cat([sp, torch.min(sp)*torch.ones(sp.shape[0], n_rows - sp.shape[-2], sp.shape[-1]).to(sp.device)], dim=-2)

    return sp

def change_pitch(f0, factor):
    """
    Change pitch by a multiplicative factor _factor_
    """
    return f0 * factor

def time_stretch(f0, sp, ap, factor):
    """
    Stretch the duration of the audio by a factor _factor_ without changing pitch or formant characteristics
    """
    f0 = F.interpolate(f0.unsqueeze(0), size=(int(f0.shape[-1]*factor),)).squeeze(0)
    sp = F.interpolate(sp, size=(int(sp.shape[-1]*factor),))
    ap = F.interpolate(ap, size=(int(ap.shape[-1]*factor),))

    return f0, sp, ap

def modify_audio(
    audio,
    sr,
    helium_factor       = 1.0,
    change_pitch_factor = 1.0,
    time_stretch_factor = 1.0,
):
    """
    Modifies audio by mapping audio to WORLD parameters, applying modifications on the WORLD parameters and mapping them back to audio
    """
    f0, sp, ap = audio_to_world(audio, sr)

    sp         = helium(sp, factor=helium_factor)
    f0         = change_pitch(f0, factor=change_pitch_factor) 
    f0, sp, ap = time_stretch(f0, sp, ap, factor=time_stretch_factor)

    audio = world_to_audio(f0, sp, ap, sr)

    return audio