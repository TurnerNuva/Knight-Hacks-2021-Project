# import jetson.inference
# import jetson.utils

# net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold = 0.5) # adj threshold for detection strength
# camera = jetson.utils.gstCamera(1280, 720, "/dev/video0")
# display = jetson.utils.glDisplay()

# while display.IsOpen():
# 	img, width, height = camera.CaptureRGBA()
# 	detections = net.Detect(img, width, height)
# 	display.RenderOnce(img, width, height)
# 	display.SetTitle("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))
	
# 	for detection in detections:
# 		class_name = net.GetClassDesc(detection.ClassID)
# 		print(f"Detected --> '{class_name}'")

def transcribe_file(speech_file):
    """Transcribe the given audio file."""
    from google.cloud import speech
    import io

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
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        print(u"Transcript: {}".format(result.alternatives[0].transcript))

def main():
    
    transcribe_file("listen_HumptyDumptySample4416.flac")


if __name__ == '__main__':
    main()


