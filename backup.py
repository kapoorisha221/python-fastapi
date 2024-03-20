# MAIN.py

# def audios_validation(self, audio_path, language):
#         """Method for validating the provided audio input
#         Args:
#             audio_path (str): Audio path for the audio input provided by the user
#         Returns: 
#             dic: indicates wether the input audio has passed validation(s) or not through "result" & "validation_failed" keys
#         """
#         try:
#             # Check for allowed languages
#             if language not in FileConfig().ALLOWED_LANGUAGES:
#                 return {"validation_failed": "Unsupported language. Please proide audio in either english or arabic language."}
                
#             # Check audio file extension
#             extension = audio_path.split(".")[-1]
#             if extension != "wav":
#                 return {"validation_failed": "Validation failed. Uploaded audio file is not a wav file. Please upload the required audio file."}

#             try:
#                 # Read attributes of audio
#                 sf = SoundFile(audio_path)
#                 channels = sf.channels
#                 if channels != 1:
#                     return {"validation_failed": "Validation failed. Input audio does not have mono channel"}
                    
#             # Validation fails if corrupted audio file is provided as an input
#             except Exception as e:
#                 return {"validation_failed": "Error opening the audio file. Audio file is either corrupted or it's empty."}
            
#             # If all the validations gets passed
#             return {"result": True}
        
#         except Exception as e:
#             print(f"Exception inside stt_validation() : {e}")
#             do_logging(f"Exception inside stt_validation() : {str(e)}")

    
            
    
#     def audios_helper(self, audio_path, language):
#         """Method for transcribing the provided input audio.
#         Args:
#             audio_path (str): Audio provided by user for converting to text translation
#         Returns: 
#             dic: whether the speech is converted to text or not
#         """
#         try:
#             # Checks for validation(s) of provided audio input
#             res = self.audios_helper_validation(audio_path, language)
#             self.logger.info(f"[MAIN] stt validation result : {res}")
#             # Return error if any validation get's failed
#             if "validation_failed" in res.keys():
#                 return {"error": res["validation_failed"]}
            
#              # Creating object to handle  STT pre-processing
#             obj = SpeechPreprocessing(audio_path= audio_path)
#             # Path where the processed audio get's stored
#             output_path = obj.processing_main()
#             print(f"output_path : {output_path}")






#              # Creating object for doing STT using processed audio path
#             stt_obj = Stt(audio_path= output_path, language = language)  
#             # Getting transcription using continuous recognition from wav file
#             start_time = time.time()
#             result = stt_obj.recognise_continuous_from_file()
#             end_time = time.time()
#             print("#################################################################")
#             print(f"Total time to transcribe : {end_time - start_time} secs")
#             print("##################################################################")
#             # Returning the text transcription of the provided audio 
#             return result 
           
#         except Exception as e:
#             print(f"Exception inside stt_helper() : {e}")
#             self.logger.info(f"[MAIN-EXCEPTION-STT] stt_helper : {str(e)}")
           
#             return {"error": "Something went wrong. Please try again"}