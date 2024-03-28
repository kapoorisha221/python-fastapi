import json, os, requests, time
# from config import *

from azure.ai.textanalytics import (
    TextAnalyticsClient,
    ExtractiveSummaryAction,
    AbstractiveSummaryAction
) 
from azure.ai.textanalytics import TextAnalyticsClient
from azure.ai.language.conversations import ConversationAnalysisClient
from azure.core.credentials import AzureKeyCredential

class Summarization():

    def __init__(self, transcripts):
        self.transcripts = transcripts
        self.transcriptions = self.transcripts["transcript"]
        
        self.with_diarisation_flag = False
        self.document = []
        self.text_to_append = ""

        ########################## REST ######################
        self.LANGUAGE_ENDPOINT = "https://proj-rnd-uae-et-language-001.cognitiveservices.azure.com/"
        self.url = f"{self.LANGUAGE_ENDPOINT}/language/analyze-text/jobs?api-version=2023-04-01"
        self.key = "0b938542471248fda3aab56075a251c1"
        self.text_to_summarise = None
        self.language = "en"
        #######################################################

        ###### CREDS #######
        self.endpoint = "https://proj-rnd-uae-et-language-001.cognitiveservices.azure.com/"
        

    def get_text(self):

        #text_to_summarise = ""
        text_to_summarise_ls = []
        
        for item in self.transcriptions:
            text = ""
            if self.with_diarisation_flag:
                # text_to_summarise = text_to_summarise + item["speaker"] + ": " + item["dialogue"] + "\n"
                text =  item["speaker"] + ": " + item["dialogue"] 
            else:
            #    text_to_summarise = text_to_summarise +  item["dialogue"] + "\n" 
                text =  item["dialogue"] 
            text_to_summarise_ls.append(text)

        self.document = text_to_summarise_ls
        self.text_to_summarise = " ".join(text_to_summarise_ls)

    def get_extractive_summary(self, extractive_summary_response):
        status = False
        if extractive_summary_response["status"].lower() == "succeeded":
            print("@1")
            extractive_summary = extractive_summary_response["tasks"]
            final_summary = ""
            for item in extractive_summary["items"][0]["results"]["documents"][0]["sentences"]:
                final_summary += item["text"]

            # print(f"Final Summary : {final_summary}")
            status = True
        else:
            print("@2")
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
                                            "sentenceCount": 6
                                            }
                        }
                    ]
            }

        headers = {
                    "Content-Type": "application/json",
                    "Ocp-Apim-Subscription-Key": self.key
                }
        
        res = requests.post(url = self.url, headers= headers, json= data)
        # print(f"data : \n{data}\n")
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
                if extractive_summary_response["status"].lower() == "succeeded":
                    flag = False
                    result = self.get_extractive_summary(extractive_summary_response)
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



#######################    Under development      ############################################
    def get_conversational_text(transcription_jsonPath):
        with open(transcription_jsonPath) as fp:
            transcriptions = json.load(fp)

        text_to_summarise_ls = []
        for item in transcriptions['transcript']:
            text_to_summarise_ls.append(item)

        return text_to_summarise_ls
    
    def conversational_summarisation_helper(self,key, endpoint, transcription_jsonPath):
        text_to_summarise_ls = self.get_conversational_text(transcription_jsonPath)

        if self.text_to_summarise == None:
            return {"status": "fail", "error": "no text to summarise"}
        
        credential = AzureKeyCredential(key)
        client = ConversationAnalysisClient(endpoint, credential)
        #data parameters are needed to be fixed
        poller = client.begin_conversation_analysis(
            task={
                "displayName": "Analyze conversations from xxx",
                "analysisInput": {
                    "conversations": [
                        {
                            "conversationItems": text_to_summarise_ls,
                            "modality": "text",
                            "id": "conversation1",
                            "language": "en",
                        },
                    ]
                },
                "tasks": [
                    {
                        "taskName": "Issue task",
                        "kind": "ConversationalSummarizationTask",
                        "parameters": {"summaryAspects": ["issue"]},
                    },
                    {
                        "taskName": "Resolution task",
                        "kind": "ConversationalSummarizationTask",
                        "parameters": {"summaryAspects": ["resolution"]},
                    },
                ],
            }
        )

        # headers = {
        #             "Content-Type": "application/json",
        #             "Ocp-Apim-Subscription-Key": self.key
        #         }
        
        # res = poller.result()
        # if res.status_code in  [202]:
        #     print(f"#1 : {res.text}")

        #     operation_location = res.headers["operation-location"]
        #     job_id = operation_location.split("/")[-1].split("?")[0]

        #     url = f"{self.LANGUAGE_ENDPOINT}/language/analyze-text/jobs/{job_id}?api-version=2023-04-01"

        start_time = time.time()
        max_time = 10
        passed_time = 0
        flag = True
        # result
        while flag and (passed_time < max_time):
            conversational_summary_response = poller.result()
            response1 = conversational_summary_response
            extractive_summary_response = json.loads(extractive_summary_response.text)
            if extractive_summary_response["status"].lower() == "succeeded":
                flag = False
                result = self.get_extractive_summary(extractive_summary_response)
            else:
                error_msg =  f"status code : {response1.status_code}. Response : {response1.text}"
                result = {"status": "fail", "error":error_msg}
                
            end_time = time.time()
            passed_time = end_time - start_time

        return result
    # else:
    #     error_msg = res.text
    #     result = {"status": "fail", "error": error_msg}
    #     return result





    



if __name__ == "__main__":
    # with open(file= "./data/analytics/samplecopy_1.json", mode= "r") as fp:
    #     transcripts = json.load(fp= fp)
    #C:\Users\GagandeepSingh\Desktop\PROJ-EGYPT\PROJ-EGYPT\data\analytics\analytics_output.json
    with open("analytics_output.json") as fp:
        data = json.load(fp)

    transcripts = data["result_2"]["transcripts"]
    obj = Summarization(transcripts= transcripts)
    result = obj.extractive_summarisation_helper()
    print(f"RESULT: \n{result}")
    # print(f"\n\nTEXT: \n{obj.text_to_summarise}")
    # obj.sample_extractive_summarization()