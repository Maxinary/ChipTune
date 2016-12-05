import math
import numpy
import pyaudio
import copy
import re
import struct
import wave

class ChipTune:
    def square(frequency, length, volume, rate, offset):
        length = int(length * rate)
        factor = float(frequency) * (math.pi * 2) / rate
        k = [volume if x%(2*math.pi)>math.pi else -volume for x in (numpy.arange(length)+offset) * factor]
        return k

    def triangle(frequency, length, volume, rate, offset):
        length = int(length * rate)
        factor = float(frequency) * (math.pi * 2) / rate
        k = [volume-2*volume*(x%(2*math.pi)-math.pi)/math.pi if x%(2*math.pi)>math.pi else -volume+2*volume*(x%(2*math.pi))/math.pi for x in (numpy.arange(length)+offset) * factor]
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

    def playNotes(nin,r=0.2):
        p = pyaudio.PyAudio()
        chunks = []
        intermediate = []
        for i in range(len(nin)):#iterate through the different "instrument melodies" in the input
            h = nin[i]#the current Melody
            intermediate.append([])
            for j in range(len(h)):#for every note/rest in that melody
                #Turn it into a tick array of volume pos at that point
                intermediate[i] += ChipTune.square(h[j].hertz, r*h[j].length, h[j].volume, 44100, 0)
        for i in range(max([len(k) for k in intermediate])):#go through all the notes and combine the melody
            sume = 0
            for j in intermediate:#iterate through all of the notes for that tick
                if i < len(j):#make sure that melody hasnt ended yet
                    sume += j[i]#add it to the thing
            chunks.append([sume/len(nin)*0.2])#scale the volume
        chunk = numpy.concatenate(chunks)
        
        stream = p.open(format=pyaudio.paFloat32,
                    channels=1, rate=44100, output=1)
        
        with wave.open("out.wav", "wb") as w:#write to file
            w.setnchannels(1)
            w.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            w.setframerate(44100.0)

            intVec = numpy.vectorize(lambda x: int(x))
            w.writeframes(intVec(chunk * 0.1 * 2**31).astype(numpy.int16).tostring())
            
        stream.write(chunk.astype(numpy.float32).tostring())

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
        ar = []
        num = re.compile("\.\-?\d*(\.\d*)?")
        reg = re.compile("(\.\-?\d*(\.\d*)?)?(O|([ABCDEFG]\#?\d(\,\d\d)?))")
        for i in k:
            ar.append([])
            for j in i.split(" "):
                if reg.match(j):
                    print(j)
                    if j[len(j)-1] == "\n":
                        j = j[:-1]
                    l=1
                    v=.5
                    note = ""
                    point = 0
                    pitch = 1
                    if j[0] == '.':
                        value = num.search(j)
                        l = 2**float(value.group(0)[1:])
                        point+=len(value.group(0))
                    if j[point] != "O":
                        if len(j) - point == 3 or j[(point+3)%len(j)]==',':
                            note = j[point:point+2]
                            point+=2
                        else:
                            note = j[point]
                            point+=1
                        pitch = j[point]
                    else:
                        pitch = 0
                        v = 0
                        note = "G"
                        point+=1
                    point+=1
                    if j[point%len(j)] == ',':
                        point+=1
                        v=int(j[point:point+2])/100.0
                    ar[len(ar)-1].append(ChipTune.Note(ChipTune.Notes[note]*2**(int(pitch)-3), l, v))
        return ar
                    

if __name__ == "__main__":
    r = 1/5
    a = ChipTune.fileToNotes("USA.txt")
    while len(a)<3:
        a.append([])
    ChipTune.playNotes(a,r)
