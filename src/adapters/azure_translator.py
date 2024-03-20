from config.config import AzureConfig
import requests
import random
import time 
import uuid
import traceback

class AzureTranslator(AzureConfig):
    def __init__(self, transcripts) -> None:
        super().__init__()
        self.transcripts = transcripts
        self.transcriptions = self.transcripts["transcript"]

    def get_translations(self, text, from_lang, to_lang):
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
    
    def get_translated_transcriptions_pipeline(self):
        output = []
        for item in self.transcriptions:
            result = self.get_translations(item["dialogue"])
            if result["status"] == "success":
                output.append(result["keyPhrases"])
            else:
                ## for testing pipeline
                sample_ls = ["key phrase1", "key phrase2", "key phrase3", "key phrase4", "key phrase5", "key phrase6","key phrase7"]
                ls = random.sample(sample_ls, 2)
                output.append(ls)

        return output
    
if __name__ == '__main__':
    azure_translator = AzureTranslator()

    text = "this is a test"
    from_lang = 'en'
    to_lang = 'ha'
    print(azure_translator.get_translations(text, from_lang, to_lang))