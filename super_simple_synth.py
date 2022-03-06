import math
import pyaudio
import itertools
import numpy as np
from pygame import midi
from tremolo import Tremolo
import tremolo

BUFFER_SIZE = 256
SAMPLE_RATE = 44100
NOTE_AMP = 0.1
tremoloOut = 0

# -- HELPER FUNCTIONS --
def get_sin_oscillator(freq=55, amp=1, sample_rate=SAMPLE_RATE):
    increment = (2 * math.pi * freq)/ sample_rate
    return (math.sin(v) * amp * NOTE_AMP \
            for v in itertools.count(start=0, step=increment))

def get_samples(trem, notes_dict, num_samples=BUFFER_SIZE, ):
    # outSample = []
    # for _ in range(num_samples):
    #     out = 0
    #     for _, osc in notes_dict.items():
    #         out += int(trem.TremoloUpdate(next(osc))) * 32767
    #     outSample.append(out)
    # return outSample

    # return [sum([int(next(osc) * 32767) \
    #         for _, osc in notes_dict.items()]) \
    #         for _ in range(num_samples)]

    outSample = []
    for _ in range(num_samples):
        out = 0
        ifFirstNote = True
        for _, osc in notes_dict.items():
            if ifFirstNote == True:
                out += int(trem.TremoloUpdate(next(osc)) * 32767)
                ifFirstNote = False
            else:
                out += int(trem.TremoloGet(next(osc)) * 32767)
        outSample.append(out)
    return outSample

# -- INITIALIZION --
midi.init()
trem = Tremolo(0.5, 3, SAMPLE_RATE)
default_id = midi.get_default_input_id()
midi_input = midi.Input(device_id=default_id)

stream = pyaudio.PyAudio().open(
    rate=SAMPLE_RATE,
    channels=1,
    format=pyaudio.paInt16,
    output=True,
    frames_per_buffer=BUFFER_SIZE
)

# -- RUN THE SYNTH --
try: 
    print("Starting...")
    notes_dict = {}
    while True:
        if notes_dict:
            # Play the notes
            samples = get_samples(trem,notes_dict)
            samples = np.int16(samples).tobytes()
            stream.write(samples)
        if midi_input.poll():
            # Add or remove notes from notes_dict
            for event in midi_input.read(num_events=16):
                (status, note, vel, _), _ = event
                if status == 0x80 and note in notes_dict:
                    del notes_dict[note]
                elif status == 0x90 and note not in notes_dict:
                    freq = midi.midi_to_frequency(note)
                    notes_dict[note] = get_sin_oscillator(freq=freq, amp=vel/127)
                    
except KeyboardInterrupt as err:
    midi_input.close()
    stream.close()
    print("Stopping...")
