import requests, json
import random

class keyPhrase():

    def __init__(self, transcripts):
        self.transcripts = transcripts
        self.transcriptions = self.transcripts["transcript"]
        self.LANGUAGE_ENDPOINT = "https://demo-langservice-mij.cognitiveservices.azure.com/"
        self.LANGUAGE_KEY = "42c994ec9e43430aacf6312a78f6c320"

    def send_request(self, text):

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
        response = requests.post(url= url, json= data, headers= headers)
        return response
    
    def keyPhrase_helper(self, text):
        response = self.send_request(text)
        # print(response.text, " \n", response.status_code)
        if response.status_code == 401:
            return {"status": "fail", "error": response.text}
        
        result = json.loads(response.text)
        # print("___________________________________ result ________________________",result)
        if result["results"]["errors"]:
            error_msg = str(result["results"]["errors"])
            output = {"status": "fail", "error": error_msg}
        else:
            # print("___________________________________ no error result ________________________",result["results"]["documents"])
            # if len(result["results"]["documents"][0]["keyPhrases"]) != 0:
            output = {"status": "success", 
                        "keyPhrases": result["results"]["documents"][0]["keyPhrases"]}

        return output

    def keyPhrase_pipeline(self):
        # list of list
        output = []
        for item in self.transcriptions:
            result = self.keyPhrase_helper(item["dialogue"])
            if result["status"] == "success":
                output.append(result["keyPhrases"])
            else:
                ## for testing pipeline
                sample_ls = ["key phrase1", "key phrase2", "key phrase3", "key phrase4", "key phrase5", "key phrase6","key phrase7"]
                ls = random.sample(sample_ls, 2)
                output.append(ls)

        return output

    




if __name__ == "__main__":
  
    obj = keyPhrase()
    text = "The food and service were unacceptable. The concierge was nice, however."
    result = obj.keyPhrase_helper(text= text)

