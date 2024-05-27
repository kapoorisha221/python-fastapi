import requests, json
import random


class Sentiment():
    LANGUAGE_ENDPOINT = ""
    LANGUAGE_KEY = ""
    
    def __init__(self, transcripts):
        self.transcripts = transcripts
        self.transcriptions = self.transcripts["transcript"]
        self.LANGUAGE_ENDPOINT = self.LANGUAGE_ENDPOINT
        self.LANGUAGE_KEY = self.LANGUAGE_KEY

        self.words_sentiment_mapping_flag = False
        
    
    def send_request(self, dialogue):
        try:
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
            print(f"sentiment response status : {sentiment_response.status_code} ")
            return sentiment_response
        except Exception as e:
            print(f"An Error Occured ..{e}")
    
    def get_sentiment(self,sentiment_result):
        try:
            overall_sentiment = sentiment_result["results"]["documents"][0]["sentiment"]
            # print(f"overall sentiment : ", overall_sentiment)
            dic1 = sentiment_result["results"]["documents"][0]["confidenceScores"]
            max_sentiment = max(dic1, key=dic1.get)
            # print(f"sentiment : {max_sentiment}")
            return overall_sentiment, max_sentiment
        except Exception as e:
            # print(e)
            self.error_logger.error(msg="An Error Occured ..",exc_info=e,extra={"location":"sentiment_analysis.py - get_sentiment"})

    def get_words_sentiment_mapping(self, sentiment_result):
        try:
            words_sentiment_mapping = []
            for item in sentiment_result["results"]["documents"][0]["sentences"]:
                opinions  = item["targets"]
                print(len(opinions)) #depends on how many text-sentiment is predicted
                print(f"{opinions}\n\n")
                [words_sentiment_mapping.append(opinion["sentiment"], opinion["text"]) for opinion in opinions]
                # for opinion in opinions:
                #     sentiment = opinion["sentiment"]
                #     word = opinion["text"]
                #     pair = (word, sentiment)
                #     words_sentiment_mapping.append(pair)
            
            return words_sentiment_mapping
        except Exception as e:
            print(e)
            #self.error_logger.error(msg="An Error Occured ..",exc_info=e,extra={"location":"sentiment_analysis.py - get_words_sentiment_mapping"})
    
    def get_sentiment_analysis(self, sentiment_result):
        try:
            sentiment = self.get_sentiment(sentiment_result)[0]
            result = {"sentiment": sentiment}
            if self.words_sentiment_mapping_flag:
                print("______________calling get_words_sentiment_mapping function______________")
                mapping = self.get_words_sentiment_mapping(sentiment_result)
                result["words_sentiment_mapping"] = mapping
                if mapping:
                    target_words = [item[0] for item in mapping]
                    result["target_words"] = target_words
                else:
                    result["target_words"] = []
            
            return result
        except Exception as e:
            print(e)
                
    def sentiment_helper(self, dialogue):
        try:
            sentiment_response = self.send_request(dialogue)
            
            sentiment_result = json.loads(sentiment_response.text)
            print(f"sentiment_response : {sentiment_response.status_code}")
            print(sentiment_response.text)

            if sentiment_response.status_code == 401:
                return {"status": "fail", "error": sentiment_response.text}

            if sentiment_result["results"]["errors"]:
                error_msg =  f"status code : {sentiment_response.status_code}. Response : {sentiment_response.text}"
                print("___error_msg________", error_msg)
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
            print("________________________________________________________________________________")
            return result
        except Exception as e:
            print(e)
                
    def sentiment_pipeline(self):
        try:
            output = [[],[]]
            for item in self.transcriptions:
                result = self.sentiment_helper(item["dialogue"])
                if result["status"] == "success":
                    output.append(f"{item['dialogue']} : {result['sentiment']}")
                else:
                    sample_ls = ["positive", "negative", "neutral"]
                    ls = random.sample(sample_ls, 1)
                    output.append(ls[0])

            return output
        except Exception as e:
            print(e)
            




if __name__ == "__main__":
    transcript_path = "data/audio_analytics/Call 4/transcript_output_english.json"
    with open(transcript_path,'r',encoding='utf-8') as fp:
                transcripts = json.load(fp)

    obj = Sentiment(transcripts)
    result = obj.sentiment_pipeline()
    print("\n_______________result_______________________\n",result)