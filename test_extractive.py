#################################### Extractive Summarization ####################################
import json, os, requests, time

# from azure.ai.textanalytics import TextAnalyticsClient, ExtractiveSummaryAction, AbstractiveSummaryAction 
# from azure.ai.textanalytics import TextAnalyticsClient
# from azure.ai.language.conversations import ConversationAnalysisClient
# from azure.core.credentials import AzureKeyCredential

from config.config import LocalConfig, AzureConfig
from logs.logger import get_Error_Logger, get_Info_Logger

class Summarization():
    info_logger = get_Info_Logger()
    error_logger = get_Error_Logger()
    cred = AzureConfig()
    def __init__(self):       
        self.with_diarisation_flag = False
        self.document = []
        self.text_to_append = ""

        ########################## REST ######################
        self.LANGUAGE_ENDPOINT = self.cred.LANGUAGE_ENDPOINT
        self.url = f"{self.LANGUAGE_ENDPOINT}/language/analyze-text/jobs?api-version=2023-04-01"
        self.key = self.cred.LANGUAGE_KEY
        self.api_version = "2023-04-01"
        self.transcription_jsonPath = r"data\audio_analytics\Call 1\transcript_output_english.json"
        self.text_to_summarise = None
        self.language = "en"
        #######################################################

        ###### CREDS #######
        self.endpoint = "https://proj-rnd-uae-et-language-001.cognitiveservices.azure.com/"
   


    def get_text(self):
        with open(self.transcription_jsonPath,'r',encoding='utf-8') as fp:
            transcriptions = json.load(fp)
        text_to_summarise = ""
        text_to_summarise_ls = []
        
        for item in transcriptions["transcript"]:
            text = ""
            if self.with_diarisation_flag:
                # text_to_summarise = text_to_summarise + item["speaker"] + ": " + item["dialogue"] + "\n"
                text_to_summarise =  item["speaker"] + ": " + item["dialogue"] 
            else:
            #    text_to_summarise = text_to_summarise +  item["dialogue"] + "\n" 
                text_to_summarise =  item["dialogue"] 
            text_to_summarise_ls.append(text_to_summarise)

        self.document = text_to_summarise_ls
        self.text_to_summarise = " ".join(text_to_summarise_ls)

    def get_extractive_summary(self, extractive_summary_response):
        status = False
        if extractive_summary_response["status"].lower() == "succeeded":
            extractive_summary = extractive_summary_response["tasks"]
            final_summary = ""
            for item in extractive_summary["items"][0]["results"]["documents"][0]["sentences"]:
                final_summary += item["text"]

            status = True
        else:
            errors = "".join(extractive_summary_response["errors"])

        if status:
            return {"status": "success", "summary": final_summary}
        else:
            return {"status": "fail", "error": errors}

    def extractive_summarisation_helper(self):
        self.get_text()
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
                            "kind": "ExtractiveSummarization",
                            "taskName": "Document Extractive Summarization Task 1",
                            "parameters": {
                                            "sentenceCount": 1
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
                print("response _____________________________________:", response1)
                extractive_summary_response = json.loads(extractive_summary_response.text)
                print("____________________________test result______________________:", extractive_summary_response)
                if extractive_summary_response["status"].lower() == "succeeded":
                    flag = False
                    result = self.get_extractive_summary(extractive_summary_response)
                    print("__________127_result__________________________", result)
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
    
