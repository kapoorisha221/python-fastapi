#from config.config import AzureConfig
import requests, json
import random
import time 
import uuid
import traceback

from config.config import LocalConfig
from logs.logger import get_Error_Logger, get_Info_Logger

class AzureTranslator():
    def __init__(self) -> None:
        super().__init__()
        self.TRANS_KEY = "faeb05b5cbe2494297f3225efc3d3a71"
        self.SERVICE_REGION = "eastus"
        self.ENDPOINT = "https://api.cognitive.microsofttranslator.com/"
        

    info_logger = get_Info_Logger()
    error_logger = get_Error_Logger()

    def get_translations(self, text, from_lang, to_lang):
        # print(f"_________________the values being passed in azure translator is:  \n text = {text}\n  from_lang = {from_lang} \n  to_lang = {to_lang}")
        response = "Translator service not working"
        for delay_secs in (3**x for x in range(0,3)):
            try:
                path = '/translate'
                constructed_url = self.ENDPOINT + path
                params = {
                    'api-version': '3.0',
                    'from': from_lang,
                    'to': [to_lang]
                }
                headers = {
                    'Ocp-Apim-Subscription-Key': self.TRANS_KEY,
                    'Ocp-Apim-Subscription-Region': self.SERVICE_REGION,
                    'Content-type': 'application/json',
                    'X-ClientTraceId': str(uuid.uuid4())
                }
                body = [
                    {
                        'text': f'{text}'
                    }
                ]
                request = requests.post(constructed_url, params=params, headers=headers, json=body)
                response = request.json()
                response = response[0]['translations'][0]['text']
                break
            except Exception as e:
                randomness_collision_avoidance = random.randint(0, 1000) / 1000.0
                sleep_dur = delay_secs + randomness_collision_avoidance
                # print(f"Error: {e} retrying in {round(sleep_dur, 2)} seconds.")
                # print(traceback.format_exc())
                time.sleep(sleep_dur)
                continue 
        return response
    
    def get_translated_transcriptions_pipeline(self, text,  from_lang, to_lang):
        # for item in self.transcriptions:
        result = self.get_translations(text, from_lang, to_lang)
            #if result["status"] == "success":
            # if result:
            #     print("result got successfully")
            #     return output 
            # else:
            #     print(f"Error in getting transcriptions for {item['dialogue']} in audio file")
            #     return output
        return result
    




    def get_translated_transcriptions(self,audio_name, transcription_jsonPath):
        try:
            with open(transcription_jsonPath, 'r', encoding='utf-8') as file:
                original_transcript_data = json.load(file)
            
            transcript_output_english = {'transcript': []}

            # translator_obj = AzureTranslator()
            self.info_logger.info(msg=F"Starting to Iterate over the dialogue to translate of '{transcription_jsonPath}'",extra={"location":"translator.py - get_translated_transcriptions"})
            for dialogue_info in original_transcript_data['transcript']:
                if dialogue_info['locale'] != 'en':
                    translated_dialogue = self.get_translations(text=dialogue_info['dialogue'], from_lang=dialogue_info['locale'], to_lang="en")
                    transcript_output_english['transcript'].append({
                        'dialogue': translated_dialogue,
                        'speaker': dialogue_info['speaker'],
                        'duration_to_play': dialogue_info['duration_to_play'],
                        'locale': 'en' 
                    })
                    # print(f"\n the response from translator is: {translated_dialogue}\n")
                    self.info_logger.info(msg=F"the response from translator is: {translated_dialogue}",extra={"location":"translator.py - get_translated_transcriptions"})
                else:
                    # Dialogue is already in English, append it directly
                    transcript_output_english['transcript'].append(dialogue_info)
            
            self.english_transcript_output_path = LocalConfig().DATA_FOLDER + f"/audio_analytics/{audio_name}/"

            with open(self.english_transcript_output_path +'transcript_output_english.json','w', encoding='utf-8') as file:
                json.dump(transcript_output_english, file, indent=4)

            # print("________the modified json is created___________") #???????????
            english_transcription_jsonpath = self.english_transcript_output_path +'transcript_output_english.json'
            self.info_logger.info(msg=F"saved translated output to transcript_output_english.json at locaton '{english_transcription_jsonpath}'",extra={"location":"translator.py - get_translated_transcriptions"})
            return english_transcription_jsonpath
        except Exception as e:
            print(e)
            self.error_logger.error(msg="An Error Occured ..",exc_info=e,extra={"location":"main.py - get_translated_transcriptions"})


    
if __name__ == '__main__':
    transcripts_path = "data/audio_analytics/Call 1/translator_transcript_input.json"
    with open(transcripts_path, 'r', encoding='utf-8') as tph:
        transcripts = json.load(tph)
    azure_translator = AzureTranslator()
    text = "شكرا، ماشي، العفو أنا برضه هحاول أتابع لحضرتك ولو في أي حاجة هكلم حضرتك تاني، ماشي، شكرا العفو على إيه؟ تحت أمرك، أي استفسار تاني، شكرا العفو."
    from_lang = 'ar-EG'
    to_lang = 'en'
    print(azure_translator.get_translated_transcriptions_pipeline(text, from_lang, to_lang))