import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email import encoders
import os
import numpy as np
import soundfile
from random import randint

# Email configuration
SENDER_EMAIL = 'fred@fpashley.xyz'  # Update with your email address
RECIPIENT_EMAIL = 'encryption@fpashley.xyz'  # Update with recipient's email address
EMAIL_PASSWORD = 'qbcxz47m!'  # Update with your email password

# Character set and server configuration
character_set = " ABCDEFGHIJKLMNOPQRSTUVWYZabcdefghijklmnopqrstuvwxyz0123456789.!?,:;'@[]{}\"£$%^&*()/*-+_=`¬\\|"
space = 100  # Space between frequencies


def createFrequencies(message, output_file):
    """Encodes message into file"""
    if len(message) >= 100:
        return "Message cannot exceed 99 characters"

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


# Create the message.wav file
message = input("Enter message: ")
createFrequencies(message, output_file="message.wav")

# Email sending functionality
msg = MIMEMultipart()
msg['From'] = SENDER_EMAIL
msg['To'] = RECIPIENT_EMAIL
msg['Subject'] = 'New encrypted message'

# Attach the audio file
filename = 'message.wav'
attachment = open(filename, 'rb')
part = MIMEBase('application', 'octet-stream')
part.set_payload(attachment.read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
msg.attach(part)

# Connect to the SMTP server, login, send the email, and close the connection
server = smtplib.SMTP('server167.web-hosting.com ', 465)
server.starttls()
server.login(SENDER_EMAIL, EMAIL_PASSWORD)
server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
server.quit()

# Remove the temporary audio file
os.remove("message.wav")
print("Email Sent with Audio Attachment")
