import requests

class SpeechRecognizer:
    def __init__(self, speech_region, speech_key):
        self.speech_region = "eastus"
        self.speech_key = "103578cd1b1842c1bf0f10531fc13cfb"
        self.url = f"https://{self.speech_region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
    
    def recognize_speech(self, audio_file_path, language='en-US', format='detailed'):
        print("function called")
        params = {
            'language': "ar-EG",
            'format': "detailed"
        }

        headers = {
            "Ocp-Apim-Subscription-Key": self.speech_key,
            "Content-Type": "audio/wav"
        }

        with open(audio_file_path, 'rb') as audio_file:
            audio_data = audio_file.read()

        response = requests.post(self.url, params=params, headers=headers, data=audio_data)

        if response.status_code == 200:
            return response.json()  # Return the JSON response if the request was successful
        else:
            return {
                "error": response.status_code,
                "message": response.text
            }

# Example usage
if __name__ == "__main__":
    SPEECH_REGION = 'eastus'  # Replace with your actual speech region
    SPEECH_KEY = '103578cd1b1842c1bf0f10531fc13cfb'        # Replace with your actual subscription key
    audio_file_path = 'data/processed_data/Call 30.wav' # Path to your audio file

    recognizer = SpeechRecognizer(SPEECH_REGION, SPEECH_KEY)
    print("instance created ")
    result = recognizer.recognize_speech(audio_file_path)
    print(result)
