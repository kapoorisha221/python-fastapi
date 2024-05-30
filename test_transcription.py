import json
import os
import time
import azure.cognitiveservices.speech as speechsdk
from logs.logger import get_Error_Logger, get_Info_Logger
from config.config import AzureConfig


transcript = []
audio_file_path=""
folder_path=""

def conversation_transcriber_transcribed_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        try:
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                
                transcript.append({
                "dialogue": evt.result.text,
                "speaker": "Agent" if evt.result.speaker_id == "Guest-1" else "Customer",  # Assuming speaker ID 1 for Agent
                "duration_to_play": "{:.2f}".format(evt.result.offset/ (10**7)),  
                
                "locale": "ar-EG"
                })

                print("Got the transcription")

            elif evt.result.reason == speechsdk.ResultReason.NoMatch:
                # print('\tNOMATCH: Speech could not be TRANSCRIBED: {}'.format(evt.result.no_match_details))
                print(msg="An Error Occured ..",exc_info=e,extra={"location":"transcription.py - conversation_transcriber_transcribed_cb"})
        except Exception as e:
            print("NOMATCH: Speech could not be TRANSCRIBED: ")

def recognize_from_file(audio_file_path,folder):
        try:
            print("function called____________________")
            SPEECH_KEY = "103578cd1b1842c1bf0f10531fc13cfb"
            SPEECH_REGION = "eastus"
            print("Initializing Creds for AI Speech Services ")
            transcript.clear()
            
            speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
            speech_config.speech_recognition_language="ar-EG"

            audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
            conversation_transcriber = speechsdk.transcription.ConversationTranscriber(speech_config=speech_config, audio_config=audio_config)
            print("______________________________", conversation_transcriber)
            folder_path = folder
            transcribing_stop = False

            def stop_cb(evt: speechsdk.SessionEventArgs):
                json_transcript = json.dumps({"transcript":transcript}, indent=4, ensure_ascii=False)
                filename = os.path.join(folder_path, "transcript_output.json") 

                with open(filename, 'w', encoding='utf-8') as outfile:
                    outfile.write(json_transcript)
                    print("Saved Transcript.json at ' {filename}'")
                print("Stopping Session to AI Speech Service {evt}")
                # print('CLOSING on {}'.format(evt))
                nonlocal transcribing_stop
                transcribing_stop = True

            # Connect callbacks to the events fired by the conversation transcriber
            print("Connecting to the AI Speech Services and start Transcribing for audio'{audio_file_path}'")
            conversation_transcriber.transcribed.connect(conversation_transcriber_transcribed_cb)

            conversation_transcriber.session_stopped.connect(stop_cb)

            conversation_transcriber.start_transcribing_async()

            while not transcribing_stop:
                time.sleep(.5)

            conversation_transcriber.stop_transcribing_async()
        except Exception as e:
            print(f"An Error Occured ..{e}")



if __name__ == "__main __":
    file_path = "data/processed_data/Call 30.wav"
    folder = ""
    recognize_from_file(file_path, folder)