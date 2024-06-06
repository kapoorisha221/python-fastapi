import json
import os
import time
import azure.cognitiveservices.speech as speechsdk
from logs.logger import get_Error_Logger, get_Info_Logger
from config.config import AzureConfig

class AzureSpeechTranscriber:
    def __init__(self, speech_key, speech_region, language="ar-EG"):
        self.speech_key = speech_key
        self.speech_region = speech_region
        self.language = language
        self.transcript = []
        self.transcribing_stop = False

        # Initialize loggers
        self.error_logger = get_Error_Logger()
        self.info_logger = get_Info_Logger()

    def conversation_transcriber_transcribed_cb(self, evt: speechsdk.SpeechRecognitionEventArgs):
        try:
            print("___________________", evt.result)
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                self.transcript.append({
                    "dialogue": evt.result.text,
                    "speaker": "Agent" if evt.result.speaker_id == "Guest-1" else "Customer",  # Assuming speaker ID 1 for Agent
                    "duration_to_play": "{:.2f}".format(evt.result.offset / (10**7)),
                    "locale": self.language
                })
                self.info_logger.info("Got the transcription")
            elif evt.result.reason == speechsdk.ResultReason.NoMatch:
                self.error_logger.error("NoMatch: Speech could not be transcribed", exc_info=True)
        except Exception as e:
            self.error_logger.error("Error in transcription callback", exc_info=True)

    def stop_cb(self, evt: speechsdk.SessionEventArgs, folder_path):
        json_transcript = json.dumps({"transcript": self.transcript}, indent=4, ensure_ascii=False)
        filename = os.path.join(folder_path, "transcript_output.json")
        
        with open(filename, 'w', encoding='utf-8') as outfile:
            outfile.write(json_transcript)
        print(f"Saved transcript.json at '{filename}'")
        self.info_logger.info(f"Stopping session: {evt}")
        self.transcribing_stop = True

    def recognize_from_file(self, audio_file_path, folder_path):
        try:
            print("Function called")
            self.transcript.clear()
            
            print("Initializing credentials for AI Speech Services")
            speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.speech_region)
            speech_config.speech_recognition_language = self.language

            audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
            conversation_transcriber = speechsdk.transcription.ConversationTranscriber(speech_config=speech_config, audio_config=audio_config)
            print(f"ConversationTranscriber initialized: {conversation_transcriber}")

            conversation_transcriber.transcribed.connect(self.conversation_transcriber_transcribed_cb)
            conversation_transcriber.session_stopped.connect(lambda evt: self.stop_cb(evt, folder_path))

            print(f"Connecting to AI Speech Services and starting transcription for audio '{audio_file_path}'")
            conversation_transcriber.start_transcribing_async()

            while not self.transcribing_stop:
                time.sleep(0.5)

            conversation_transcriber.stop_transcribing_async()
        except Exception as e:
            self.error_logger.error(f"An error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    SPEECH_KEY = "103578cd1b1842c1bf0f10531fc13cfb"  # Replace with your actual speech key
    SPEECH_REGION = "eastus"  # Replace with your actual speech region
    audio_file_path = "data/processed_data/Call 30.wav"
    folder_path = "data/processed_data"  # Replace with your actual output folder

    transcriber = AzureSpeechTranscriber(SPEECH_KEY, SPEECH_REGION)
    transcriber.recognize_from_file(audio_file_path, folder_path)
