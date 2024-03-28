from src.audio.preprocessing import SpeechPreprocessing
from stt import Stt
from utils import *
from soundfile import SoundFile
import logging, time, traceback, base64
from datetime import datetime 

from src.adapters.keyPhrase import keyPhrase
from src.adapters.sentiment_analysis import Sentiment
from src.adapters.summarisation import Summarization
from src.adapters.azure_translator import AzureTranslator

from src.audio.audio import *

from config.config import *

import pandas as pd
import uuid

class Main():

    def __init__(self) -> None:
        self.logger = logging.getLogger("ct-logger-main")
        # transcriptions for a call (e.g. call_1.wav)
        self.transcriptions = None
        # path where all the analytics will be stored for a call (e.g call_1.wav)
        self.file_path = None

    
    ################################  Audio Processing Part :)  #############################################
    def add_to_mapping(self, audio_file_path): 
        
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
        #______________________________new parameters to add 

        with open(path, "w") as json_file:
            json.dump(call_dict, json_file, indent=4 )
      
    def audios_main(self):
        """This function checks for all the files present inside RAW DATA folder and process & stores information for the
        audio files which are not present in PROCESSED data folder"""

        path = LocalConfig().RAW_DATA_FOLDER
        for audio_file in os.listdir(path):
            # checks
            file_to_check = audio_file
            if audio_file.endswith(".mp3"):
                file_to_check = audio_file.replace(".mp3", ".wav")
            if is_file_present(folder_path= LocalConfig().PROCESSED_DATA_FOLDER, filename= file_to_check):
                print(f"check : {audio_file}")
                continue
            print(f"audio file: {audio_file}")
            extension = audio_file.split(".")[-1]
            filename = audio_file.split(".")[:-1][0]

            path1 = path + "/" + audio_file

            attrs = get_audio_attributes(path= path1)
            print(f"sample rate  {attrs.samplerate}")
            print(f"subtype : {attrs.subtype}")
            print(f"channels : {attrs.channels}")

            path2 = LocalConfig().PROCESSED_DATA_FOLDER + "/" + filename + ".wav"
            
            # if extension == "mp3":
            #     # convert to wav
            #     mp3_to_wav(mp3_file= path1, wav_file= path2)

            # processing
            audio_processing(input_path= path1, output_path= path2)
             # get & store informations 
            self.add_to_mapping(audio_file_path= path2)

            # make folders for the audios where corresponding analytics will get stored
            folder = LocalConfig().DATA_FOLDER + "/audio_analytics/" + filename
            os.makedirs(folder, exist_ok= True)

        
################################## POST Transcription ##################################################
            
    def get_kpis(self, audio_name, transcription_jsonPath):
        # additional to transcription
        result = {}
        with open(transcription_jsonPath) as fp:
            transcriptions = json.load(fp)
            self.transcriptions = transcriptions

        summarisation_obj = Summarization(transcripts= transcriptions)
        summarisation_result = summarisation_obj.extractive_summarisation_helper()

        if summarisation_result["status"] == "success":
            result["summary"] = summarisation_result["summary"]
        else:
            result["summary"] = None

        sentiment_obj = Sentiment(transcripts= transcriptions)
        result["sentiment_ls"] = sentiment_obj.sentiment_pipeline()

        keyPhrase_obj = keyPhrase(transcripts= transcriptions)
        keyPhrases = keyPhrase_obj.keyPhrase_pipeline()
        result["keyPhrases_ls"] = keyPhrases

        #audio_name = "sample_audio"
        self.file_path = f"data/audio_analytics/{audio_name}/"
    

        # save KPI's output
        with open(file= self.file_path + "kpi_output.json", mode= "w") as fh:
            json.dump(result, fp= fh, indent= 4)

        return result

    def get_translated_transcriptions(self, audio_name, transcription_jsonPath):
        # Load the original transcript JSON file
        with open(transcription_jsonPath, 'r', encoding='utf-8') as file:
            original_transcript_data = json.load(file)

        transcript_output_english = {'transcript': [], 'audio_id': original_transcript_data['audio_id']}

        ## Translator ###
        translator_obj = AzureTranslator()

        #transcript_language = transcription_language_checker(transcription_jsonPath)
        
        for dialogue_info in original_transcript_data['transcript']:
            if dialogue_info['locale'] != 'en':
                print("\n____________________________________the locale value is not english________________________________________________\n")
                translated_dialogue = translator_obj.get_translations(dialogue_info['dialogue'], dialogue_info['locale'], 'en')
                # transcript_output_english['transcript'].append({
                #     'dialogue': translated_dialogue,
                #     'speaker': dialogue_info['speaker'],
                #     'duration_to_play': dialogue_info['duration_to_play'],
                #     'locale': 'en'
                # })
                print(f"\n the response from translator is: {translated_dialogue}\n")
                transcript_output_english['transcript'].append(dialogue_info)
            else:
                # Dialogue is already in English, append it directly
                transcript_output_english['transcript'].append(dialogue_info)
        
        #audio_name = "sample_audio"
        self.english_transcript_output_path = f"data/audio_analytics/{audio_name}/"
       
        with open(self.english_transcript_output_path +'transcript_output_english.json','w', encoding='utf-8') as file:
            json.dump(transcript_output_english, file, indent=4)

        print("________the modified excel is created___________")

        english_transcription_jsonpath = self.english_transcript_output_path +'transcript_output_english.json'
        return english_transcription_jsonpath
        

    def pipeline_after_transcription(self, audio_name, transcription_jsonPath):
        
        english_transcription_jsonpath = self.get_translated_transcriptions(audio_name, transcription_jsonPath)
        # translator_result = self.get_translated_transcriptions_pipeline()
        # additional to transcription
        # result = {}
        result = self.get_kpis(audio_name, english_transcription_jsonpath)
        
        # save wordcloud
        # text = get_text_from_keyphrases(result["keyPhrases_ls"])
        # # print(f"keyphrases text : \n", text)
        # save_wordcloud(text= text, language= "en", file= file_path + "wordcloud.png")

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

        # with open(file_path + "wordcloud.png", 'rb') as image_file:
        #     encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        #     merged_output["result"]["wordcloud"] = encoded_image

        merged_output["result"]["wordcloud"] = get_text_count_from_keyphrases(result["keyPhrases_ls"])

        merged_output["result"]["transcripts"] = self.merge_sentiment_with_transcription(result["sentiment_ls"], 
                                                                                         self.transcriptions)
        
        merged_output["result"]["language"] = self.transcriptions["transcript"][0]["locale"].split("-")[0]

        with open(self.file_path + "merged_output.json", "w") as fh:
            json.dump(merged_output, fh, indent= 4)

        merged_output["result"]["transcripts"]  = self.merge_keyphrases_with_transcription(result["keyPhrases_ls"],
                                                                                           merged_output["result"]["transcripts"])

        with open(self.file_path + "power_bi_merged_output.json", "w") as fh:
            json.dump(merged_output, fh, indent= 4)

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
        # print("###############################################")
        # print(f"transcripts : \n{transcriptions}")
        #iterating over list where each item is a dialouge
        for item, keyPhrases_ls in zip(transcriptions["transcript"], keyPhrases_ls):
            res = item.copy()
            res["keyPhrases"] = keyPhrases_ls
            modified_transcriptions.append(res)
        output = {"transcript": modified_transcriptions}
        return output
    
####################################### POWER BI ##############################
    def powerbi_report_keyword(self, jsonPath):
        with open(jsonPath) as fp:
            information = json.load(fp)
            
        duration_ls, dialouges_ls, keywords_ls, sentiment_ls =  [],[], [],[]

        for dialouge in information["result"]["transcripts"]["transcript"]:
            print(f"dialouge :\n {dialouge}")
            if dialouge["keyPhrases"]:
               
                for kp in dialouge["keyPhrases"]:
                  
                    duration_ls.append(dialouge["duration_to_play"])
                    dialouges_ls.append(dialouge["dialogue"])
                    keywords_ls.append(kp)
                    sentiment_ls.append(dialouge["sentiment"])
            else:
                duration_ls.append(dialouge["duration_to_play"])
                dialouges_ls.append(None)
                keywords_ls.append(None)
                sentiment_ls.append(None)

        # final result for an audio
        dic_pandas = {"duration": duration_ls, "keywords": keywords_ls, 
                      "sentiment": sentiment_ls, "dialouge": dialouges_ls}
        df = pd.DataFrame(dic_pandas)
        df.to_excel("PowerBi_1.xlsx")

    def power_bi_report_main_helper(self, audio_file, merged_output_jsonPath = "data/audio_analytics/sample_audio/merged_output.json" ):
        # Use merged_output.json & audios_info/mappings.json
      
        with open(merged_output_jsonPath) as fh:
            data1 = json.load(fh)
        if data1.values() != 0:
            print("any value is picked")

        sentiment_mapping = {"positive": 1, "negative": -1, "neutral": 0}
        overall_sentiment = 0
        language = ""
        call_opening_sentiment = 0
        call_opening_count = 0
        call_closing_sentiment = 0

        transcriptions = data1['result']['transcripts']['transcript']

        locale = transcriptions[0]["locale"]
        if "en" in locale:
            language = "english"
        elif "ar" in locale:
            language = "arabic"
        elif "hi" in locale:
            language = "hindi"

        
        for dialogue in transcriptions:
            overall_sentiment += sentiment_mapping[dialogue["sentiment"]]
            if (dialogue["speaker"].lower() == "agent"):
                call_opening_count += 1
                call_opening_sentiment += sentiment_mapping[dialogue["sentiment"]]
            else:
                break

        call_opening_sentiment= max(0, call_opening_sentiment)
        call_opening_score = call_opening_sentiment/call_opening_count

        reverse_transcriptions = transcriptions[::-1]
        # removing customer last interactions
        agent_part_start_index = -1
        for index, dialogue in enumerate(reverse_transcriptions):
            if (dialogue["speaker"].lower() == "agent"):
                agent_part_start_index = index
                break
                
        reverse_transcriptions = reverse_transcriptions[agent_part_start_index:]


        call_closing_count = 0
        call_closing_sentiment = 0
        for dialogue in reverse_transcriptions:
            if (dialogue["speaker"].lower() == "agent") :
                call_closing_count += 1
                call_closing_sentiment += sentiment_mapping[dialogue["sentiment"]]
            else:
                break

        call_closing_sentiment= max(0, call_closing_sentiment)
        call_closing_score = call_closing_sentiment/call_closing_count

        path = LocalConfig().DATA_FOLDER + "/" + "audios_info/mappings.json"
        with open(path) as fh:
            call_dict = json.load(fh)

        call_dict[audio_file]["language"] = language
        call_dict[audio_file]["overall_sentiment"] = [k for k,v in sentiment_mapping.items() if v == overall_sentiment][0]
        call_dict[audio_file]["call_opening_score"] = call_opening_score
        call_dict[audio_file]["call_closing_score"] = call_closing_score

        with open(path, "w") as json_file:
            json.dump(call_dict, json_file, indent=4)

    def power_bi_main_report(self):

        with open("data/audios_info/mappings.json") as fh:
            data = json.load(fh)

        output = []
        for k,v in data.items():
            res = {}
            res["audio_filename"] = k
            for attr, value in v.items():
                res[attr] = value
            output.append(res)

        dff = pd.DataFrame.from_dict(output)
        dff.to_excel("PowerBi_main.xlsx")
        # Save excel




    # path = "./data/transcript/transcript_output.json"
    # try:
    #     obj.pipeline_after_transcription(transcription_jsonPath= path)
    # except Exception as e:
    #     print(f"Exception : {e}")
    #     print(f"\ntraceback : {traceback.format_exc()}")

    # path = "./data/audio_analytics/sample_audio/power_bi_merged_output.json"
    # try:
    #     obj.powerbi_report_keyword(jsonPath= path)
    # except Exception as e:
    #     print(f"Exception : {e}")
    #     print(f"\ntraceback : {traceback.format_exc()}")


    ## @@@@@@@@@@@@@@@@@@@@@ ###############
    # audio = "sample_audio"
    # merged_output_jsonPath = f"data/audio_analytics/{audio}/merged_output.json"
    # obj.power_bi_report_main_helper(audio_file= "Call 1.wav")
    # obj.power_bi_report_main_helper(audio_file= "Call 2.wav")
    # obj.power_bi_main_report()
    ############## @@@@@@@@@@@@@@@@@@@@@@ ###################################
    

################################################################# Testing ###################################################################################
if __name__ == "__main__":
    obj = Main()

    ####### PowerBI mapping.json #########
    audio_file = "Call 2.wav"
    obj.power_bi_report_main_helper(audio_file, merged_output_jsonPath = "data/audio_analytics/sample_audio/merged_output.json")
    #power_bi_report_main_helper(self, audio_file, merged_output_jsonPath = "data/audio_analytics/sample_audio/merged_output.json" )


    ######### Azure Translator ############
    # audio_name = "Call 1"
    # transcription_jsonPath = f"data/audio_analytics/sample_audio/transcript_output.json"
    # temp_result = obj.get_translated_transcriptions(audio_name, transcription_jsonPath)
    # print(f"The final path of the created json file is: {temp_result}")


        

        
            

    