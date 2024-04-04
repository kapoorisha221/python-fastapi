import requests, json
import random
from config.config import AzureConfig
from logs.logger import get_Error_Logger, get_Info_Logger

class keyPhrase():
    cred = AzureConfig()
    def __init__(self, transcripts):
        self.transcripts = transcripts
        self.transcriptions = self.transcripts["transcript"]
        self.LANGUAGE_ENDPOINT = self.cred.LANGUAGE_ENDPOINT
        self.LANGUAGE_KEY = self.cred.LANGUAGE_KEY
        
    info_logger = get_Info_Logger()
    error_logger = get_Error_Logger()

    def send_request(self, text):
        try:

            headers = {
                        "Content-Type": "application/json",
                        "Ocp-Apim-Subscription-Key": self.LANGUAGE_KEY
                    }
            data = {
                "kind": "KeyPhraseExtraction",
                "parameters": {
                    "modelVersion": "latest"
                },
                "analysisInput":{
                    "documents":[
                        {
                            "id":"1",
                            "language":"en",
                            "text": text
                        }
                    ]
                }
            }
            url = f"{self.LANGUAGE_ENDPOINT}/language/:analyze-text?api-version=2022-05-01"
            self.info_logger.info(msg=F"Sending Post request to the API for keyPhrase",extra={"location":"KeyPhrase.py - send_request"})
            response = requests.post(url= url, json= data, headers= headers)
            return response
        except Exception as e:
            # print(e)
            self.error_logger.error(msg="An Error Occured ..",exc_info=e,extra={"location":"KeyPhrase.py - send_request"})

    
    def keyPhrase_helper(self, text):
        try:
            self.info_logger.info(msg=F"calling function to send request",extra={"location":"KeyPhrase.py - keyPhrase_helper"})
            response = self.send_request(text)
            # print(response.text, " \n", response.status_code)
            if response.status_code == 401:
                return {"status": "fail", "error": response.text}
            
            self.info_logger.info(msg=F"loading API response to json.",extra={"location":"KeyPhrase.py - keyPhrase_helper"})
            result = json.loads(response.text)
            # print("___________________________________ result ________________________",result)
            if result["results"]["errors"]:
                error_msg = str(result["results"]["errors"])
                output = {"status": "fail", "error": error_msg}
            else:
                # print("___________________________________ no error result ________________________",result["results"]["documents"])
                # if len(result["results"]["documents"][0]["keyPhrases"]) != 0:
                self.info_logger.info(msg=F"creating output format with the fetched keyphrases",extra={"location":"KeyPhrase.py - keyPhrase_helper"})
                output = {"status": "success", 
                            "keyPhrases": result["results"]["documents"][0]["keyPhrases"]}

            return output
        except Exception as e:
            # print(e)
            self.error_logger.error(msg="An Error Occured ..",exc_info=e,extra={"location":"KeyPhrase.py - keyPhrase_helper"})

    def keyPhrase_pipeline(self):
        try:
            # list of list
            output = []
            for item in self.transcriptions:
                self.info_logger.info(msg=F"calling keyphrase helper ",extra={"location":"KeyPhrase.py - keyPhrase_pipeline"})
                result = self.keyPhrase_helper(item["dialogue"])
                if result["status"] == "success":
                    self.info_logger.info(msg=F"appending result of keyphrase helper to the output",extra={"location":"KeyPhrase.py - keyPhrase_pipeline"})
                    output.append(result["keyPhrases"])
                else:
                    ## for testing pipeline
                    sample_ls = ["key phrase1", "key phrase2", "key phrase3", "key phrase4", "key phrase5", "key phrase6","key phrase7"]
                    ls = random.sample(sample_ls, 2)
                    output.append(ls)

            return output
        except Exception as e :
            # print(e)
            self.error_logger.error(msg="An Error Occured ..",exc_info=e,extra={"location":"KeyPhrase.py - keyPhrase_pipeline"})

    




if __name__ == "__main__":
  
    obj = keyPhrase()
    text = "The food and service were unacceptable. The concierge was nice, however."
    result = obj.keyPhrase_helper(text= text)