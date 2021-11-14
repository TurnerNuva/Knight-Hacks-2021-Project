import jetson.inference
import jetson.utils

import pyaudio
import wave
import soundfile as sf

import time

import serial
import Jetson.GPIO
import board
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import digitalio

from google.cloud import speech
import io


#jetson nano facial recognition
#===============================================================================================================

def look_for_person():
	import jetson.inference
	import jetson.utils

	net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold = 0.6) # adj. threshold for detection strength
	camera = jetson.utils.videoSource("/dev/video0")
	display = jetson.utils.videoOutput()

	while True:
		img = camera.Capture()
		detections = net.Detect(img)
		display.Render(img)
		display.SetStatus("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))
	
		for detection in detections:
			class_name = net.GetClassDesc(detection.ClassID)
			if class_name == "person":
				return
			else:
				print('Detected --> ' + class_name)

#record audio
#===============================================================================================================
def record_audio():

	chunk = 1024  # Record in chunks of 1024 samples
	sample_format = pyaudio.paInt16  # 16 bits per sample
	channels = 1
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
    config = speech.RecognitionConfig(encoding=speech.RecognitionConfig.AudioEncoding.FLAC, sample_rate_hertz=44100, language_code="en-US")
	response = client.recognize(config=config, audio=audio)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    
    for result in response.results:
    # The first alternative is the most likely one for this portion.
        print(u"Transcript: {}".format(result.alternatives[0].transcript))

    return response

#Display to oled screen
#===============================================================================================================

def display_message(response_string):
	ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
	ser.flush()
	#ser.write(b"test")
	ser.write(str(response_string).encode('utf-8'))		
	line = ser.readline().decode('utf-8').rstrip()
	print(line)
	time.sleep(1)


def main():

	look_for_person()

	audio_file = record_audio()

	response_string = transcribe_file(audio_file)

	display_message(response_string)


if __name__ == '__main__':
    main()
