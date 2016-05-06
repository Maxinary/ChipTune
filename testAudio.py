import math
import numpy
import pyaudio
import copy

class ChipTune:
    def square(frequency, length, volume, rate):
        length = int(length * rate)
        factor = float(frequency) * (math.pi * 2) / rate
        k = [volume if x>0 else -volume for x in numpy.sin(numpy.arange(length) * factor)]
        return k


    def play_tone(stream, frequency=440, length=1, volume=.5, rate=44100):
        chunks = []
        chunks.append(ChipTune.square(frequency, length, volume, rate))

        chunk = numpy.concatenate(chunks) * 0.25

        stream.write(chunk.astype(numpy.float32).tostring())


    class Note:
        def __init__(self, hertz, volume=.5):
            self.hertz = hertz
            self.volume = volume

    Notes = {
        "C3": 130.81,
        "C3": 130.81,
        "C#3":138.59,
        "D3": 146.83,
        "D#3":155.56,
        "E3" :164.81,
        "F3" :174.61,
        "F#3":185.00,
        "G3" :196.00,
        "G#3":207.65,
        "A3" :220.00,
        "A#3":233.08,
        "B3" :246.94,
        "C4" :261.63,
        "C#4":277.18,
        "D4" :293.66,
        "D#4":311.13,
        "E4" :329.63,
        "F4" :349.23,
        "F#4":369.99,
        "G4": 392.00,
        "G#4":415.30,
        "A4": 440.00,
        "A#4":466.16,
        "B4" :493.88,
        "C5" :523.25,
        "C#5":554.37,
        "D5" :587.33,
        "D#5":622.25,
        "E5" :659.25,
        "F5" :698.46,
        "F#5":739.99,
        "G5" :783.99,
        "G#5":830.61,
        "A5" :880.00,
        "A#5":932.33,
        "B5" :987.77
        
    }

    def playNotes(n1=[],n2=[],n3=[],r=0.2):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paFloat32,
                    channels=1, rate=44100, output=1)

        chunks = []
        for i in range(max([len(n1),len(n2),len(n3)])):
            k=[]
            for j in [n1,n2,n3]:
                if len(j)>i:
                    k+=[ChipTune.square(j[i].hertz, r, .5, 44100)]
                else:
                    k+=[ChipTune.square(0, r, 0, 44100)]
            chunks.append([(k[0][x]+k[1][x]+k[2][x])/3 for x in range(int(r*44100))])
            chunk = numpy.concatenate(chunks) * 0.25

#                ChipTune.play_tone(stream, i.hertz, i.length)
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

if __name__ == "__main__":
    r = 1/5
    main = [
            ChipTune.Note(ChipTune.Notes["G3"]),
            ChipTune.Note(ChipTune.Notes["D4"]),
            ChipTune.Note(ChipTune.Notes["B4"]),
            ChipTune.Note(ChipTune.Notes["A4"]),
            ChipTune.Note(ChipTune.Notes["B4"]),
            ChipTune.Note(ChipTune.Notes["D4"]),
            ChipTune.Note(ChipTune.Notes["B4"]),
            ChipTune.Note(ChipTune.Notes["A4"])
        ]
    up = [
            ChipTune.Note(ChipTune.Notes["G3"]),
            ChipTune.Note(ChipTune.Notes["E4"]),
            ChipTune.Note(ChipTune.Notes["C5"]),
            ChipTune.Note(ChipTune.Notes["B4"]),
            ChipTune.Note(ChipTune.Notes["C5"]),
            ChipTune.Note(ChipTune.Notes["E4"]),
            ChipTune.Note(ChipTune.Notes["C5"]),
            ChipTune.Note(ChipTune.Notes["E4"])
        ]
    ChipTune.playNotes(
        2*main+
        2*up+
        2*ChipTune.replace(up, {ChipTune.Notes["E4"]:ChipTune.Notes["F#4"]})+
        2*main
        ,
        [ChipTune.Note(x.hertz, 0.25) for x in (
            2*(
                2*[ChipTune.Note(ChipTune.Notes["G3"])]+
                3*[ChipTune.Note(ChipTune.Notes["G3"],0)]+
                2*[ChipTune.Note(ChipTune.Notes["D4"])]+
                [ChipTune.Note(ChipTune.Notes["G3"],0)])+
            2*(
                2*[ChipTune.Note(ChipTune.Notes["G3"])]+
                3*[ChipTune.Note(ChipTune.Notes["G3"],0)]+
                2*[ChipTune.Note(ChipTune.Notes["E4"])]+
                [ChipTune.Note(ChipTune.Notes["G3"],0)])+
            2*(
                2*[ChipTune.Note(ChipTune.Notes["G3"])]+
                3*[ChipTune.Note(ChipTune.Notes["G3"],0)]+
                2*[ChipTune.Note(ChipTune.Notes["F#4"])]+
                [ChipTune.Note(ChipTune.Notes["G3"],0)])+
            2*(
                2*[ChipTune.Note(ChipTune.Notes["G3"])]+
                3*[ChipTune.Note(ChipTune.Notes["G3"],0)]+
                2*[ChipTune.Note(ChipTune.Notes["D4"])]+
                [ChipTune.Note(ChipTune.Notes["G3"],0)])
        )]
    )
