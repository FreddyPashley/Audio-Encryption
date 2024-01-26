import socket
import pylab
import soundfile
import os
import numpy as np
from random import randint

# Server configuration
HOST = '127.0.0.1'  # localhost
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
character_set = " ABCDEFGHIJKLMNOPQRSTUVWYZabcdefghijklmnopqrstuvwxyz0123456789.!?,:;'@[]{}\"£$%^&*()/*-+_=`¬\\|"

def createFrequencies(message, output_file, space=100):
    """Encodes message into file"""
    if len(message) >= 100:
        return "Message cannot exceed 99 characters"
        """This limit is due to encoding the index of where the character appears in the message.
        As the frequencies are ##ii (## = frequency, ii = index), the most we can do is index 99."""
    
    # Creates frequencies to add based on where the character is in the character set and in the message
    frequencies = []
    for ci, c in enumerate(message):
        f_base = (character_set.index(c) + 1) * space
        frequencies.append(f_base + (ci + 1))

    for i in range(space // 10, space, space // 10):
        if randint(1, space // 10) == 1:
            frequencies.append(i)
    for i in range((len(character_set) * space) + (space - 1), space ** 2, space // 10):
        if randint(1, space // 10) == 1:
            frequencies.append(i)

    duration = 1  # Duration of the audio in seconds.
    sample_rate = 44100  # Sample rate (samples per second).
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)  # Generate time array.

    # Generate audio samples.
    audio_samples = np.zeros_like(t)
    for freq in frequencies:
        audio_samples += np.sin(2 * np.pi * freq * t)
    audio_samples /= np.max(np.abs(audio_samples))  # Normalise audio samples

    soundfile.write(output_file, audio_samples, sample_rate, subtype="PCM_24")  # Save audio to .wav file.
    return True


while True:
    persistent_files = input("Save latest audio file? (y/n) ").lower()
    if persistent_files == "y":
        persistent_files = True
        break
    elif persistent_files == "n":
        persistent_files = False
        break


while True:
    message = input("")
    # Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Bind the socket to the address and port
        server_socket.bind((HOST, PORT))

        # Listen for incoming connections
        server_socket.listen()

        # Accept a connection and establish a connection with the client
        conn, addr = server_socket.accept()

        r = createFrequencies(message, output_file="message.wav")

        if r:
            # Send the sound file
            with open('message.wav', 'rb') as file:
                data = file.read()
                conn.sendall(data)
            conn.send(b"END_OF_TRANSMISSION")
            if not persistent_files:
                os.remove("message.wav")    
            print(">> Sent <<")
