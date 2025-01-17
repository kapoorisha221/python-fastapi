import os

class AzureConfig():
    def __init__(self) -> None:

        ####### LANGUAGE #######
        self.LANGUAGE_KEY = ""
        self.LANGUAGE_ENDPOINT = ""
        
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
        self.DATA_FOLDER = f"{self.PROJECT_PATH}/data"
        self.RAW_DATA_FOLDER = f"{self.DATA_FOLDER}/raw_data"
        self.PROCESSED_DATA_FOLDER = f"{self.DATA_FOLDER}/processed_data"
       
        self.INFERENCE_FOLDER =  f"{self.DATA_FOLDER}/inference_data"
    

