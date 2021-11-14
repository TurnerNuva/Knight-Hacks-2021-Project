import jetson.inference
import jetson.utils

import pyaudio
import wave
import pysoundfile as sf

import time

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import digitalio

from google.cloud import speech
import io


#jetson nano facial recognition
#===============================================================================================================

#INSERT HERE

#record audio
#===============================================================================================================
def record_audio():

    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 2
    fs = 44100  # Record at 44100 samples per second
    seconds = 3
    filename = "output.wav"

    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    print('Recording')

    stream = p.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True)

    frames = []  # Initialize array to store frames

    # Store data in chunks for 3 seconds
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream 
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()

    print('Finished recording')

    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    # file convert
    data, samplerate = sf.read('output.wav')
    sf.write('audio.flac', data, samplerate)

    return "audio.flac"

#Google API
#===============================================================================================================

def transcribe_file(speech_file):

    client = speech.SpeechClient()

    with io.open(speech_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=44100,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    
    # for result in response.results:
    #     # The first alternative is the most likely one for this portion.
    #     print(u"Transcript: {}".format(result.alternatives[0].transcript))

    return response

#Display to oled screen
#===============================================================================================================
def display_message(response_string):
    spi = busio.SPI(board.SCK, MOSI=board.MOSI)
    reset_pin = digitalio.DigitalInOut(board.D4) # any pin!
    cs_pin = digitalio.DigitalInOut(board.D5)    # any pin!
    dc_pin = digitalio.DigitalInOut(board.D6)    # any pin!

    oled = adafruit_ssd1306.SSD1306_SPI(128, 32, spi, dc_pin, reset_pin, cs_pin)

    # Clear display.
    oled.fill(0)
    oled.show()

    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    width = oled.width
    height = oled.height
    image = Image.new("1", (width, height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Draw some shapes.
    # First define some constants to allow easy resizing of shapes.
    padding = -2
    top = padding
    bottom = height - padding
    # Move left to right keeping track of the current x position for drawing shapes.
    x = 0


    # Load default font.
    font = ImageFont.load_default()

    # Alternatively load a TTF font.  Make sure the .ttf font file is in the
    # same directory as the python script!
    # Some other nice fonts to try: http://www.dafont.com/bitmap.php
    # font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)

    while True:

        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        # Write four lines of text.

        draw.text((x, top + 0), "Testing", font=font, fill=255)
        draw.text((x, top + 8), "This ", font=font, fill=255)
        draw.text((x, top + 16), "Display", font=font, fill=255)
        draw.text((x, top + 25), "Out", font=font, fill=255)

        # Display image.
        oled.image(image)
        oled.show()
        time.sleep(0.1)


    def main():
        
        #Jetson here

        audio_file = record_audio()

        response_string = transcribe_file(audio_file)

        display_message(response_string)


if __name__ == '__main__':
    main()