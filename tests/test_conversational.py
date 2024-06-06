import json, os, requests, time

from config.config import LocalConfig

class Summarization():
    def __init__(self):       
        self.with_diarisation_flag = False
        self.document = []
        self.text_to_append = ""

        ########################## REST ######################
        self.LANGUAGE_ENDPOINT = "https://demo-langservice-mij.cognitiveservices.azure.com/"
        self.url = f"{self.LANGUAGE_ENDPOINT}/language/analyze-text/jobs?api-version=2023-04-01"
        self.key = "42c994ec9e43430aacf6312a78f6c320"
        self.api_version = "2023-04-01"
        self.text_to_summarise = None
        self.language = "en"
        #######################################################

        ###### CREDS #######
        self.endpoint = "https://proj-rnd-uae-et-language-001.cognitiveservices.azure.com/"
        
    

#######################    Conversational Summarization      ############################################
    def get_conversational_text(self,transcription_jsonPath):
        try:
            print("opening conversational_input.json")
            with open(transcription_jsonPath,'r',encoding='utf-8') as fp:
                transcriptions = json.load(fp)

            text_to_summarise_ls = []
            for item in transcriptions:
                text_to_summarise_ls.append(item)

            print(F"appended and returned in a list successfully")
            return text_to_summarise_ls

        except Exception as e:
            print("An Error Occured ..")
    
    def conversational_summarisation_helper(self,audio_name,transcription_jsonPath):
        try:
            print(F"creating json for summarization desired input")
            json_path = create_conversatioanl_summ_input(audio_name,transcription_jsonPath)
            text_to_summarise_ls = self.get_conversational_text(json_path)
            print("___________text_to_summarise_ls__________", text_to_summarise_ls)
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

            print(F"Sending request for summarization")
            res = requests.post(url = url, headers= headers, json=data)
            print("res_________87__________", res)
            if res.status_code in  [202]:

                operation_location = res.headers["operation-location"]
                job_id = operation_location.split("/")[-1].split("?")[0]
                print(F"Extracted job id from the response '{job_id}'")
                
                url = f"{self.LANGUAGE_ENDPOINT}/language/analyze-conversations/jobs/{job_id}?api-version=2023-04-01"
                res = requests.post(url = url, headers= headers, json= data)        
                print("res_________96__________", res)
                start_time = time.time()
                max_time = 10
                passed_time = 0
                flag = True
                while flag and (passed_time < max_time):
                    print(F"calling get in loop for 10 min and passed time is {passed_time} min, to have summarization using jobid '{job_id}'")
                    conversatioanl_summary_response = requests.get(url = url, headers= headers)
                    conversatioanl_summary_response = json.loads(conversatioanl_summary_response.text)
                    print("______________conversational result_________", conversatioanl_summary_response)
                    if conversatioanl_summary_response["status"].lower() == "succeeded":
                        print(F"got the response successfully of conversation from the API,now will format it to desired format")
                        flag = False
                        result = self.get_conversational_summary(conversatioanl_summary_response)
                    else:
                        error_msg =  f"status code : {conversatioanl_summary_response.status_code}. Response : {conversatioanl_summary_response.text}"
                        result = {"status": "fail", "error":error_msg}
                        
                    end_time = time.time()
                    passed_time = end_time - start_time
                return result
            else:
                error_msg = res.text
                result = {"status": "fail", "error": error_msg}
                return result
        except Exception as e:
            print("An Error Occured ..")

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
                                print("formatting status is successfull")
                status = True               
            except Exception as e:
                errors = str(e)
                print(f"An Error Occured ..{errors}")
        else:
            errors = ", ".join(conversational_summary_response.get("errors", []))

        if status:
            return {"status": "success", "aspects_texts": aspects_texts}
        else:
            return {"status": "fail", "error": errors}



def create_conversatioanl_summ_input(audio_name,transcription_jsonpath):
    print("summ input called")
    with open(transcription_jsonpath, 'r', encoding='utf-8') as file:
        english_transcriptions = json.load(file)
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
    audio_name = "Call 2"
    transcription_jsonPath = "data/audio_analytics/Call 2/transcript_output_english.json"
    obj = Summarization()
    #print("instance created__")
    result = obj.conversational_summarisation_helper(audio_name, transcription_jsonPath)
    print(result)