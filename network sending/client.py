import imaplib
import email
import os
import numpy as np
import soundfile
import pylab

# Email configuration
EMAIL = 'encryption@fpashley.xyz'  # Update with your email address
PASSWORD = 'qbcxz47m!'  # Update with your email password
IMAP_SERVER = 'server167.web-hosting.com '
MAILBOX = 'INBOX'

# Character set and server configuration
character_set = " ABCDEFGHIJKLMNOPQRSTUVWYZabcdefghijklmnopqrstuvwxyz0123456789.!?,:;'@[]{}\"£$%^&*()/*-+_=`¬\\|"
space = 100  # Space between frequencies


def detectFrequencies(file_path, threshold=0.75, DEV=False):
    """Decodes file into message"""

    audio_samples, sample_rate = soundfile.read(file_path, dtype="float32")
    number_samples = len(audio_samples)

    freq_bins = np.fft.fftfreq(number_samples, d=1 / sample_rate)
    fft_data = np.fft.fft(audio_samples)
    fft_magnitude = np.abs(fft_data)

    positive_freq_mask = freq_bins > 0
    freq_bins = freq_bins[positive_freq_mask]
    fft_magnitude = fft_magnitude[positive_freq_mask]

    pylab.plot(freq_bins, fft_magnitude, color="black")
    pylab.xlabel("Freq (Hz)")
    pylab.ylabel("Magnitude")

    detected_frequencies = []
    filler_frequencies = []
    target_frequencies = [i for i in range(0, space ** 2)]
    for freq in target_frequencies:
        freq_bin = np.abs(freq_bins - freq)
        freq_idx = np.argmin(freq_bin)
        magnitude = fft_magnitude[freq_idx] / np.max(fft_magnitude)
        if magnitude > threshold:
            if freq < (len(character_set) * space) + (space - 1) and freq >= space:
                detected_frequencies.append((freq, magnitude))
            else:
                filler_frequencies.append((freq, magnitude))

    if DEV:
        for freq, magnitude in detected_frequencies:
            pylab.plot(freq, magnitude, "go")
        for freq, magnitude in filler_frequencies:
            pylab.plot(freq, magnitude, "ro")

    largest_freq = max([i[0] for i in detected_frequencies])
    max_length = len(str(largest_freq))
    characters = {}
    for freq, magnitude in detected_frequencies:
        freq = str(freq)
        index = (int(freq) // space) - 1
        freq = ("0" * (max_length - len(freq))) + freq
        order = int(freq[2:]) - 1
        characters[str(order)] = character_set[index]

    final_str = ""
    for k in sorted([int(i) for i in characters.keys()]):
        final_str += characters[str(k)]

    if DEV:
        print(final_str)
        pylab.xlim(0, space ** 2)
        pylab.show()
        return ""
    else:
        return final_str


def download_latest_attachment():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select(MAILBOX)

    result, data = mail.search(None, 'ALL')
    latest_email_id = data[0].split()[-1]

    result, data = mail.fetch(latest_email_id, '(RFC822)')
    raw_email = data[0][1]
    email_message = email.message_from_bytes(raw_email)

    for part in email_message.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        file_name = part.get_filename()
        if file_name:
            file_path = os.path.join(os.getcwd(), file_name)
            with open(file_path, 'wb') as fp:
                fp.write(part.get_payload(decode=True))
            return file_path


while True:
    persistent_files = input("Save latest audio file? (y/n) ").lower()
    if persistent_files == "y":
        persistent_files = True
        break
    elif persistent_files == "n":
        persistent_files = False
        break

while True:
    try:
        file_path = download_latest_attachment()
        print(detectFrequencies(file_path))
        if not persistent_files:
            os.remove(file_path)
    except Exception as e:
        print("Error:", e)
