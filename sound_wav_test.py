import math, struct

alphabet = "aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ"
def from_alphabet(s):
  length = len(alphabet)
  return (alphabet.index(s) / length) * 2.0 - 1.0

def make_sample(s):
  return struct.pack("<h", max(-32767, min(round(s*32767), 32767))) # 16-битное число

class AS: # Символьный sound
  def __init__(self, symbols, start=0, endin=-1, framesspeed=1):
    self.smb = symbols
    self.speed = framesspeed
    self.endin = endin
    self.start = start
  def get(self, frame):
    if self.start>frame: return False
    if self.endin > -1 and frame >= self.endin:
        return False

    index = (frame-self.start) // self.speed

    actual_index = index % len(self.smb)
    a = self.smb[actual_index]
    if not a in alphabet:
      return False
    else:
      return a

class SS: # Синусоидная часточная-волновая sound
  def __init__(self, a, start=0, endin=-1, framesspeed=1):
    self.f = [None, None]
    self.f[0] = a[0]
    self.f[1] = a[1]

    self.speed = framesspeed
    self.endin = endin
    self.start = start
    self.phase = 0
  def get(self, frame, sample_rate):
    if self.start > frame:
        return False
    if self.endin > -1 and frame >= self.endin:
        return False

    t = float(frame) / sample_rate

    f = 0     # Частота
    v = 1.0 # Громкость

    f = self.f[0](t)
    if callable(self.f[1]):
      v = self.f[1](t)
    else:
      v = self.f[1]

    self.phase += 2 * math.pi * f / sample_rate
    self.phase %= 2 * math.pi
    return v * math.sin(self.phase*self.speed)


import random
# ОСНОВНЫЕ ЗНАЧЕНИЯ
frames = [
  SS([lambda a: random.random()*400,lambda a:  random.random()], 0, -1, 1),
  #AS("AbZy", 0, -1, 100),
  #SS([lambda d: max(0,1-math.sinh(d*4-d*4//1))*500, 1.0], 0, -1, 10)
  #AS("ZyBe", 0, 44100*1, 50),
  #AS("AzAz", 44100*2, -1, 200),
  #AS("AzAzAzAzaZaZaZaZaZMpMpMpMpMpmMmMmMmMmMmMmMmM__________________________________", 0, -1, 200),
  #lambda x: math.sin(2*math.pi*440.0*x)
] # Ну типа кадры всяк такое
sample_rate = 44100 # Количество фреймов в секунду (частота дискредизации Гц)
duration = 4.0 # Кол-во секунд
dividebyframes = True # Деление на кол-во элементов в frames, если необходимо

import wave
file = wave.open("./syntetic_audio.wav", "w")

samples_count = int(sample_rate * duration)
file.setparams((1, 2, sample_rate, samples_count, "NONE", "not compressed"))


audio = []
for i in range(samples_count):
  t = float(i) / sample_rate
  s = 0.0

  for f in frames:
    if type(f) is AS:
      a = f.get(i)
      if a != False:
        s += from_alphabet(a)
    elif type(f) is SS:
      a = f.get(i,sample_rate)
      if a != False:
        s += a
    elif callable(f):
      s += f(t)

  s = s / len(frames)
  audio.append(make_sample(s))

file.writeframes(b"".join(audio))
file.close()

print("Типа да файл готав навернаи")