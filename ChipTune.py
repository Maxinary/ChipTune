import math
import numpy
import pyaudio
import copy
import wave

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
        for i in range(max([len(n1),len(n2),len(n3)])):
            k=[]
            c=0
            for j in [n1,n2,n3]:
                if len(j)>i:
                    k+=[ChipTune.square(j[i].hertz, r, .5, 44100)]
                    c+=1
                else:
                    k+=[ChipTune.square(0, r, 0, 44100)]
            chunks.append([(k[0][x]+k[1][x]+k[2][x])/c for x in range(int(r*44100))])
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

if __name__ == "__main__":
    r = 1/5
    main = [
            ChipTune.Note(ChipTune.Notes["G"]),
            ChipTune.Note(ChipTune.Notes["D"]*2),
            ChipTune.Note(ChipTune.Notes["B"]*2),
            ChipTune.Note(ChipTune.Notes["A"]*2),
            ChipTune.Note(ChipTune.Notes["B"]*2),
            ChipTune.Note(ChipTune.Notes["D"]*2),
            ChipTune.Note(ChipTune.Notes["B"]*2),
            ChipTune.Note(ChipTune.Notes["A"]*2)
        ]
    up = [
            ChipTune.Note(ChipTune.Notes["G"]),
            ChipTune.Note(ChipTune.Notes["E"]*2),
            ChipTune.Note(ChipTune.Notes["C"]*4),
            ChipTune.Note(ChipTune.Notes["B"]*2),
            ChipTune.Note(ChipTune.Notes["C"]*4),
            ChipTune.Note(ChipTune.Notes["E"]*2),
            ChipTune.Note(ChipTune.Notes["C"]*4),
            ChipTune.Note(ChipTune.Notes["E"]*2)
        ]
    ChipTune.playNotes(
        2*main+
        2*up+
        2*ChipTune.replace(up, {ChipTune.Notes["E"]*2:ChipTune.Notes["F#"]*2})+
        2*main
        ,
        [ChipTune.Note(x.hertz, 0.25) for x in (
            2*(
                2*[ChipTune.Note(ChipTune.Notes["G"])]+
                3*[ChipTune.Note(ChipTune.Notes["G"],0)]+
                2*[ChipTune.Note(ChipTune.Notes["D"]*2)]+
                [ChipTune.Note(ChipTune.Notes["G"],0)])+
            2*(
                2*[ChipTune.Note(ChipTune.Notes["G"])]+
                3*[ChipTune.Note(ChipTune.Notes["G"],0)]+
                2*[ChipTune.Note(ChipTune.Notes["E"]*2)]+
                [ChipTune.Note(ChipTune.Notes["G"],0)])+
            2*(
                2*[ChipTune.Note(ChipTune.Notes["G"])]+
                3*[ChipTune.Note(ChipTune.Notes["G"],0)]+
                2*[ChipTune.Note(ChipTune.Notes["F#"]*2)]+
                [ChipTune.Note(ChipTune.Notes["G"],0)])+
            2*(
                2*[ChipTune.Note(ChipTune.Notes["G"])]+
                3*[ChipTune.Note(ChipTune.Notes["G"],0)]+
                2*[ChipTune.Note(ChipTune.Notes["D"]*2)]+
                [ChipTune.Note(ChipTune.Notes["G"],0)])
        )]
    )
