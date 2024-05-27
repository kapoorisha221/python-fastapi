#################################### Extractive Summarization ####################################
import json, os, requests, time

class Summarization():
    def __init__(self):       
        self.with_diarisation_flag = False
        self.document = []
        self.text_to_append = ""

        ########################## REST ######################
        self.LANGUAGE_ENDPOINT = self.LANGUAGE_ENDPOINT
        self.url = f"{self.LANGUAGE_ENDPOINT}/language/analyze-text/jobs?api-version=2023-04-01"
        self.key = self.LANGUAGE_KEY
        self.api_version = "2023-04-01"
        self.language = "en"
        #######################################################

        ###### CREDS #######
        self.endpoint = "https://proj-rnd-uae-et-language-001.cognitiveservices.azure.com/"
   


    def get_text(self, call):
        transcription_jsonPath =  f"data/audio_analytics/{call}/transcript_output_english.json"
        with open(transcription_jsonPath,'r',encoding='utf-8') as fp:
            transcriptions = json.load(fp)
        text_to_summarise = ""
        text_to_summarise_ls = []
        
        for item in transcriptions["transcript"]:
            if self.with_diarisation_flag:
                # text_to_summarise = text_to_summarise + item["speaker"] + ": " + item["dialogue"] + "\n"
                text_to_summarise =  item["speaker"] + ": " + item["dialogue"] 
            else:
            #    text_to_summarise = text_to_summarise +  item["dialogue"] + "\n" 
                text_to_summarise =  item["dialogue"] 
            text_to_summarise_ls.append(text_to_summarise)

        self.document = text_to_summarise_ls
        self.text_to_summarise = " ".join(text_to_summarise_ls)

    def get_abstractive_summary(self, extractive_summary_response):
        status = False
        if extractive_summary_response["status"].lower() == "succeeded":
            extractive_summary = extractive_summary_response["tasks"]
            final_summary = ""
            for item in extractive_summary["items"][0]["results"]["documents"][0]["summaries"]:
                final_summary += item["text"]

            status = True
        else:
            errors = "".join(extractive_summary_response["errors"])

        if status:
            return {"status": "success", "summary": final_summary}
        else:
            return {"status": "fail", "error": errors}

    def abstractive_summarisation_helper(self, call):
        self.get_text(call)
        if self.text_to_summarise == None:
            return {"status": "fail", "error": "no text to summarise"}

        data = {
            "displayName": "Document text Summarization Task Example",
            "analysisInput": {
                "documents": [
                {
                    "id": "1",
                    "language": "en",
                    "text": self.text_to_summarise
                }
                ]
            },
            "tasks": [
                        {
                            "kind": "AbstractiveSummarization",
                            "taskName": "Text Abstractive Summarization Task 1",
                            "parameters": {
                                            "summaryLength": "short"
                                            }
                        }
                    ]
            }
        headers = {
                    "Content-Type": "application/json",
                    "Ocp-Apim-Subscription-Key": self.key
                }
        
        res = requests.post(url = self.url, headers= headers, json= data)
        print(f"data : \n{data}\n")
        if res.status_code in  [202]:
            print(f"#1 : {res.text}")

            operation_location = res.headers["operation-location"]
            job_id = operation_location.split("/")[-1].split("?")[0]

            url = f"{self.LANGUAGE_ENDPOINT}/language/analyze-text/jobs/{job_id}?api-version=2023-04-01"

            start_time = time.time()
            max_time = 10
            passed_time = 0
            flag = True
            # result
            while flag and (passed_time < max_time):
                extractive_summary_response = requests.get(url = url, headers= headers)
                response1 = extractive_summary_response
                extractive_summary_response = json.loads(extractive_summary_response.text)
                print("____________________________test result______________________:", extractive_summary_response)
                if extractive_summary_response["status"].lower() == "succeeded":
                    flag = False
                    result = self.get_abstractive_summary(extractive_summary_response)
                    print("_________________result__________________________", result)
                else:
                    error_msg =  f"status code : {response1.status_code}. Response : {response1.text}"
                    result = {"status": "fail", "error":error_msg}
                    
                end_time = time.time()
                passed_time = end_time - start_time

            return result
        else:
            error_msg = res.text
            result = {"status": "fail", "error": error_msg}
            return result
    
if __name__ == "__main__":
    call = "Call 27"

    obj = Summarization()
    res= obj.abstractive_summarisation_helper(call)
    print(res)

