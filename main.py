import json, os
import pandas as pd
from src.adapters.keyPhrase import keyPhrase
from src.adapters.sentiment_analysis import Sentiment
from src.adapters.summarisation import Summarization
from src.adapters.translator import AzureTranslator
from src.adapters.transcription import recognize_from_file
from src.audio.audio import audio_processing, get_audio_attrs_for_report
from logs.logger import get_Error_Logger, get_Info_Logger
from utils import is_file_present, get_audio_attributes, get_text_count_from_keyphrases
from config.config import LocalConfig, AzureConfig


class Main:
    info_logger = get_Info_Logger()
    error_logger = get_Error_Logger()

    # #################################### Pre Processing and transcription ##################################################

    def add_to_mapping(self, audio_file_path):
        try:
            self.info_logger.info(
                msg=f"Started function add_to_mapping to create mapping.json data",
                extra={"location": "main.py - add_to_mapping"},
            )

            path = LocalConfig().DATA_FOLDER + "/" + "audios_info/mappings.json"
            with open(path) as fh:
                call_dict = json.load(fh)

            next_call_number = len(call_dict) + 1

            next_call_name = "Call_{}".format(next_call_number) + ".wav"

            audio_file = audio_file_path.split("/")[-1]

            call_dict[audio_file] = {"id": next_call_name}

            audio_atrs = get_audio_attrs_for_report(audio_path=audio_file_path)
            call_dict[audio_file]["audio_duration"] = audio_atrs["audio_duration"]
            call_dict[audio_file]["audio_file_size"] = audio_atrs["audio_file_size"]

            with open(path, "w") as json_file:
                json.dump(call_dict, json_file, indent=4)

            self.info_logger.info(
                msg=f"attributes added sucesfully to mapping.json for  '{audio_file}'",
                extra={"location": "main.py - add_to_mapping"},
            )
        except Exception as e:
            self.error_logger.error(
                msg="An Error Occured ..",
                exc_info=e,
                extra={"location": "main.py - add_to_mapping"},
            )

    def audios_main(self):
        try:
            """This function checks for all the files present inside RAW DATA folder and process & stores information for the
            audio files which are not present in PROCESSED data folder"""
            self.info_logger.info(
                msg="Sterted Processing from audios_main",
                extra={"location": "main.py-audios_main"},
            )
            path = LocalConfig().RAW_DATA_FOLDER
            for audio_file in os.listdir(path):
                # checks
                file_to_check = audio_file
                if audio_file.endswith(".mp3"):
                    file_to_check = audio_file.replace(".mp3", ".wav")
                if is_file_present(
                    folder_path=LocalConfig().PROCESSED_DATA_FOLDER,
                    filename=file_to_check,
                ):
                    # print(f"check : {audio_file}")
                    self.info_logger.info(
                        msg=f"file {file_to_check} already found",
                        extra={"location": "main.py-audios_main"},
                    )
                    continue
                print(f"audio file: {audio_file}")
                extension = audio_file.split(".")[-1]
                filename = audio_file.split(".")[:-1][0]

                path1 = path + "/" + audio_file
                self.info_logger.info(
                    msg=f"Calling get_audio_attributes",
                    extra={"location": "main.py-audios_main"},
                )
                attrs = get_audio_attributes(path=path1)
                # print(f"sample rate  {attrs.samplerate}")
                # print(f"subtype : {attrs.subtype}")
                # print(f"channels : {attrs.channels}")

                path2 = LocalConfig().PROCESSED_DATA_FOLDER + "/" + filename + ".wav"
                # processing
                audio_processing(input_path=path1, output_path=path2)
                # get & store informations
                self.add_to_mapping(audio_file_path=path2)

                # make folders for the audios where corresponding analytics will get stored
                folder = LocalConfig().DATA_FOLDER + "/audio_analytics/" + filename
                os.makedirs(folder, exist_ok=True)
                self.info_logger.info(
                    msg=f"Created folder for audio to save transcriptions at'{folder}'",
                    extra={"location": "main.py-audios_main"},
                )
                recognize_from_file(audio_file_path=path2, folder=folder)
                transcripted_json_file_path = folder + "/transcript_output.json"
                self.info_logger.info(
                    msg=f"Calling Post Transcription for audio '{filename}' and file '{transcripted_json_file_path}'",
                    extra={"location": "main.py-audios_main"},
                )
                self.pipeline_after_transcription(
                    audio_name=filename,
                    transcription_jsonPath=transcripted_json_file_path,
                )
            self.create_excel_for_powerbi()
        except Exception as e:
            # print(e)
            self.error_logger.error(
                msg="An Error Occured ..",
                exc_info=e,
                extra={"location": "main.py-audios_main"},
            )

    # #################################### Post Transcription Process ##################################################

    def get_kpis(self, audio_name, transcription_jsonPath):
        try:
            # additional to transcription
            result = {}
            with open(transcription_jsonPath, "r", encoding="utf-8") as fp:
                transcriptions = json.load(fp)
                self.transcriptions = transcriptions

            self.info_logger.info(
                msg=f"getting Conversational Summarization",
                extra={"location": "main.py - get_kpis"},
            )
            summarisation_obj = Summarization()
            summarisation_result = (
                summarisation_obj.conversational_summarisation_helper(
                    audio_name, transcription_jsonPath
                )
            )
            # summarisation_result = summarisation_obj.extractive_summarisation_helper()
            print(
                "_____________ summary ___________________________",
                summarisation_result["aspects_texts"],
            )
            if summarisation_result:
                result["summary"] = summarisation_result["aspects_texts"]
            else:
                self.info_logger.info(
                    msg=f"getting no results for summary",
                    extra={"location": "main.py - get_kpis"},
                )
                result["summary"] = None

            self.info_logger.info(
                msg=f"getting sentiments for the dialogue",
                extra={"location": "main.py - get_kpis"},
            )
            sentiment_obj = Sentiment(transcripts=transcriptions)
            sentiment_result = sentiment_obj.sentiment_pipeline()
            if sentiment_result:
                result["sentiment_ls"] = sentiment_result
            else:
                result["sentiment_ls"] = None

            self.info_logger.info(
                msg=f"getting Keyphrases for the dialogue and conversation in list",
                extra={"location": "main.py - get_kpis"},
            )
            keyPhrase_obj = keyPhrase(transcripts=transcriptions)
            keyPhrases_results = keyPhrase_obj.keyPhrase_pipeline()
            if keyPhrases_results:
                result["keyPhrases_ls"] = keyPhrases_results
            else:
                result["keyPhrases_ls"] = None

            self.file_path = f"data/audio_analytics/{audio_name}/"
            self.info_logger.info(
                msg=f"Saving kpi_output.json at location '{self.file_path}'",
                extra={"location": "main.py - get_kpis"},
            )
            with open(file=self.file_path + "kpi_output.json", mode="w") as fh:
                json.dump(result, fp=fh, indent=4)

            return result
        except Exception as e:
            self.error_logger.error(
                msg=f"An Error Occured: {e}",
                exc_info=e,
                extra={"location": "main.py - pipeline_after_transcription"},
            )

    def pipeline_after_transcription(self, audio_name, transcription_jsonPath):
        try:
            translator_obj = AzureTranslator()
            self.info_logger.info(
                msg=f"Calling get_translated_transcriptions for '{transcription_jsonPath}'",
                extra={"location": "main.py - pipeline_after_transcription"},
            )
            english_transcription_jsonpath = (
                translator_obj.get_translated_transcriptions(
                    audio_name, transcription_jsonPath
                )
            )

            self.info_logger.info(
                msg=f"Calling get_kpis for '{english_transcription_jsonpath}'",
                extra={"location": "main.py - pipeline_after_transcription"},
            )
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
            self.info_logger.info(
                msg=f"Adding unique key phrases as topics to merged output",
                extra={"location": "main.py - pipeline_after_transcription"},
            )

            merged_output["result"]["topics"] = unique_keyphrases

            # # with open(file_path + "wordcloud.png", 'rb') as image_file:
            # #     encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            # #     merged_output["result"]["wordcloud"] = encoded_image
            self.info_logger.info(
                msg=f"getting text count from keyphrases and saving in merged output as wordcloud",
                extra={"location": "main.py - pipeline_after_transcription"},
            )
            merged_output["result"]["wordcloud"] = get_text_count_from_keyphrases(
                result["keyPhrases_ls"]
            )

            self.info_logger.info(
                msg=f"merging sentiments with transcriptions and saving in merged output as transcription",
                extra={"location": "main.py - pipeline_after_transcription"},
            )
            merged_output["result"]["transcripts"] = (
                self.merge_sentiment_with_transcription(
                    result["sentiment_ls"], self.transcriptions
                )
            )

            merged_output["result"]["language"] = self.transcriptions["transcript"][0][
                "locale"
            ].split("-")[0]

            merged_path = self.file_path + "merged_output.json"
            power_bi_merged_path = self.file_path + "power_bi_merged_output.json"

            self.info_logger.info(
                msg=f"Saving merged_output.json as path '{self.file_path}'",
                extra={"location": "main.py - pipeline_after_transcription"},
            )
            with open(merged_path, "w") as fh:
                json.dump(merged_output, fh, indent=4)

            self.info_logger.info(
                msg=f"merging keyphrases with transcription for power_bi_merged_output.json",
                extra={"location": "main.py - pipeline_after_transcription"},
            )
            merged_output["result"]["transcripts"] = (
                self.merge_keyphrases_with_transcription(
                    result["keyPhrases_ls"], merged_output["result"]["transcripts"]
                )
            )

            self.info_logger.info(
                msg=f"Saving power_bi_merged_output.json as path '{self.file_path}'",
                extra={"location": "main.py - pipeline_after_transcription"},
            )
            with open(power_bi_merged_path, "w") as fh:
                json.dump(merged_output, fh, indent=4)

            self.power_bi_report_main_helper(
                audio_file=audio_name,
                merged_output_jsonPath=merged_path,
                powerbi_merged_jsonPath=power_bi_merged_path,
            )

        except Exception as e:
            # print(e)
            self.error_logger.error(
                msg=f"An Error Occured: {e}",
                exc_info=e,
                extra={"location": "main.py - pipeline_after_transcription"},
            )

    def merge_sentiment_with_transcription(self, sentiment_ls, transcriptions):
        try:
            modified_transcriptions = []
            # iterating over list where each item is a dialouge
            for item, sentiment in zip(transcriptions["transcript"], sentiment_ls):
                res = item.copy()
                res["sentiment"] = sentiment
                modified_transcriptions.append(res)

            self.info_logger.info(
                msg=f"sentiments added with the transcription based on the both list indexing",
                extra={"location": "main.py - pipeline_after_transcription"},
            )
            output = {"transcript": modified_transcriptions}
            return output
        except Exception as e:
            # print(e)
            self.error_logger.error(
                msg=f"An Error Occured: {e}",
                exc_info=e,
                extra={"location": "main.py - merge_sentiment_with_transcription"},
            )

    def merge_keyphrases_with_transcription(self, keyPhrases_ls, transcriptions):
        try:
            modified_transcriptions = []
            for item, keyPhrases_ls in zip(transcriptions["transcript"], keyPhrases_ls):
                res = item.copy()
                res["keyPhrases"] = keyPhrases_ls
                modified_transcriptions.append(res)

            self.info_logger.info(
                msg=f"KeyPhrases added with the transcription based on the both list indexing",
                extra={"location": "main.py - pipeline_after_transcription"},
            )
            output = {"transcript": modified_transcriptions}
            return output
        except Exception as e:
            # print(e)
            self.error_logger.error(
                msg="An Error Occured: {e}",
                exc_info=e,
                extra={"location": "main.py - merge_sentiment_with_transcription"},
            )

    ###################################################################################################################
    #################################### Power BI report creation process #############################################
    ###################################################################################################################

    def powerbi_report_keyword(self, powerbi_merged_jsonPath):
            with open(powerbi_merged_jsonPath) as fp:
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
            df1 = pd.DataFrame(dic_pandas)
            return df1
            

    def power_bi_report_main_helper(self, audio_file,powerbi_merged_jsonPath, merged_output_jsonPath):
            # Use merged_output.json & audios_info/mappings.json
        
            with open(merged_output_jsonPath) as fh:
                data1 = json.load(fh)
            if data1.values() != 0:
                print("any value is picked")

            sentiment_mapping = {"positive": 1, "negative": -1, "neutral": 0,"mixed":0}
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

            if (overall_sentiment >= 1):
                overall_sentiment = 1
            elif(overall_sentiment <= -1):
                overall_sentiment = -1
                
            print(overall_sentiment)
            print([k for k,v in sentiment_mapping.items() if v == overall_sentiment])
            audio_file = audio_file + ".wav"
            call_dict[audio_file]["language"] = language
            call_dict[audio_file]["overall_sentiment"] = [k for k,v in sentiment_mapping.items() if v == overall_sentiment][0]
            call_dict[audio_file]["call_opening_score"] = call_opening_score
            call_dict[audio_file]["call_closing_score"] = call_closing_score

            with open(path, "w") as json_file:
                json.dump(call_dict, json_file, indent=4)
                
            # self.powerbi_report_keyword(powerbi_merged_jsonPath)
            


    def power_bi_main_report(self,mapping_json_path):

        with open(mapping_json_path,'r') as fh:
            data = json.load(fh)

        output = []
        print(data)
        print(data.items())
        for k,v in data.items():
            res = {}
            res["audio_filename"] = k
            for attr, value in v.items():
                res[attr] = value
            output.append(res)

        dff = pd.DataFrame.from_dict(output)
        dff.to_excel("Powerbi_reports/PowerBi_main.xlsx")
        # Save excel
        
    def create_excel_for_powerbi(self):
        path =LocalConfig()
        path = path.DATA_FOLDER + r"/audio_analytics"
 
        for calls in os.listdir(path):
            powerbi_merged_path = f"{path}\{calls}\power_bi_merged_output.json"
            # path2 = f"{path}\{calls}\merged_output.json"
            
            All_audio_result = pd.DataFrame()
            for file in calls:
                if ((is_file_present(folder_path= f"{path}\{calls}", filename= "merged_output.json")) and (is_file_present(folder_path= f"{path}\{calls}", filename= "power_bi_merged_output.json"))):
                    result_for_one_audio = self.powerbi_report_keyword(powerbi_merged_jsonPath=powerbi_merged_path)
                    All_audio_result = All_audio_result._append(result_for_one_audio, ignore_index=True)
            
            print(All_audio_result)
            self.power_bi_main_report(mapping_json_path=LocalConfig().DATA_FOLDER + "/audios_info\mappings.json")
            All_audio_result.to_excel("Powerbi_reports/PowerBi_1.xlsx")
        
if __name__ == "__main__":
    obj = Main()
    obj.call_all_files()

