


import json
from src.adapters.keyPhrase import keyPhrase
from src.adapters.sentiment_analysis import Sentiment
from src.adapters.summarisation import Summarization
from src.adapters.translator import AzureTranslator
from logs.logger import *
from src.audio.audio import *
from config.config import *
from utils import *
from src.adapters.transcription import *

class Main():
    info_logger = get_Info_Logger()
    error_logger = get_Error_Logger()

# #################################### Pre Processing and transcripting ##################################################

    def add_to_mapping(self, audio_file_path): 
        try:
            self.info_logger.info(msg=F"Started function add_to_mapping to create mapping.json data",extra={"location":"main.py - add_to_mapping"})
            
            path = LocalConfig().DATA_FOLDER + "/" + "audios_info/mappings.json"
            with open(path) as fh:
                call_dict = json.load(fh)

            next_call_number = len(call_dict) + 1

            next_call_name = 'Call_{}'.format(next_call_number) + ".wav"

            audio_file = audio_file_path.split("/")[-1]

            call_dict[audio_file] = {"id" : next_call_name}

            audio_atrs = get_audio_attrs_for_report(audio_path= audio_file_path)
            call_dict[audio_file]["audio_duration"] = audio_atrs["audio_duration"]
            call_dict[audio_file]["audio_file_size"] = audio_atrs["audio_file_size"]

            with open(path, "w") as json_file:
                json.dump(call_dict, json_file, indent=4 )
            
            self.info_logger.info(msg=F"attributes added sucesfully to mapping.json for  '{audio_file}'",extra={"location":"main.py - add_to_mapping"})
        except Exception as e:
            self.error_logger.error(msg="An Error Occured ..",exc_info=e,extra={"location":"main.py - add_to_mapping"})


    def audios_main(self):
        try:
            """This function checks for all the files present inside RAW DATA folder and process & stores information for the
            audio files which are not present in PROCESSED data folder"""
            self.info_logger.info(msg="Sterted Processing from audios_main",extra={"location":"main.py-audios_main"})
            path = LocalConfig().RAW_DATA_FOLDER
            for audio_file in os.listdir(path):
                # checks
                file_to_check = audio_file
                if audio_file.endswith(".mp3"):
                    file_to_check = audio_file.replace(".mp3", ".wav")
                if is_file_present(folder_path= LocalConfig().PROCESSED_DATA_FOLDER, filename= file_to_check):
                    # print(f"check : {audio_file}")
                    self.info_logger.info(msg=F"file {file_to_check} already found",extra={"location":"main.py-audios_main"})
                    continue
                print(f"audio file: {audio_file}")
                extension = audio_file.split(".")[-1]
                filename = audio_file.split(".")[:-1][0]

                path1 = path + "/" + audio_file
                self.info_logger.info(msg=F"Calling get_audio_attributes",extra={"location":"main.py-audios_main"})
                attrs = get_audio_attributes(path= path1)
                # print(f"sample rate  {attrs.samplerate}")
                # print(f"subtype : {attrs.subtype}")
                # print(f"channels : {attrs.channels}")
        
                path2 = LocalConfig().PROCESSED_DATA_FOLDER + "/" + filename + ".wav"
                # processing
                audio_processing(input_path= path1, output_path= path2)
                # get & store informations 
                self.add_to_mapping(audio_file_path= path2)

                # make folders for the audios where corresponding analytics will get stored
                folder = LocalConfig().DATA_FOLDER + "/audio_analytics/" + filename
                os.makedirs(folder, exist_ok= True)
                self.info_logger.info(msg=F"Created folder for audio to save transcriptions at'{folder}'",extra={"location":"main.py-audios_main"})
                recognize_from_file(audio_file_path=path2,folder=folder)
                transcripted_json_file_path = folder + "/transcript_output.json"
                self.info_logger.info(msg=F"Calling Post Transcription for audio '{filename}' and file '{transcripted_json_file_path}'",extra={"location":"main.py-audios_main"})
                self.pipeline_after_transcription(audio_name=filename,transcription_jsonPath=transcripted_json_file_path)
        except Exception as e:
            # print(e)
            self.error_logger.error(msg="An Error Occured ..",exc_info=e,extra={"location":"main.py-audios_main"})






# #################################### Post Transcription Process ##################################################

    def get_kpis(self, audio_name, transcription_jsonPath):
        try:
            # additional to transcription
            result = {}
            with open(transcription_jsonPath, 'r', encoding='utf-8') as fp:
                transcriptions = json.load(fp)
                self.transcriptions = transcriptions
                
            key = "42c994ec9e43430aacf6312a78f6c320"
            LANGUAGE_ENDPOINT = "https://demo-langservice-mij.cognitiveservices.azure.com/"
            
            obj = Summarization(key, LANGUAGE_ENDPOINT)
            summarisation_result = obj.conversational_summarisation_helper(audio_name,transcription_jsonPath)
            print("_____________ summary ___________________________",summarisation_result["aspects_texts"])

            # summarisation_obj = Summarization(transcripts= transcriptions)
            # summarisation_result = summarisation_obj.extractive_summarisation_helper()

            if summarisation_result["status"] == "success":
                result["summary"] = summarisation_result["aspects_texts"]
            else:
                result["summary"] = None

            self.info_logger.info(msg=F"getting sentiments for the dialogue",extra={"location":"main.py - get_kpis"})
            sentiment_obj = Sentiment(transcripts= transcriptions)
            result["sentiment_ls"] = sentiment_obj.sentiment_pipeline()

            self.info_logger.info(msg=F"getting Keyphrases for the dialogue and conversation in list",extra={"location":"main.py - get_kpis"})
            keyPhrase_obj = keyPhrase(transcripts= transcriptions)
            keyPhrases = keyPhrase_obj.keyPhrase_pipeline()
            result["keyPhrases_ls"] = keyPhrases

            #audio_name = "sample_audio"
            self.file_path = f"data/audio_analytics/{audio_name}/"
        

            # save KPI's output
            with open(file= self.file_path + "kpi_output.json", mode= "w") as fh:
                json.dump(result, fp= fh, indent= 4)

            return result
        except Exception as e:
            print(e)
            self.error_logger.error(msg="An Error Occured ..",exc_info=e,extra={"location":"main.py - pipeline_after_transcription"})


    
    
    def pipeline_after_transcription(self, audio_name, transcription_jsonPath):

        try:
            translator_obj = AzureTranslator()
            self.info_logger.info(msg=F"Calling get_translated_transcriptions for '{transcription_jsonPath}'",extra={"location":"main.py - pipeline_after_transcription"})
            english_transcription_jsonpath = translator_obj.get_translated_transcriptions(audio_name, transcription_jsonPath)
            
            self.info_logger.info(msg=F"Calling get_kpis for '{english_transcription_jsonpath}'",extra={"location":"main.py - pipeline_after_transcription"})
            result = self.get_kpis(audio_name, english_transcription_jsonpath)

            # merge outputs
            merged_output = {}
            merged_output["result"] = {}

            merged_output["result"]["summary"] = result["summary"]
            unique_keyphrases = []
            for ls in result["keyPhrases_ls"]:
                if isinstance(ls, list):
                    for kp in ls:
                        unique_keyphrases.append(kp)
            unique_keyphrases = list(set(unique_keyphrases))
            merged_output["result"]["topics"] = unique_keyphrases

            print("____________ merged output____________",merged_output)
            # # with open(file_path + "wordcloud.png", 'rb') as image_file:
            # #     encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            # #     merged_output["result"]["wordcloud"] = encoded_image

            merged_output["result"]["wordcloud"] = get_text_count_from_keyphrases(result["keyPhrases_ls"])

            merged_output["result"]["transcripts"] = self.merge_sentiment_with_transcription(result["sentiment_ls"], 
                                                                                             self.transcriptions)
            
            merged_output["result"]["language"] = self.transcriptions["transcript"][0]["locale"].split("-")[0]

            with open(self.file_path + "merged_output.json", "w") as fh:
                json.dump(merged_output, fh, indent= 4)

            merged_output["result"]["transcripts"]  = self.merge_keyphrases_with_transcription(result["keyPhrases_ls"],
                                                                                               merged_output["result"]["transcripts"])
            print("____________ merged output____________",merged_output["result"]["transcripts"])
            with open(self.file_path + "power_bi_merged_output.json", "w") as fh:
                json.dump(merged_output, fh, indent= 4)

            
        except Exception as e:
            print(e)
            self.error_logger.error(msg="An Error Occured ..",exc_info=e,extra={"location":"main.py - pipeline_after_transcription"})


    def merge_sentiment_with_transcription(self, sentiment_ls, transcriptions):
        modified_transcriptions = []
        #iterating over list where each item is a dialouge
        for item, sentiment in zip(transcriptions["transcript"], sentiment_ls):
            res = item.copy()
            res["sentiment"] = sentiment
            modified_transcriptions.append(res)

        output = {"transcript": modified_transcriptions}
        return output
    
    
    def merge_keyphrases_with_transcription(self, keyPhrases_ls, transcriptions):
        modified_transcriptions = []
        for item, keyPhrases_ls in zip(transcriptions["transcript"], keyPhrases_ls):
            res = item.copy()
            res["keyPhrases"] = keyPhrases_ls
            modified_transcriptions.append(res)
        print("____________________ adding transcript with powerbi json _____________",modified_transcriptions)
        output = {"transcript": modified_transcriptions}
        return output


    