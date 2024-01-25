import numpy as np
import soundfile
import scipy.signal
import pylab
import matplotlib
import warnings
import os

warnings.filterwarnings("ignore")  # suppress complex numbers warning in terminal
matplotlib.use("tkagg")

character_set = " ABCDEFGHIJKLMNOPQRSTUVWYZabcdefghijklmnopqrstuvwxyz0123456789.!?,:;'@[]{}\"£$%^&*()/*-+_=`¬\\|"

def detectFrequencies(file_path, threshold=.75, DEV=True):

    audio_samples, sample_rate = soundfile.read(file_path, dtype="float32")
    number_samples = len(audio_samples)

    duration = round(number_samples / sample_rate, 2)

    freq_bins = np.fft.fftfreq(number_samples, d=1/sample_rate)
    fft_data = np.fft.fft(audio_samples)
    fft_magnitude = np.abs(fft_data)

    positive_freq_mask = freq_bins > 0
    freq_bins = freq_bins[positive_freq_mask]
    fft_magnitude = fft_magnitude[positive_freq_mask]

    # Plot FFT
    pylab.plot(freq_bins, fft_magnitude, color="black")
    pylab.xlabel("Freq (Hz)")
    pylab.ylabel("Magnitude")

    # Detect target frequencies
    detected_frequencies = []
    target_frequencies = [i for i in range(100, 10000)]
    print("Decoding...")
    for freq in target_frequencies:
        idx = np.argmax(np.abs(fft_data))
        freq_bin = np.abs(freq_bins - freq)
        freq_idx = np.argmin(freq_bin)
        magnitude = fft_magnitude[freq_idx] / np.max(fft_magnitude)
        if magnitude > threshold:
            detected_frequencies.append((freq, magnitude))

    character_frequencies = []
    for freq, magnitude in detected_frequencies:
        pylab.plot(freq, magnitude, 'bo')  # Mark detected frequencies

    largest_freq = max([i[0] for i in detected_frequencies])
    max_length = len(str(largest_freq))
    characters = {}
    for freq, magnitude in detected_frequencies:
        freq = str(freq)
        index = (int(freq)//100)-1
        freq = "0"*(max_length - len(freq)) + freq
        order = int(freq[2:])-1
        characters[str(order)] = character_set[index]
            
    final_str = ""
    for k in sorted([int(i) for i in characters.keys()]):
        final_str += characters[str(k)]

    if DEV:
        print(final_str)

        # Limit x-axis scale
        pylab.xlim(0, 10000)

        pylab.show()
        return
    else:
        return final_str


def createFrequencies(message, output_file):
    if len(message) >= 100:
        return "Message cannot exceed 99 characters"
    
    frequencies = []
    for ci, c in enumerate(message):
        f_base = (character_set.index(c)+1)*100
        frequencies.append(f_base+(ci+1))
    duration = 1  # Duration of the audio in seconds
    sample_rate = 44100  # Sample rate (samples per second)

    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Generate audio samples
    audio_samples = np.zeros_like(t)
    for freq in frequencies:
        audio_samples += np.sin(2 * np.pi * freq * t)

    # Normalize audio samples
    audio_samples /= np.max(np.abs(audio_samples))

    # Save audio to WAV
    soundfile.write(output_file, audio_samples, sample_rate, subtype='PCM_24')

    return file_path + " created successfully"


if __name__ == "__main__":
    while True:
        choice = ""
        while choice not in ["d", "decode", "e", "encode"]:
            choice = input("Encode/decode ").lower()
        if choice in ["d", "decode"]:
            file_path = ""
            while not os.path.exists(file_path):
                file_path = input("File path: ")
            print(detectFrequencies(file_path))
        else:
            message = ""
            while message == "":
                message = input("Message: ")
            file_path = input("File name: ")
            while os.path.exists(file_path):
                file_path = input("File name: ")
            print(createFrequencies(message, file_path+".wav"))
        print("="*10)
