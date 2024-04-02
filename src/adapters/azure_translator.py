#from config.config import AzureConfig
import requests, json
import random
import time 
import uuid
import traceback

class AzureTranslator():
    def __init__(self) -> None:
        super().__init__()
        self.TRANS_KEY = "faeb05b5cbe2494297f3225efc3d3a71"
        self.SERVICE_REGION = "eastus"
        self.ENDPOINT = "https://api.cognitive.microsofttranslator.com/"
        

    def get_translations(self, text, from_lang, to_lang):
        print(f"_________________the values being passed in azure translator is:  \n text = {text}\n  from_lang = {from_lang} \n  to_lang = {to_lang}")
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
                print(f"Error: {e} retrying in {round(sleep_dur, 2)} seconds.")
                print(traceback.format_exc())
                time.sleep(sleep_dur)
                continue 
        return response
    
    def get_translated_transcriptions_pipeline(self, text,  from_lang, to_lang):
        output = []
        for item in self.transcriptions:
            result = self.get_translations(text, from_lang, to_lang)
            #if result["status"] == "success":
            if result:
                print("result got successfully")
                return output 
            else:
                print(f"Error in getting transcriptions for {item["dialogue"]} in audio file")
                return output
        return result
    
if __name__ == '__main__':
    transcripts_path = "data/audio_analytics/Call 1/translator_transcript_input.json"
    with open(transcripts_path, 'r', encoding='utf-8') as tph:
        transcripts = json.load(tph)
    azure_translator = AzureTranslator()
    text = "شكرا، ماشي، العفو أنا برضه هحاول أتابع لحضرتك ولو في أي حاجة هكلم حضرتك تاني، ماشي، شكرا العفو على إيه؟ تحت أمرك، أي استفسار تاني، شكرا العفو."
    from_lang = 'ar-EG'
    to_lang = 'en'
    print(azure_translator.get_translated_transcriptions_pipeline(text, from_lang, to_lang))