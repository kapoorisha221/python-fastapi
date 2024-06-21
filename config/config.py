import os

class AzureConfig():
    def __init__(self) -> None:
        
        ########### Container Credentials #######################
        self.LANGUAGE_KEY = "49ea02bc7cc644c49ec309ca849a3810"
        self.LANGUAGE_ENDPOINT = "https://tanzu.cognitiveservices.azure.com/"

        self.SPEECH_KEY = "a3357a8ce902473f830837e46d7e538c"
        self.SPEECH_ENDPOINT = "https://centralindia.api.cognitive.microsoft.com/"
        self.SPEECH_REGION = "centralindia"

        self.TRANSLATOR_KEY = "faeb05b5cbe2494297f3225efc3d3a71"
        self.TRANSLATOR_ENDPOINT = "https://api.cognitive.microsofttranslator.com/"

        #Audio File location
        self.audio_source = "source/calls"
        
        # STT
        self.STT_HOST_URL = "http://10.20.20.126:"
        self.SUMMARIZATION_URL = "http://10.20.20.125:"


        ##Connected Container Ports
        self.SUMMARIZATION_PORT = "5000"
        self.SPEECH_PORT = "5001"
        self.KEYPHRASE_PORT = "5002"
        self.SENTIMENT_PORT = "5003"
        self.TRANSLATOR_PORT = "5004"
        
        
        

class FileConfig():
    def __init__(self) -> None:
        # Sample rate
        self.ALLOWED_SAMPLE_RATES = [8000, 16000]
        self.DESIRED_SAMPLE_RATE = 16000
        # Subtype
        self.ALLOWED_SUBTYPES = ["PCM_16", "ULAW"]
        self.DESIRED_SUBTYPE = "PCM_16"
        # Wether to do denoising or not
        self.IS_DENOISING = False
        # Allowed languages
        self.ALLOWED_LANGUAGES = ["arabic", "english"]


class LocalConfig():
    def __init__(self) -> None:
        self.PROJECT_PATH = os.path.abspath('.')
        self.TRANSCRIPT_DATA = f"{self.PROJECT_PATH}/source/source_transcription"
        self.SOURCE_DATA = f"{self.PROJECT_PATH}/source/calls"
        self.DATA_FOLDER = f"{self.PROJECT_PATH}/data"
        self.RAW_DATA_FOLDER = f"{self.DATA_FOLDER}/raw_data"
        self.PROCESSED_DATA_FOLDER = f"{self.DATA_FOLDER}/processed_data"
       
        self.INFERENCE_FOLDER =  f"{self.DATA_FOLDER}/inference_data"

        #Excel file location
        #Excel file location
        self.audio_data = f"{self.PROJECT_PATH}/source/records/Accent Validation Data Updated.xlsx"
        self.sheet1 = "Normal Calls without escalation"
        self.sheet2 = "Escalated Calls"
        self.sheet3 = "Outages"
        self.sheet4 = "Hard Calls"
        self.sheet5 = "Hitting Calls"
        


        
        

    

