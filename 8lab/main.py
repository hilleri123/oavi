#!/usr/bin/python3
from matplotlib import mlab
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
import sys
from clint.textui import progress
import soundfile as sf

#from scikits.audiolab import Sndfile


VMIN = -100
VMAX = 40

ZERO = 1e-12
NOISE_AVG = -1e-7
NOISE_VAR = 1e-7


def specgram2d(signal_data, fs, ax=None, title=None):
    ax.set_title(title, loc='center', wrap=True)
    pxx, freq, time, im = ax.specgram(signal_data, Fs=fs)
    im = ax.pcolormesh(time, freq, 10 * np.log10(pxx), shading='auto', vmin=VMIN, vmax=VMAX)
    ax.set_xlabel('Время, с')
    ax.set_ylabel('Частота, Гц')
    return pxx, freq, time, im


def main():
    file_name = sys.argv[-2]
    file_noise = sys.argv[-1]
    print(file_name, file_noise)
    signal_data, sampling_frequency = sf.read(file_name)
    noise, _ = sf.read(file_noise)
    #signal_data += noise
    off_set = sampling_frequency*0
    count = sampling_frequency*6
    secs = signal_data.size / sampling_frequency
    #print(secs, noise.size)
    noise*=8
    for idx, data in enumerate(progress.bar(signal_data)):
        #print(idx, data, noise[idx%noise.size]*8, idx%noise.size)
        signal_data[idx] += noise[idx%noise.size]
        if data == 0:
            signal_data[idx] = ZERO
    sf.write('song_noise.wav', signal_data, sampling_frequency, 'PCM_32')
    slice_data = np.array(signal_data)[off_set:off_set+count]
    #data = np.array(f.read_frames(f.nframes), dtype=np.float64)
    #f.close()
    #rate = f.samplerate;
    
    #sampling_frequency = samplerate
    #signal_data = data

    #sampling_frequency, signal_data = wavfile.read(file_name)
    #sampling_frequency = 1000
    #signal_data = np.array(signal_data)[:,0][:sampling_frequency]
    
    print(signal_data)
    print(sampling_frequency)
    fig, ax = plt.subplots()
    pxx, freq, time, img = specgram2d(slice_data, fs=sampling_frequency, ax=ax)
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Амплитуда, дБ')
    cbar.minorticks_on()
    plt.savefig('base.png')
    #plt.show()
    _, _, _, _ = specgram2d(noise, fs=sampling_frequency, ax=ax)
    plt.savefig('pure_noise.png')
    
        
    #a_noise = signal_data[:int(sampling_frequency*2)]
    pxx_noise, _, _, _ = plt.specgram(noise, Fs=sampling_frequency)
    new_data = slice_data
    for idx, data in enumerate(progress.bar(slice_data)):
        new_data[idx] = max(ZERO, data - np.average(noise))
    sf.write('song_without_noise.wav', new_data, sampling_frequency, 'PCM_32')
    plt.savefig('noise.png')
    for i, f in enumerate(pxx_noise):
        for j, psd in enumerate(pxx[i]):
            pxx[i][j] = max(ZERO, psd - np.average(f))
    
    im = ax.pcolormesh(time, freq, 10 * np.log10(pxx), shading='auto', vmin=VMIN, vmax=VMAX)
    plt.savefig('without_noise.png')
    #sf.write('my_32bit_file.wav', signal_data, sampling_frequency, 'PCM_32')
    #plt.show()




if __name__ == "__main__":
    main()
