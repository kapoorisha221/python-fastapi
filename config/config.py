import os

class AzureConfig():
    def __init__(self) -> None:

        ####### CREDENTIALS #######
        self.LANGUAGE_KEY = "49ea02bc7cc644c49ec309ca849a3810"
        self.LANGUAGE_ENDPOINT = "https://tanzu.cognitiveservices.azure.com/"

        self.SPEECH_KEY = "a3357a8ce902473f830837e46d7e538c"
        self.SPEECH_ENDPOINT = "https://centralindia.api.cognitive.microsoft.com/"
        self.SPEECH_REGION = "centralindia"

        self.TRANSLATOR_KEY = "faeb05b5cbe2494297f3225efc3d3a71"
        self.TRANSLATOR_ENDPOINT = "https://api.cognitive.microsofttranslator.com/"
        

        #Audio File location
        self.audio_source = "source/calls"

        #Excel file location
        self.audio_data = "source/records/Accent Validation Data (1).xlsx"
        self.sheet1 = "Normal Calls"
        self.sheet2 = "Complaint "
        self.sheet3 = "Hitting the company "
        
        # STT
        self.STT_HOST_URL = "ws://127.0.0.1:<port>"
        # enter the port values
        # self.EN_US_PORT = "5000"  # original
        # self.AR_AE_PORT = "5001"   # original
        #####
        self.EN_US_PORT = "5070"
        self.EN_US_PORT = "5071" # testing acoustic
        self.AR_AE_PORT = "5060"
        
        #####
      
        # Host urls for using stt services in disconnected environment
        self.EN_US_HOST_URL = self.STT_HOST_URL.replace("<port>",self.EN_US_PORT)
        self.AR_AE_HOST_URL = self.STT_HOST_URL.replace("<port>",self.AR_AE_PORT)
        
        
        
        

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
        self.SOURCE_DATA = f"{self.PROJECT_PATH}/source/calls"
        self.DATA_FOLDER = f"{self.PROJECT_PATH}/data"
        self.RAW_DATA_FOLDER = f"{self.DATA_FOLDER}/raw_data"
        self.PROCESSED_DATA_FOLDER = f"{self.DATA_FOLDER}/processed_data"
       
        self.INFERENCE_FOLDER =  f"{self.DATA_FOLDER}/inference_data"
    

