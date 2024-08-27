#! /usr/bin/env python
"""
A part of of this code is taken from one of the demo file of
aubio @ https://github.com/aubio/aubio/blob/master/python/demos/demo_alsa.py

Frequencies of music notes are taken from 
https://pages.mtu.edu/~suits/notefreqs.html to create notefreq.pkl

Thank you!

"""
import numpy as np
import aubio
import sys
if sys.platform == 'linux':
    import alsaaudio
else:
    import pyaudio
sys.path.append('/home/jk/jk/python/')
from mytools import *
import os
import pathlib

def measureFrequency(que):

    # note-freq table - list of two lists
    # [
    #  [f1,    f2,    f3......],
    #  [note1, note2, note3,....]
    # ]
    curdir = pathlib.Path(__file__).parent.resolve()
    freqpath = os.path.join(curdir, 'notefreq.pkl')
    freqnote = load(freqpath)
    #print(freqnote)

    # constants
    samplerate = 44100
    win_s = 2048 * 2 
    hop_s = win_s // 2
    framesize = hop_s
    buffer_size = 1024
    n_channels = 1

    if sys.platform == 'linux':
        # set up audio input
        recorder = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE)
        recorder.setperiodsize(framesize)
        recorder.setrate(samplerate)
        recorder.setformat(alsaaudio.PCM_FORMAT_FLOAT_LE)
        recorder.setchannels(1)
    else:
        p = pyaudio.PyAudio()
        pyaudio_format = pyaudio.paFloat32
        stream = p.open(format=pyaudio_format,
                channels=n_channels,
                rate=samplerate,
                input=True,
                frames_per_buffer=buffer_size)

    # create aubio pitch detection (first argument is method, "default" is
    # "yinfft", can also be "yin", "mcomb", fcomb", "schmitt").
    #win_s = 4096 # fft size
    #hop_s = buffer_size # hop size
    #hop_s = 1024
    #print('\n*********', win_s, hop_s, '\n***************')
    pitcher = aubio.pitch("default", win_s, hop_s, samplerate)
    # set output unit (can be 'midi', 'cent', 'Hz', ...)
    pitcher.set_unit("Hz")
    # ignore frames under this level (dB)
    pitcher.set_silence(-10)

    print("Starting to listen, press Ctrl+C to stop")

    strings = {
            'e2' : 82,
            'a2' : 110,
            'd3' : 146.83,
            'g3' : 196.00,
            'b3' : 246.94,
            'e4' : 329.63,
            }
    def vInrange(v):
        freqs = freqnote[0] #
        #freqs = strings.values()
        for f in freqs:
            if v < f + 10 and v > f - 10:
                return True
        return False

    tune = 329.63 #(82#110 #146.83 # 196.00#246.94 #329.63)
    print("starts with tuning e4")
    print("to tune a different string presss Ctrl^C.  Then enter\
            the labels e2, a2, d3 etc")
    print("enter q to quit after Ctrl^c")

    count = 0
    freql = []
    avfreq = 0
    lnote = '?'
    hnote = '?'
    # main loop
    while True:
        try:
            if sys.platform == 'linux': # using pyalsaaudio
                # read data from audio input
                _, data = recorder.read()
                # convert data to aubio float samples
                samples = np.fromstring(data, dtype=aubio.float_type)
            else:
                # read data from audio input
                data = stream.read(buffer_size * 2)
                samples = np.fromstring(data, dtype=np.float32)
            # pitch of current frame
            freq = pitcher(samples)[0]
            # compute energy of current block
            energy = np.sum(samples**2)/len(samples)

            #print(freq) if freq != 0 else None

            # eliminating noise by selecting freq around 
            # notes 
            if vInrange(freq): freql.append(freq)
            # finding average freq
            if len(freql) == 2:
                sum_ = 0
                for v in freql:
                        sum_ += v
                        count += 1
                if count != 0:  avfreq = sum_/count
                # checking around which note frequency falls
                # - the lower, middle and upper frequencey for
                # visualization purpose
                # lf, mf, hf
                for i in range(len(freqnote[0]) - 1):
                    if avfreq >= freqnote[0][i] and avfreq <= freqnote[0][i+1]:
                        # delta - separation of notes
                        delta = freqnote[0][i+1] - freqnote[0][i]
                        # if avfreq x<- avfreq ->(halfway)<-     ->y  
                        # then choose a lower freq as lf
                        if avfreq <= freqnote[0][i] + 0.5 * delta:
                            lnote, lf = (freqnote[1][i - 1], freqnote[0][i - 1]) if i!=0 else ('?', 16)
                            mnote, mf = freqnote[1][i], freqnote[0][i]
                            hnote = freqnote[1][i + 1] if i + 1 <= len(freqnote[0]) - 1 else 'C9'
                            hf = freqnote[0][i + 1] if i + 1 <= len(freqnote[0]) - 1 else 8372
                            fmark = int(10 * (avfreq - mf)/(hf - mf))
                            print(lnote + 10 * '~' + mnote + (fmark - 1) * '~' + 'X' + (10 - fmark) * '~' + hnote)
                            # 1 in the last tuple represents the first range
                            # where avfreq falls
                            qdata = ((lf, lnote), (mf, mnote), (hf, hnote), (avfreq, 1))
                            que.put(qdata)
                        # if x<-      (halfway)  avfreq     ->y
                        # then choose next to next freq as hf
                        else:
                            lnote, lf = freqnote[1][i], freqnote[0][i]
                            mnote, mf = freqnote[1][i + 1], freqnote[0][i + 1]
                            hnote = freqnote[1][i + 2] if i + 2 <= len(freqnote[0]) - 1 else 'C9'
                            hf = freqnote[0][i + 2] if i + 2 <= len(freqnote[0]) - 1 else 8372
                            fmark = int(10 * (avfreq - lf)/(mf - lf))
                            print(lnote + (fmark - 1) * '~' + 'X' + (10- fmark) * '~' + mnote + 10 * '~' +  hnote)
                            # 2 in the last tuple represents the second range
                            # where avfreq falls
                            qdata = ((lf, lnote), (mf, mnote), (hf, hnote), (avfreq, 2))
                            que.put(qdata)
                        #print(lnote, mnote, hnote, avfreq)
                        break
                #print(lnote, hnote, avfreq)
                freql = []
                count = 0
                avfreq = 0
        except KeyboardInterrupt:
            print("Ctrl+C pressed, exiting")
            tune_ = input('string: ')
            tune = strings[tune_]
            if tune_ == 'q':
                break
if __name__ == '__main__':
    class QueMock:
        def put(self, x):
            print(x)
    que = QueMock()
    measureFrequency(que)
