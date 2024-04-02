import requests, json
import random

class Sentiment():
    def __init__(self, transcripts):
        self.transcripts = transcripts
        self.transcriptions = self.transcripts["transcript"]
        self.LANGUAGE_ENDPOINT = "https://demo-langservice-mij.cognitiveservices.azure.com/"
        self.LANGUAGE_KEY = "42c994ec9e43430aacf6312a78f6c320"

        self.words_sentiment_mapping_flag = False
    
    def send_request(self, dialogue):
        data= {
                    "kind": "SentimentAnalysis",
                    "parameters": {
                        "modelVersion": "latest",
                        "opinionMining": "True"
                    },
                    "analysisInput":{
                        "documents":[
                            {
                                "id":"1",
                                "language":"en",
                                "text": dialogue
                            }
                        ]
                    }
                }

        url = f"{self.LANGUAGE_ENDPOINT}/language/:analyze-text?api-version=2023-04-15-preview"

        headers = {
                    "Content-Type": "application/json",
                    "Ocp-Apim-Subscription-Key": self.LANGUAGE_KEY
                }

        sentiment_response = requests.post(url= url, json=data, headers= headers)
        # print(f"sentiment response status : {sentiment_response.status_code} ")
        return sentiment_response
    
    def get_sentiment(self,sentiment_result):
        overall_sentiment = sentiment_result["results"]["documents"][0]["sentiment"]
        # print(f"overall sentiment : ", overall_sentiment)
        dic1 = sentiment_result["results"]["documents"][0]["confidenceScores"]
        max_sentiment = max(dic1, key=dic1.get)
        # print(f"sentiment : {max_sentiment}")
        return overall_sentiment, max_sentiment

    def get_words_sentiment_mapping(self, sentiment_result):
        words_sentiment_mapping = []
        for item in sentiment_result["results"]["documents"][0]["sentences"]:
            opinions  = item["targets"]
            # print(len(opinions)) #depends on how many text-sentiment is predicted
            # print(f"{opinions}\n\n")
            for opinion in opinions:
                sentiment = opinion["sentiment"]
                word = opinion["text"]
                pair = (word, sentiment)
                words_sentiment_mapping.append(pair)
        
        return words_sentiment_mapping
    
    def get_sentiment_analysis(self, sentiment_result):
        sentiment = self.get_sentiment(sentiment_result)[0]
        result = {"sentiment": sentiment}
        if self.words_sentiment_mapping_flag:
            mapping = self.get_words_sentiment_mapping(sentiment_result)
            result["words_sentiment_mapping"] = mapping
            if mapping:
                target_words = [item[0] for item in mapping]
                result["target_words"] = target_words
            else:
                result["target_words"] = []
        
        return result
    
    def sentiment_helper(self, dialouge):
        sentiment_response = self.send_request(dialogue= dialouge)
        
        sentiment_result = json.loads(sentiment_response.text)
        # print(f"sentiment_response : {sentiment_response.status_code}")
        # print(sentiment_response.text)

        if sentiment_response.status_code == 401:
            return {"status": "fail", "error": sentiment_response.text}

        if sentiment_result["results"]["errors"]:
            error_msg =  f"status code : {sentiment_response.status_code}. Response : {sentiment_response.text}"
            # Log entire error message
            # error_msg = "".join(sentiment_result["results"]["errors"])
            error_msg = ""
            for i in sentiment_result["results"]["errors"]:
                error_msg += i["error"]["message"]
                error_msg = error_msg + " #inner error# " +  i["error"]["innererror"]["message"]

            result = {"status": "fail", "error": error_msg}
        else:
            result = self.get_sentiment_analysis(sentiment_result)
            result["status"] = "success"

        return result
    
    def sentiment_pipeline(self):
        output = []
        for item in self.transcriptions:
            result = self.sentiment_helper(item["dialogue"])
            if result["status"] == "success":
                output.append(result["sentiment"])
            else:
                # print("____________________________________else sentiment ____________________")
                sample_ls = ["positive", "negative", "neutral"]
                ls = random.sample(sample_ls, 1)
                output.append(ls[0])

        return output




if __name__ == "__main__":
    obj = Sentiment()
    text = "The food and service were unacceptable. The concierge was nice, however."
    result = obj.sentiment_helper(dialouge= "Good morning vikram ji")
    # print("#################################################")
    # print(result)
    if result["status"] == "success":
        r = result["sentiment"]
        # print(f"sentiment : {r}")


