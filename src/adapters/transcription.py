import json
import os
import time
import azure.cognitiveservices.speech as speechsdk
from logs.logger import get_Error_Logger, get_Info_Logger
from config.config import AzureConfig

cred = AzureConfig()
info_logger = get_Info_Logger()
error_logger = get_Error_Logger()

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

                info_logger.info(msg=F"Got the transcription",extra={"location":"transcription.py - conversation_transcriber_transcribed_cb"})

            elif evt.result.reason == speechsdk.ResultReason.NoMatch:
                # print('\tNOMATCH: Speech could not be TRANSCRIBED: {}'.format(evt.result.no_match_details))
                error_logger.error(msg="An Error Occured ..",exc_info=e,extra={"location":"transcription.py - conversation_transcriber_transcribed_cb"})
        except Exception as e:
            error_logger.error(msg='NOMATCH: Speech could not be TRANSCRIBED: {}'.format(evt.result.no_match_details),exc_info=e,extra={"location":"transcription.py - conversation_transcriber_transcribed_cb"})

def recognize_from_file(audio_file_path,folder):
        try:
            print("___________________Connecting to Speech________")
            info_logger.info(msg=F"Initializing Creds for AI Speech Services ",extra={"location":"transcription.py - recognize_from_file"})
            transcript.clear()
            
            speech_config = speechsdk.SpeechConfig(host=cred.STT_HOST_URL + f"{cred.SPEECH_PORT}")
            speech_config.speech_recognition_language="ar-EG"

            audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
            print("___________________Connected to Speech________")
            conversation_transcriber = speechsdk.transcription.ConversationTranscriber(speech_config=speech_config, audio_config=audio_config)
            folder_path = folder
            transcribing_stop = False

            def stop_cb(evt: speechsdk.SessionEventArgs):
                json_transcript = json.dumps({"transcript":transcript}, indent=4, ensure_ascii=False)
                filename = os.path.join(folder_path, "transcript_output.json") 

                with open(filename, 'w', encoding='utf-8') as outfile:
                    outfile.write(json_transcript)
                    info_logger.info(msg=F"Saved Transcript.json at ' {filename}'")
                info_logger.info(msg=F"Stopping Session to AI Speech Service {evt}",extra={"location":"transcription.py - stop_cb"})
                # print('CLOSING on {}'.format(evt))
                nonlocal transcribing_stop
                transcribing_stop = True

            # Connect callbacks to the events fired by the conversation transcriber
            info_logger.info(msg=F"Connecting to the AI Speech Services and start Transcribing for audio'{audio_file_path}'",extra={"location":"transcription.py - recognize_from_file"})
            conversation_transcriber.transcribed.connect(conversation_transcriber_transcribed_cb)

            conversation_transcriber.session_stopped.connect(stop_cb)

            conversation_transcriber.start_transcribing_async()

            while not transcribing_stop:
                time.sleep(.5)

            conversation_transcriber.stop_transcribing_async()
        except Exception as e:
            error_logger.error(msg="An Error Occured ..",exc_info=e,extra={"location":"transcription.py - recognize_from_file"})