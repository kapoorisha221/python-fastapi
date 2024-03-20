from config.config import *
import os, time, logging
import azure.cognitiveservices.speech as speechsdk

class Stt(AzureConfig):

    def __init__(self, audio_path, language) -> None:
        super().__init__()
        
        # Audio path where audio is stored
        self.audio_path = audio_path
        
        # Setting host url according to language
        if language.lower() == "english":
            self.host_url = self.EN_US_HOST_URL
        elif language.lower() == "arabic":
            self.host_url = self.AR_AE_HOST_URL

        print("STT host url used : ",self.host_url)
            
        self.logger = logging.getLogger("ct-logger-stt")

    def recognize_once_from_file(self):
        try:
            # speechsdk config
            speech_config = speechsdk.SpeechConfig(host = self.host_url)

            # Audio config
            audio_config = speechsdk.audio.AudioConfig(filename= self.audio_path)

            self.logger.info("[INFO] audio and speech config successfully initisalised")
            
            #Setting up the speech recognizer object for speech recognition
            speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, 
            #auto_detect_source_language_config=auto_detect_source_language_config, 
            audio_config=audio_config)

            # Getting speechsdk result
            speech_recognition_result = speech_recognizer.recognize_once_async().get()

            if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
                #print("Recognized: {}".format(speech_recognition_result.text))
                return {"transcription": speech_recognition_result.text }
            
            # In case of errors
            elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
                print("No speechsdk could be recognized: {}".format(speech_recognition_result.no_match_details))
                return {"error": speech_recognition_result.no_match_details}
            
            elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speech_recognition_result.cancellation_details
                error = speech_recognition_result.cancellation_details
                print("speechsdk Recognition canceled: {}".format(cancellation_details.reason))
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    error = speechsdk.CancellationReason.Error
                    print("Error details: {}".format(cancellation_details.error_details))
                    print("Did you set the speechsdk resource key and region values?")

                return {"error": error}
        except Exception as e:
            print(f"Exception inside recognize_once_from_file() : {e}")
        
    def recognise_continuous_from_file(self):
        """Method for recognition of speech from a provided .wav file 
        """
        try:
            # List for storing recognised utterances from the audio
            ans=[]
            # audio config
            audio_config = speechsdk.AudioConfig(filename= self.audio_path)
            # speech config
            speech_config = speechsdk.SpeechConfig(host= self.host_url)
    
            # Setting up the speech recognizer object for speech recognition
            speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, 
            audio_config=audio_config)
            self.logger.info("[INFO] speech recogniser object successfully initisalised")
            # Calling the continuous recognition function to initiate speech recognition
            speech_recognizer.start_continuous_recognition()
            # Flag variable to stop the continuous recognition
            done=False
            
            def on_recognized(evt):
                """Method to extracting the text from speech recognizer object after continuous recognition ends
                """
                #assert (evt.result.reason==speechsdk.ResultReason.RecognizedSpeech),"A portion was not recognized."
                ans.append(evt.result.text)
                
            def stop_cb(evt):
                """Method to terminate the continuous recognition
                """
                speech_recognizer.stop_continuous_recognition()
                nonlocal done
                done=True

            def handle_errors(evt):
                if evt.result.reason == speechsdk.ResultReason.NoMatch:
                    error = evt.result.no_match_details
                    self.logger.info(f"[STT] no match : {str(error)}")
                elif evt.result.reason == speechsdk.ResultReason.Canceled:
                    cancellation_details = evt.result.cancellation_details
                    # print(cancellation_details)
                    if cancellation_details.reason == speechsdk.CancellationReason.Error:
                        error = speechsdk.CancellationReason.Error
                        print("Error details: {}".format(cancellation_details.error_details))
                        self.logger.info(f"[STT] no match : {cancellation_details.error_details}")
                        # print("Did you set the speechsdk resource key and region values?")

            # Signal for events that contains final recognition results, indicates successful recognition attempt  
            speech_recognizer.recognized.connect(on_recognized)

            speech_recognizer.canceled.connect(handle_errors)
            #speech_recognizer.canceled.connect(lambda evt: self.logger.info(f'CANCELED {evt.reult.reason}'))
            speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
            
            # stop continuous recognition on either session stopped or canceled events
            speech_recognizer.session_stopped.connect(stop_cb)
            speech_recognizer.canceled.connect(stop_cb)
            
            while not done:
                time.sleep(.5)

            # Getting whole transcription by combining all the recognised utterances from the audio file.
            res = " ".join([str(item) for item in ans])
            # Returning the transcription from audio
            return {"transcription":res}
        
        except Exception as e:
            print(f"Exception inside recognise_continuous_from_file() : {e}")
            self.logger.info(f"[STT-EXCEPTION] recognise_continuous_from_file() : {str(e)}")
            return  {"error": "Something went wrong. Please try again"}
        


