import socket
import pylab
import soundfile
import os
import numpy as np

# Server configuration
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server
character_set = " ABCDEFGHIJKLMNOPQRSTUVWYZabcdefghijklmnopqrstuvwxyz0123456789.!?,:;'@[]{}\"£$%^&*()/*-+_=`¬\\|"

def detectFrequencies(file_path, threshold=.75, DEV=False, space=100):
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
    filler_frequencies = []
    target_frequencies = [i for i in range(0, space ** 2)]  # A list of all possible frequencies.
    #print("Decoding...")
    for freq in target_frequencies:
        freq_bin = np.abs(freq_bins - freq)
        freq_idx = np.argmin(freq_bin)
        magnitude = fft_magnitude[freq_idx] / np.max(fft_magnitude)  # 'Strength' of audio at frequency.
        if magnitude > threshold:  # Is the strength enough to count as a positive ID?
            if freq < (len(character_set) * space) + (space - 1) and freq >= space:
                detected_frequencies.append((freq, magnitude))
            else:
                filler_frequencies.append((freq, magnitude))

    if DEV:
        # Plots positive frequencies on chart
        for freq, magnitude in detected_frequencies:
            pylab.plot(freq, magnitude, "go")
        # Plots filler frequencies on chart
        for freq, magnitude in filler_frequencies:
            pylab.plot(freq, magnitude, "ro")

    """Creates a 'characters' dictionary with values of characters in the decoded message,
    and keys of the order which they appear based on frequency."""
    largest_freq = max([i[0] for i in detected_frequencies])
    max_length = len(str(largest_freq))
    characters = {}
    for freq, magnitude in detected_frequencies:
        freq = str(freq)
        index = (int(freq) // space) - 1
        freq = ("0" * (max_length - len(freq))) + freq
        order = int(freq[2:]) - 1
        characters[str(order)] = character_set[index]
            
    # Generates the final message.
    final_str = ""
    for k in sorted([int(i) for i in characters.keys()]):
        final_str += characters[str(k)]

    if DEV:
        print(final_str)
        pylab.xlim(0, space ** 2)  # Limit x-axis scale.
        pylab.show()
        return ""
    else:
        return final_str


while True:
    persistent_files = input("Save latest audio file? (y/n) ").lower()
    if persistent_files == "y":
        persistent_files = True
        break
    elif persistent_files == "n":
        persistent_files = False
        break

while True:
    # Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        # Connect to the server
        connection = False
        while not connection:
            try:
                client_socket.connect((HOST, PORT))
                connection = True
            except ConnectionRefusedError: pass

        # Receive the sound file
        with open('received_message.wav', 'wb') as file:
            client_socket.settimeout(10)
            while True:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    file.write(data)
                    if b"END_OF_TRANSMISSION" in data:
                        break
                except socket.timeout:
                    break
                except Exception as e:
                    break

        print(detectFrequencies("received_message.wav"))
        if not persistent_files:
            os.remove("received_message.wav")
