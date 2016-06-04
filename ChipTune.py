import math
import numpy
import pyaudio
import copy
import re
import wave

class ChipTune:
    def square(frequency, length, volume, rate):
        length = int(length * rate)
        factor = float(frequency) * (math.pi * 2) / rate
        k = [volume if x%(2*math.pi)>math.pi else -volume for x in numpy.arange(length) * factor]
        return k


    def play_tone(stream, frequency=440, length=1, volume=.5, rate=44100):
        chunks = []
        chunks.append(ChipTune.square(frequency, length, volume, rate))

        chunk = numpy.concatenate(chunks) * 0.25

        stream.write(chunk.astype(numpy.float32).tostring())


    class Note:
        def __init__(self, hertz, length, volume=.5):
            self.hertz = hertz
            self.volume = volume
            self.length = length

    Notes = {
        "C": 130.81,
        "C#":138.59,
        "D": 146.83,
        "D#":155.56,
        "E" :164.81,
        "F" :174.61,
        "F#":185.00,
        "G" :196.00,
        "G#":207.65,
        "A" :220.00,
        "A#":233.08,
        "B" :246.94
    }

    def playNotes(n1=[],n2=[],n3=[],r=0.2):
        p = pyaudio.PyAudio()
        chunks = []
        intermediate = []
        for i in range(3):
            h = [n1,n2,n3][i]
            if h!=[]:
                intermediate.append([])
                for j in range(len(h)):
                    intermediate[i] += ChipTune.square(h[j].hertz, r*h[j].length, h[j].volume, 44100)
        for i in range(max([len(k) for k in intermediate])):
            sume = 0
            count = 0
            for j in intermediate:
                if i < len(j):
                    sume += j[i]
                    count += 1
            chunks.append([sume/count])
        print(len(chunks))
        chunk = numpy.concatenate(chunks) * 0.25
        
        stream = p.open(format=pyaudio.paFloat32,
                    channels=1, rate=44100, output=1
                        ,frames_per_buffer=1024)
        
        with wave.open("out.wav", "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(p.get_sample_size(pyaudio.paFloat32))
            w.setframerate(44100)
            w.writeframes(chunk.astype(numpy.float32).tostring())

        stream.write(chunk.astype(numpy.float32).tostring())

        #write to file
        stream.close()
        p.terminate()



    def replace(notes, q):
        a = copy.deepcopy(notes)
        for key in q:
            for i in range(len(notes)):
                if notes[i].hertz == key:
                    a[i].hertz = q[key]
        return a

    def fileToNotes(filename):
        k = []
        with open(filename,"r") as f:
            k = "".join(f.readlines()).replace("\n"," ").split("+")
            print(k)
        ar = []
        reg = re.compile("(\.\d)?(0|([ABCDEFG]\#?))\d(\,\d\d)?")
        for i in k:
            ar.append([])
            for j in i.split(" "):
                if reg.match(j):
                    if j[len(j)-1] == "\n":
                        j = j[:-1]
                    l=1
                    v=.5
                    note = ""
                    point = 0
                    pitch = 1
                    if j[0] == '.':
                        l = 2**int(j[1])
                        point+=2
                    if j[point] != "0":
                        if len(j) - point == 3 or j[(point+3)%len(j)]==',':
                            note = j[point:point+2]
                            point+=2
                        else:
                            note = j[point]
                            point+=1
                        pitch = j[point]
                    else:
                        pitch = 0
                        l=0
                        point+=1
                    point+=1
                    if j[point%len(j)] == ',':
                        point+=1
                        v=int(j[point:point+2])/100.0
                    ar[len(ar)-1].append(ChipTune.Note(ChipTune.Notes[note]*2**(int(pitch)-3), l, v))
        return ar
                    

if __name__ == "__main__":
    r = 1/9
    a = ChipTune.fileToNotes("USA.txt")
    while len(a)<3:
        a.append([])
    ChipTune.playNotes(a[0],a[1],a[2],r)
