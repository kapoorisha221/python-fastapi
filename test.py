import requests
speech_region = "eastus"
speech_key = "faeb05b5cbe2494297f3225efc3d3a71"
audio_file_path = "data\processed_data\Call 1.wav"


print("______________transcribe_function Called______________________-")
url = f"https://{speech_region}.tts.speech.microsoft.com/cognitiveservices/v1"
#url = "https://eastus.api.cognitive.microsoft.com/"
params = {
    "language": "en-US",
    "format": "detailed"
}
headers = {
    "Ocp-Apim-Subscription-Key": speech_key,
    "Content-Type": "audio/wav"
}

with open(audio_file_path, "rb") as audio_file:
    audio_data = audio_file.read()
try:
    response = requests.post(url, params=params, headers=headers, data=audio_data)
    response.raise_for_status()
    print("____________________________response___________________", response)
    print("____________________________________________",response.text)
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")


# if __name__ == "__main__()":
#     speech_region = "eastus"
#     speech_key = "faeb05b5cbe2494297f3225efc3d3a71"
#     audio_file_path = "data\processed_data\Call 1.wav"
#     transcribe_audio(speech_region, speech_key, audio_file_path)


# import requests

# url = f"https://{speech_region}.tts.speech.microsoft.com/cognitiveservices/v1"
# headers = {
#     "Ocp-Apim-Subscription-Key": speech_key,
#     "Content-Type": "audio/wav",
#     "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3",
#     "User-Agent": "curl"
# }
# #data = "<speak version='1.0' xml:lang='en-US'><voice xml:lang='en-US' xml:gender='Female' name='en-US-AvaMultilingualNeural'>my voice is my passport verify me</voice></speak>"
# response = requests.post(url, headers=headers, data=audio_data)
# with open("output.mp3", "wb") as f:
#     f.write(response.content)