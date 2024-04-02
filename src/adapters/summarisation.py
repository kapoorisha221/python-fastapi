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

from config.config import LocalConfig

class Summarization():

    def __init__(self,  key, LANGUAGE_ENDPOINT):       
        self.with_diarisation_flag = False
        self.document = []
        self.text_to_append = ""

        ########################## REST ######################
        self.LANGUAGE_ENDPOINT = LANGUAGE_ENDPOINT
        self.url = f"{self.LANGUAGE_ENDPOINT}/language/analyze-text/jobs?api-version=2023-04-01"
        self.key = key
        self.api_version = "2023-04-01"
        # self.transcription_jsonPath = transcription_jsonPath
        self.text_to_summarise = None
        self.language = "en"
        #######################################################

        ###### CREDS #######
        self.endpoint = "https://proj-rnd-uae-et-language-001.cognitiveservices.azure.com/"
        

    # def get_text(self):
    #     # with open(self.transcription_jsonPath) as fp:
    #     #     transcriptions = json.load(fp)
    #     #text_to_summarise = ""
    #     text_to_summarise_ls = []
        
    #     # for item in transcriptions:
    #     #     text = ""
    #     #     if self.with_diarisation_flag:
    #     #         # text_to_summarise = text_to_summarise + item["speaker"] + ": " + item["dialogue"] + "\n"
    #     #         text =  item["speaker"] + ": " + item["dialogue"] 
    #     #     else:
    #     #     #    text_to_summarise = text_to_summarise +  item["dialogue"] + "\n" 
    #     #         text =  item["dialogue"] 
    #     #     text_to_summarise_ls.append(text)

    #     # self.document = text_to_summarise_ls
    #     # self.text_to_summarise = " ".join(text_to_summarise_ls)

    # def get_extractive_summary(self, extractive_summary_response):
    #     status = False
    #     if extractive_summary_response["status"].lower() == "succeeded":
    #         extractive_summary = extractive_summary_response["tasks"]
    #         final_summary = ""
    #         for item in extractive_summary["items"][0]["results"]["documents"][0]["sentences"]:
    #             final_summary += item["text"]

    #         status = True
    #     else:
    #         errors = "".join(extractive_summary_response["errors"])

    #     if status:
    #         return {"status": "success", "summary": final_summary}
    #     else:
    #         return {"status": "fail", "error": errors}

    # def extractive_summarisation_helper(self):
    #     self.get_text()
    #     if self.text_to_summarise == None:
    #         return {"status": "fail", "error": "no text to summarise"}

    #     data = {
    #         "displayName": "Document text Summarization Task Example",
    #         "analysisInput": {
    #             "documents": [
    #             {
    #                 "id": "1",
    #                 "language": "en",
    #                 "text": self.text_to_summarise
    #             }
    #             ]
    #         },
    #         "tasks": [
    #                     {
    #                         "kind": "ExtractiveSummarization",
    #                         "taskName": "Document Extractive Summarization Task 1",
    #                         "parameters": {
    #                                         "sentenceCount": 6
    #                                         }
    #                     }
    #                 ]
    #         }
    #     headers = {
    #                 "Content-Type": "application/json",
    #                 "Ocp-Apim-Subscription-Key": self.key
    #             }
        
    #     res = requests.post(url = self.url, headers= headers, json= data)
    #     # print(f"data : \n{data}\n")
    #     if res.status_code in  [202]:
    #         print(f"#1 : {res.text}")

    #         operation_location = res.headers["operation-location"]
    #         job_id = operation_location.split("/")[-1].split("?")[0]

    #         url = f"{self.LANGUAGE_ENDPOINT}/language/analyze-text/jobs/{job_id}?api-version=2023-04-01"

    #         start_time = time.time()
    #         max_time = 10
    #         passed_time = 0
    #         flag = True
    #         # result
    #         while flag and (passed_time < max_time):
    #             extractive_summary_response = requests.get(url = url, headers= headers)
    #             response1 = extractive_summary_response
    #             extractive_summary_response = json.loads(extractive_summary_response.text)
    #             if extractive_summary_response["status"].lower() == "succeeded":
    #                 flag = False
    #                 result = self.get_extractive_summary(extractive_summary_response)
    #             else:
    #                 error_msg =  f"status code : {response1.status_code}. Response : {response1.text}"
    #                 result = {"status": "fail", "error":error_msg}
                    
    #             end_time = time.time()
    #             passed_time = end_time - start_time

    #         return result
    #     else:
    #         error_msg = res.text
    #         result = {"status": "fail", "error": error_msg}
    #         return result



#######################    Under development      ############################################
    def get_conversational_text(self,transcription_jsonPath):
        # print("______________________________ get_conversational_text start____________________________________")
        with open(transcription_jsonPath,'r',encoding='utf-8') as fp:
            transcriptions = json.load(fp)

        text_to_summarise_ls = []
        for item in transcriptions:
            text_to_summarise_ls.append(item)

        # print("______________________________ get_conversational_text stop____________________________________",text_to_summarise_ls)
        return text_to_summarise_ls
    
    def conversational_summarisation_helper(self,audio_name,transcription_jsonPath):
        json_path = create_conversatioanl_summ_input(audio_name,transcription_jsonPath)
        # print("______________________ json_path_________________________",json_path)
        text_to_summarise_ls = self.get_conversational_text(json_path)
        if text_to_summarise_ls == None:
            return {"status": "fail", "error": "no text to summarise"}
        
        url = f"{self.LANGUAGE_ENDPOINT}/language/analyze-conversations/jobs?api-version={self.api_version}"
        headers = {
                "Content-Type": "application/json",
                "Ocp-Apim-Subscription-Key": self.key
                }
        data = {
            "displayName": "Conversation Task Example",
            "analysisInput": {
                "conversations": [{
                    "conversationItems": text_to_summarise_ls, 
                    "modality": "text",
                    "id": "conversation1",
                    "language": "en"
                }]
            },
            "tasks": [
                {
                    "taskName": "Conversation Task 1",
                    "kind": "ConversationalSummarizationTask",
                    "parameters": {
                        "summaryAspects": ["issue"]
                    }
                },
                {
                    "taskName": "Conversation Task 2",
                    "kind": "ConversationalSummarizationTask",
                    "parameters": {
                        "summaryAspects": ["resolution"],
                        "sentenceCount": 1
                    }
                }
            ]
        }
    
    
        # print("the data sent to the service is____________________: /n", text_to_summarise_ls)
        res = requests.post(url = url, headers= headers, json=data)
          
        if res.status_code in  [202]:
            # print(f"#1 : {res.text}")

            operation_location = res.headers["operation-location"]
            job_id = operation_location.split("/")[-1].split("?")[0]

            url = f"{self.LANGUAGE_ENDPOINT}/language/analyze-conversations/jobs/{job_id}?api-version=2023-04-01"
            res = requests.post(url = url, headers= headers, json= data)        
            
            start_time = time.time()
            max_time = 10
            passed_time = 0
            flag = True
            while flag and (passed_time < max_time):
                conversatioanl_summary_response = requests.get(url = url, headers= headers)
                conversatioanl_summary_response = json.loads(conversatioanl_summary_response.text)
                # print("response is______________:  ", conversatioanl_summary_response)
                if conversatioanl_summary_response["status"].lower() == "succeeded":
                    flag = False
                    result = self.get_conversational_summary(conversatioanl_summary_response)
                else:
                    error_msg =  f"status code : {conversatioanl_summary_response.status_code}. Response : {conversatioanl_summary_response.text}"
                    result = {"status": "fail", "error":error_msg}
                    
                end_time = time.time()
                passed_time = end_time - start_time
            # print("_______________ result ___________________________________",result)
            return result
        else:
            error_msg = res.text
            result = {"status": "fail", "error": error_msg}
            return result

    def get_conversational_summary(self,conversational_summary_response):
        status = False
        errors = ""
        aspects_texts = []
        if conversational_summary_response.get("status", "").lower() == "succeeded":
            try:
                tasks = conversational_summary_response["tasks"]["items"]
                for item in tasks:
                    conversations = item.get("results", {}).get("conversations", [])
                    for conversation in conversations:
                        summaries = conversation.get("summaries", [])
                        for summary in summaries:
                            aspect = summary.get("aspect")
                            text = summary.get("text")
                            if aspect is not None and text is not None:
                                aspects_texts.append({"aspect": aspect, "text": text})
                status = True
            except Exception as e:
                errors = str(e)
        else:
            errors = ", ".join(conversational_summary_response.get("errors", []))

        if status:
            # print("___________________ aspect ________________________",aspects_texts)
            return {"status": "success", "aspects_texts": aspects_texts}
        else:
            return {"status": "fail", "error": errors}


    

def create_conversatioanl_summ_input(audio_name,transcription_jsonpath):
    with open(transcription_jsonpath, 'r', encoding='utf-8') as file:
        english_transcriptions = json.load(file)
    # print("______________________________creating new____________________________________")
    output = []
    cnt =0
    for item in english_transcriptions["transcript"]:
        cnt +=1
        english_output = {}
        
        english_output["text"] = item["dialogue"]
        english_output["id"] = f"{cnt}"

        if item["speaker"] == "Agent":
            english_output["role"] = "Agent"
        else:
            english_output["role"] = "Customer"

        if item["speaker"] == "Agent":
            english_output["participantId"] = "Agent_1"
        else:
            english_output["participantId"] = "Customer_1"
        
        output.append(english_output)

    conversatioanl_summ_input_path = LocalConfig().DATA_FOLDER + f"/audio_analytics/{audio_name}/conversatioanl_summ_input.json"
    with open(conversatioanl_summ_input_path, 'w', encoding='utf-8') as eop:
        json.dump(output, eop, indent=4)
    return conversatioanl_summ_input_path

if __name__ == "__main__":
    # with open("analytics_output.json") as fp:
    #     data = json.load(fp)
        
        # self.LANGUAGE_ENDPOINT = "https://proj-rnd-uae-et-language-001.cognitiveservices.azure.com/"
        # self.url = f"{self.LANGUAGE_ENDPOINT}/language/analyze-text/jobs?api-version=2023-04-01"
        # self.key = "0b938542471248fda3aab56075a251c1"
        # self.text_to_summarise = None
        # self.language = "en"
    audio_name = "Call 5"
    transcription_jsonPath = r"C:\Users\AnshulBhardwaj\Desktop\Telecom EGYPT FASTAPI\data\audio_analytics\Call 5\transcript_output_english.json"
    key = "0b938542471248fda3aab56075a251c1"
    LANGUAGE_ENDPOINT = "https://proj-rnd-uae-et-language-001.cognitiveservices.azure.com/"
    
    obj = Summarization(transcription_jsonPath, key, LANGUAGE_ENDPOINT)
    result = obj.conversational_summarisation_helper(audio_name,transcription_jsonPath)
    print(f"RESULT: \n{result}")