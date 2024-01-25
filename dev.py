import numpy as np
import soundfile
import pylab
import matplotlib
from warnings import filterwarnings
import os

filterwarnings("ignore")  # Suppresses 'complex numbers warning' in terminal when working with frequencies.
matplotlib.use("tkagg")  # Use tkinter with matplotlib (I know, not nice)

character_set = " ABCDEFGHIJKLMNOPQRSTUVWYZabcdefghijklmnopqrstuvwxyz0123456789.!?,:;'@[]{}\"£$%^&*()/*-+_=`¬\\|"

def detectFrequencies(file_path, threshold=.75, DEV=True):
    """Decodes file into message"""

    audio_samples, sample_rate = soundfile.read(file_path, dtype="float32")  # Reading the audio file and getting the audio samples from it for analysis.
    number_samples = len(audio_samples)

    freq_bins = np.fft.fftfreq(number_samples, d=1/sample_rate)  # Get 'active' frequencies from file.
    fft_data = np.fft.fft(audio_samples)  # Get audio from relevant 'active' frequencies.
    fft_magnitude = np.abs(fft_data)  # Get the magnitude (aka strength) of each audio sample.

    # Removes the negative frequencies as they are not relevant.
    positive_freq_mask = freq_bins > 0
    freq_bins = freq_bins[positive_freq_mask]
    fft_magnitude = fft_magnitude[positive_freq_mask]

    # Plot frequency chart (visual of file).
    pylab.plot(freq_bins, fft_magnitude, color="black")
    pylab.xlabel("Freq (Hz)")
    pylab.ylabel("Magnitude")

    # Go through all possible frequencies and check if there's a positive ID there.
    detected_frequencies = []
    target_frequencies = [i for i in range(100, 10_000)]  # A list of all possible frequencies.
    print("Decoding...")
    for freq in target_frequencies:
        freq_bin = np.abs(freq_bins - freq)
        freq_idx = np.argmin(freq_bin)
        magnitude = fft_magnitude[freq_idx] / np.max(fft_magnitude)  # 'Strength' of audio at frequency.
        if magnitude > threshold:  # Is the strength enough to count as a positive ID?
            detected_frequencies.append((freq, magnitude))

    # Plots positive frequencies on chart
    for freq, magnitude in detected_frequencies:
        pylab.plot(freq, magnitude, "bo")

    """Creates a 'characters' dictionary with values of characters in the decoded message,
    and keys of the order which they appear based on frequency."""
    largest_freq = max([i[0] for i in detected_frequencies])
    max_length = len(str(largest_freq))
    characters = {}
    for freq, magnitude in detected_frequencies:
        freq = str(freq)
        index = (int(freq)//100) - 1
        freq = ("0" * (max_length - len(freq))) + freq
        order = int(freq[2:]) - 1
        characters[str(order)] = character_set[index]
            
    # Generates the final message.
    final_str = ""
    for k in sorted([int(i) for i in characters.keys()]):
        final_str += characters[str(k)]

    if DEV:
        print(final_str)
        pylab.xlim(0, 10_000)  # Limit x-axis scale.
        pylab.show()
        return ""
    else:
        return final_str


def createFrequencies(message, output_file):
    """Encodes message into file"""
    if len(message) >= 100:
        return "Message cannot exceed 99 characters"
        """This limit is due to encoding the index of where the character appears in the message.
        As the frequencies are ##ii (## = frequency, ii = index), the most we can do is index 99."""
    
    # Creates frequencies to add based on where the character is in the character set and in the message
    frequencies = []
    for ci, c in enumerate(message):
        f_base = (character_set.index(c) + 1) * 100
        frequencies.append(f_base + (ci + 1))

    duration = 1  # Duration of the audio in seconds.
    sample_rate = 44100  # Sample rate (samples per second).
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)  # Generate time array.

    # Generate audio samples.
    audio_samples = np.zeros_like(t)
    for freq in frequencies:
        audio_samples += np.sin(2 * np.pi * freq * t)
    audio_samples /= np.max(np.abs(audio_samples))  # Normalise audio samples

    soundfile.write(output_file, audio_samples, sample_rate, subtype="PCM_24")  # Save audio to .wav file.
    return file_path + " created successfully"


if __name__ == "__main__":
    # User interface
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
            print(createFrequencies(message, file_path + ".wav"))
        print("=" * 10)
