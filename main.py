import json, os
import pandas as pd
from src.adapters.keyPhrase import keyPhrase
from src.adapters.sentiment_analysis import Sentiment
from src.adapters.summarisation import Summarization
from src.adapters.translator import AzureTranslator
from src.adapters.transcription import recognize_from_file
from src.audio.audio import audio_processing, get_audio_attrs_for_report
from src.utils import convert_to_minutes, is_file_present, get_audio_attributes, get_text_count_from_keyphrases
from logs.logger import get_Error_Logger, get_Info_Logger
from config.config import LocalConfig


class Main:
    info_logger = get_Info_Logger()
    error_logger = get_Error_Logger()

###################################################################################################################
##################################### Pre Processing and transcription ############################################
###################################################################################################################

    def add_to_mapping(self, audio_file_path, agent_name, call_date):
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
            audio_atrs = get_audio_attrs_for_report(audio_path=audio_file_path)
            minutes = convert_to_minutes(audio_atrs["audio_duration"])

            
            call_dict[audio_file] = {"id": next_call_name}
            call_dict[audio_file]["recordingID"] = next_call_number            
            call_dict[audio_file]["CallDuration"] = minutes
            call_dict[audio_file]["Audio_Size"] = int(audio_atrs["audio_file_size"])
            call_dict[audio_file]["Agent Name"] = agent_name
            call_dict[audio_file]["Call Date"] = call_date
            

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

    def audios_main(self, agent_name, call_date):
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
                    self.info_logger.info(
                        msg=f"file {file_to_check} already found",
                        extra={"location": "main.py-audios_main"},
                    )
                    continue
                #print(f"audio file: {audio_file}")
                extension = audio_file.split(".")[-1]
                filename = audio_file.split(".")[:-1][0]

                path1 = path + "/" + audio_file
                self.info_logger.info(
                    msg=f"Calling get_audio_attributes",
                    extra={"location": "main.py-audios_main"},
                )
                attrs = get_audio_attributes(path=path1)

                path2 = LocalConfig().PROCESSED_DATA_FOLDER + "/" + filename + ".wav"
                # processing
                audio_processing(input_path=path1, output_path=path2)
                # get & store informations
                self.add_to_mapping(audio_file_path=path2, agent_name=agent_name, call_date=call_date)

                # make folders for the audios where corresponding analytics will get stored
                folder = LocalConfig().DATA_FOLDER + "/audio_analytics/" + filename
                os.makedirs(folder, exist_ok=True)
                self.info_logger.info(
                    msg=f"Created folder for audio to save transcriptions at'{folder}'",
                    extra={"location": "main.py-audios_main"},
                )
                recognize_from_file(audio_file_path=path2, folder=folder)
                transcripted_json_file_path = folder + "/transcript_output.json"
                #transcripted_json_file_path_arabic = folder + "/"
                self.info_logger.info(
                    msg=f"Calling Post Transcription for audio '{filename}' and file '{transcripted_json_file_path}'",
                    extra={"location": "main.py-audios_main"},
                )
                self.pipeline_after_transcription(
                    audio_name=filename,
                    transcription_jsonPath=transcripted_json_file_path,
                )
                
            self.info_logger.info(
                    msg=f"Starts Creating the excel for",
                    extra={"location": "main.py-audios_main"},
                )
            self.create_excel_for_powerbi()
            self.info_logger.info(
                    msg=f" ################## Successfully: Done with the Processing of audio files ################## ",
                    extra={"location": "main.py-audios_main"},
                )
            #print("done with call processing")
        except Exception as e:
            self.error_logger.error(
                msg="An Error Occured ..",
                exc_info=e,
                extra={"location": "main.py-audios_main"},
            )

###################################################################################################################
##################################### Post Transcription Process ##################################################
###################################################################################################################

    def get_kpis(self, audio_name, transcription_jsonPath):
        try:
            result = {}
            with open(transcription_jsonPath, "r", encoding="utf-8") as fp:
                transcriptions = json.load(fp)
                self.transcriptions = transcriptions

            self.info_logger.info(
                msg=f"getting Conversational Summarization",
                extra={"location": "main.py - get_kpis"},
            )
            # summarisation_obj = Summarization()
            # summarisation_result = (
            #     summarisation_obj.conversational_summarisation_helper(audio_name, transcription_jsonPath)
            # )
            call = audio_name
            summarisation_obj = Summarization()
            summarisation_result = summarisation_obj.abstractive_summarisation_helper(call)
            self.summarisation_result = summarisation_result

            #print("______________________summarisation_result_________________________", summarisation_result)
            
            if summarisation_result:
                result["summary"] = summarisation_result["summary"]
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

    def get_kpis_arabic(self,audio_name, transciption_jsonpath_arabic):
        try:
            arabic_result = {}
            with open(transciption_jsonpath_arabic, "r", encoding="utf-8") as fp:
                arabic_transcriptions = json.load(fp)
                self.arabic_transcriptions = arabic_transcriptions

            self.info_logger.info(
                msg=f"getting Conversational Summarization",
                extra={"location": "main.py - get_kpis"},
            )

            #taking english summary as an input and translating it in Arabic
            eng_summ_result = self.summarisation_result
            trans_obj = AzureTranslator()
            #print("eng_summ_result[summary]", eng_summ_result["summary"])
            arabic_summarisation_result = trans_obj.get_translated_transcriptions_pipeline(eng_summ_result["summary"], "en", "ar-EG")

            if arabic_summarisation_result:
                arabic_result["summary"] = arabic_summarisation_result
            else:
                self.info_logger.info(
                    msg=f"getting no results for summary",
                    extra={"location": "main.py - get_kpis"},
                )
                arabic_result["summary"] = None

            self.info_logger.info(
                msg=f"getting sentiments for the dialogue",
                extra={"location": "main.py - get_kpis"},
            )
            sentiment_obj = Sentiment(transcripts=arabic_transcriptions)
            arabic_sentiment_result = sentiment_obj.sentiment_pipeline()
            if arabic_sentiment_result:
                arabic_result["sentiment_ls"] = arabic_sentiment_result
            else:
                arabic_result["sentiment_ls"] = None

            self.info_logger.info(
                msg=f"getting Keyphrases for the arabic dialogue and conversation in list",
                extra={"location": "main.py - get_kpis"},
            )
            keyPhrase_obj = keyPhrase(transcripts=arabic_transcriptions)
            arabic_keyPhrases_results = keyPhrase_obj.keyPhrase_pipeline()
            if arabic_keyPhrases_results:
                arabic_result["keyPhrases_ls"] = arabic_keyPhrases_results
            else:
                arabic_result["keyPhrases_ls"] = None

            self.file_path = f"data/audio_analytics/{audio_name}/"
            self.info_logger.info(
                msg=f"Saving arabic_kpi_output.json at location '{self.file_path}'",
                extra={"location": "main.py - get_kpis"},
            )
            arabic_json_path = self.file_path + "arabic_kpi_output.json"
            with open(file=arabic_json_path, mode="w", encoding = "utf-8") as fh:
                json.dump(arabic_result, fh, ensure_ascii=False, indent=4)
            self.info_logger.info(
                msg=f"Saved arabic_kpi_output.json at location '{self.file_path}'",
                extra={"location": "main.py - get_kpis"},
            )
            return arabic_result
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
            arabic_result = self.get_kpis_arabic(audio_name, transcription_jsonPath)

            # merge outputs
            merged_output = {}
            merged_output["result"] = {}
            merged_output_arabic = {}
            merged_output_arabic["result"] = {}

            merged_output["result"]["summary"] = result["summary"]
            merged_output_arabic["result"]["summary"] = arabic_result["summary"]

            unique_keyphrases = []
            unique_keyphrases_arabic = []

            for ls in result["keyPhrases_ls"]:
                if isinstance(ls, list):
                    for kp in ls:
                        unique_keyphrases.append(kp)
            unique_keyphrases = list(set(unique_keyphrases))
            self.info_logger.info(
                msg=f"Adding unique key phrases as topics to merged output",
                extra={"location": "main.py - pipeline_after_transcription"},
            )
            for ls in arabic_result["keyPhrases_ls"]:
                if isinstance(ls, list):
                    for kp in ls:
                        unique_keyphrases_arabic.append(kp)
            unique_keyphrases_arabic = list(set(unique_keyphrases_arabic))
            self.info_logger.info(
                msg=f"Adding unique key phrases as topics to merged output",
                extra={"location": "main.py - pipeline_after_transcription"},
            )

            merged_output["result"]["topics"] = unique_keyphrases
            merged_output_arabic["result"]["topics"] = unique_keyphrases_arabic
            self.info_logger.info(
                msg=f"getting text count from keyphrases and saving in merged output as wordcloud",
                extra={"location": "main.py - pipeline_after_transcription"},
            )

            merged_output["result"]["wordcloud"] = get_text_count_from_keyphrases(
                result["keyPhrases_ls"]
            )
            merged_output_arabic["result"]["wordcloud"] = get_text_count_from_keyphrases(
                arabic_result["keyPhrases_ls"]
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
            merged_output_arabic["result"]["transcripts"] = (
                self.merge_sentiment_with_transcription(
                    arabic_result["sentiment_ls"], self.arabic_transcriptions
                )
            )

            merged_output["result"]["language"] = self.transcriptions["transcript"][0][
                "locale"
            ].split("-")[0]
            merged_output_arabic["result"]["language"] = self.arabic_transcriptions["transcript"][0][
                "locale"
            ].split("-")[0]

            merged_path = self.file_path + "merged_output.json"
            merged_path_arabic = self.file_path + "arabic_merged_output.json"
            power_bi_merged_path = self.file_path + "power_bi_merged_output.json"
            power_bi_merged_path_arabic = self.file_path + "arabic_power_bi_merged_output.json"

            self.info_logger.info(
                msg=f"Saving merged_output.json as path '{self.file_path}'",
                extra={"location": "main.py - pipeline_after_transcription"},
            )
            with open(merged_path, mode = "w", encoding='utf-8') as fh:
                json.dump(merged_output, fh, indent=4)
            with open(merged_path_arabic, mode = "w", encoding="utf-8") as afh:
                json.dump(merged_output_arabic, afh, ensure_ascii=False, indent=4)

            self.info_logger.info(
                msg=f"merging keyphrases with transcription for power_bi_merged_output.json",
                extra={"location": "main.py - pipeline_after_transcription"},
            )
            merged_output["result"]["transcripts"] = (
                self.merge_keyphrases_with_transcription(
                    result["keyPhrases_ls"], merged_output["result"]["transcripts"]
                )
            )
            merged_output_arabic["result"]["transcripts"] = (
                self.merge_keyphrases_with_transcription(
                    arabic_result["keyPhrases_ls"], merged_output_arabic["result"]["transcripts"]
                )
            )

            self.info_logger.info(msg=f"Saving power_bi_merged_output.json as path '{self.file_path}'",
                extra={"location": "main.py - pipeline_after_transcription"},
            )
            with open(power_bi_merged_path, mode = "w", encoding='utf-8') as fh:
                json.dump(merged_output, fh, indent=4)
            with open(power_bi_merged_path_arabic, mode = "w", encoding='utf-8') as afh:
                json.dump(merged_output_arabic, afh, ensure_ascii=False, indent=4)

            self.power_bi_report_main_helper(
                audio_file=audio_name,
                merged_output_jsonPath=merged_path,
                powerbi_merged_jsonPath=power_bi_merged_path,
            )

            self.info_logger.info(msg=f"Saved power_bi_merged_output.json as path '{self.file_path}'",
                extra={"location": "main.py - pipeline_after_transcription"},
            )
            
        except Exception as e:
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

            self.info_logger.info(msg=f"KeyPhrases added with the transcription based on the both list indexing",
                extra={"location": "main.py - pipeline_after_transcription"},
            )
            output = {"transcript": modified_transcriptions}
            return output
        except Exception as e:
            self.error_logger.error(
                msg="An Error Occured: {e}",
                exc_info=e,
                extra={"location": "main.py - merge_sentiment_with_transcription"},
            )

###################################################################################################################
#################################### Power BI report creation process #############################################
###################################################################################################################

    def powerbi_report_keyword(self, powerbi_merged_jsonPath,audio_file):
        try:
            self.info_logger.info(msg=f"Starting function  powerbi_report_keyword",
                extra={"location": "main.py - powerbi_report_keyword"},
            )
            with open(powerbi_merged_jsonPath) as fp:
                information = json.load(fp)
                
            audio_file_ls , duration_ls, dialouges_ls, keywords_ls, sentiment_ls,sort_sentiment_ls =  [],[], [],[], [],[]
            
            self.info_logger.info(msg=f"Azure Translator instance created for translation of data for report",
                extra={"location": "main.py - powerbi_report_keyword"},
            )
            
            translator_obj = AzureTranslator()
            native_lang='en'
            output_lang='ar-EG'
            arabic_audio_file_ls , arabic_duration_ls, arabic_dialouges_ls, arabic_keywords_ls, arabic_sentiment_ls, arabic_sort_sentiment_ls =  [],[], [],[], [],[]
            
            self.info_logger.info(msg=f"Iterating over Dialogs to translate of file '{powerbi_merged_jsonPath}'",
                extra={"location": "main.py - powerbi_report_keyword"},
            )
            
            for dialouge in information["result"]["transcripts"]["transcript"]:
                if dialouge["keyPhrases"]:
                    sentiment_mapping = {"positive": 1, "negative": -1, "neutral": 0,"mixed":0}
                    for kp in dialouge["keyPhrases"]:
                        audio_file_ls.append(audio_file)
                        arabic_audio_file_ls.append(translator_obj.get_translations(text=audio_file,from_lang=native_lang,to_lang=output_lang))
                        
                        duration_ls.append(dialouge["duration_to_play"])
                        arabic_duration_ls.append(translator_obj.get_translations(text=dialouge["duration_to_play"],from_lang=native_lang,to_lang=output_lang))
                        
                        dialouges_ls.append(dialouge["dialogue"])
                        arabic_dialouges_ls.append(translator_obj.get_translations(text=dialouge["dialogue"],from_lang=native_lang,to_lang=output_lang))
                        
                        keywords_ls.append(kp)
                        arabic_keywords_ls.append(translator_obj.get_translations(text=kp,from_lang=native_lang,to_lang=output_lang))
                        
                        sentiment_ls.append(dialouge["sentiment"])
                        arabic_sentiment_ls.append(translator_obj.get_translations(text=dialouge["sentiment"],from_lang=native_lang,to_lang=output_lang))
                        
                        
                        sort_sentiment_ls.append(sentiment_mapping[dialouge["sentiment"]])
                        arabic_sort_sentiment_ls.append(translator_obj.get_translations(text=sentiment_mapping[dialouge["sentiment"]],from_lang=native_lang,to_lang=output_lang))
                                                
                else:
                    self.info_logger.info(msg=f"no keyword found for dialog '{dialouge['dialouge']}'",
                        extra={"location": "main.py - powerbi_report_keyword"},
                    )
                    
                    duration_ls.append(dialouge["duration_to_play"])
                    arabic_duration_ls.append(translator_obj.get_translations(text=dialouge["duration_to_play"],from_lang=native_lang,to_lang=output_lang))

                    audio_file_ls.append(audio_file)
                    arabic_audio_file_ls.append(translator_obj.get_translations(text=audio_file,from_lang=native_lang,to_lang=output_lang))
                    
                    dialouges_ls.append(dialouge["dialogue"])
                    arabic_dialouges_ls.append(translator_obj.get_translations(text=dialouge["dialogue"],from_lang=native_lang,to_lang=output_lang))

                    keywords_ls.append(None)
                    arabic_keywords_ls.append(None)

                    sentiment_ls.append(dialouge["sentiment"])
                    arabic_sentiment_ls.append(translator_obj.get_translations(text=dialouge["sentiment"],from_lang=native_lang,to_lang=output_lang))

                    sort_sentiment_ls.append(sentiment_mapping[dialouge["sentiment"]])
                    arabic_sort_sentiment_ls.append(translator_obj.get_translations(text=sentiment_mapping[dialouge["sentiment"]],from_lang=native_lang,to_lang=output_lang))


            # final result for an audio
            dic_pandas = {"audio_filename":audio_file_ls, "duration_1": duration_ls, "keywords_1": keywords_ls, 
                        "sentiment_1": sentiment_ls, "dialouge_1": dialouges_ls,"sort sentiment_1":sort_sentiment_ls}
            
            
            arabic_dic_pandas = {"audio_filename":arabic_audio_file_ls, "duration_1": arabic_duration_ls, "keywords_1": arabic_keywords_ls, 
                        "sentiment_1": arabic_sentiment_ls, "dialouge_1": arabic_dialouges_ls,"sort sentiment_1":arabic_sort_sentiment_ls}
            
            self.info_logger.info(msg=f"creating the dataframe for english and arabic report.",
                        extra={"location": "main.py - powerbi_report_keyword"},
                    )
            df1 = pd.DataFrame(dic_pandas)
            arabic_df1 = pd.DataFrame(arabic_dic_pandas)

            self.info_logger.info(msg=f"Returning the dataframe for english and arabic report.",
                        extra={"location": "main.py - powerbi_report_keyword"},)
                
            return df1, arabic_df1
        except Exception as e :
            self.error_logger.error(
                msg="An Error Occured ..",
                exc_info=e,
                extra={"location": "main.py-powerbi_report_keyword"},
            )

    def power_bi_report_main_helper(self, audio_file,powerbi_merged_jsonPath, merged_output_jsonPath):
            # Use merged_output.json & audios_info/mappings.json
            try:
                self.info_logger.info(msg=f"opening the '{merged_output_jsonPath}' for the powerbi main report",
                            extra={"location": "main.py - power_bi_report_main_helper"},)
                
                with open(merged_output_jsonPath) as fh:
                    data1 = json.load(fh)
                if data1.values() != 0:
                    val = "any value is picked"
                    

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

                self.info_logger.info(msg=f"starting to Iterate over the Dialogs of '{merged_output_jsonPath}'",
                            extra={"location": "main.py - power_bi_report_main_helper"},)
                
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
                
                self.info_logger.info(msg=f"Loading the mappings.json",
                            extra={"location": "main.py - power_bi_report_main_helper"},)

                path = LocalConfig().DATA_FOLDER + "/" + "audios_info/mappings.json"
                with open(path) as fh:
                    call_dict = json.load(fh)

                if (overall_sentiment >= 1):
                    overall_sentiment = 1
                elif(overall_sentiment <= -1):
                    overall_sentiment = -1
                    
                audio_file = audio_file + ".wav"
                call_dict[audio_file]["language"] = language
                call_dict[audio_file]["Sentiment"] = [k for k,v in sentiment_mapping.items() if v == overall_sentiment][0]
                call_dict[audio_file]["CallOpeningScore"] = call_opening_score
                call_dict[audio_file]["CallClosingScore"] = call_closing_score

                with open(path, "w") as json_file:
                    json.dump(call_dict, json_file, indent=4)
                
                self.info_logger.info(msg=f"Updated the values in mapping.json",
                            extra={"location": "main.py - power_bi_report_main_helper"},)
            except Exception as e :
                self.error_logger.error(
                    msg="An Error Occured ..",
                    exc_info=e,
                    extra={"location": "main.py - power_bi_report_main_helper"},
                )
                    
            
    def power_bi_main_report(self,mapping_json_path):
        try:
            self.info_logger.info(msg=f"opening the file '{mapping_json_path}'",
                            extra={"location": "main.py - power_bi_main_report"},)
            with open(mapping_json_path,'r') as fh:
                data = json.load(fh)

            output = []
            arabic_output = []
            
            translator_obj = AzureTranslator()
            
            native_lang='en'
            output_lang='ar-EG'

            self.info_logger.info(msg=f"STARTS iTERATING OVER DATA OF THE  '{mapping_json_path}'",
                            extra={"location": "main.py - power_bi_main_report"},)
            for k,v in data.items():
                eng_res = {}
                arabic_res = {}
                eng_res["audio_filename"] = k
                arabic_k = translator_obj.get_translations(text=k,from_lang=native_lang,to_lang=output_lang)
                arabic_res["audio_filename_2"] = "wav."+ arabic_k[:-4]
                for attr, value in v.items():
                    eng_res[attr] = value
                    
                    arabic_res[f"{attr}_2"] = translator_obj.get_translations(text=value,from_lang=native_lang,to_lang=output_lang)
                output.append(eng_res)
                arabic_output.append(arabic_res)

            self.info_logger.info(msg=f"creating data frame for the english and Arabic output",
                            extra={"location": "main.py - power_bi_main_report"},)
            
            dff = pd.DataFrame.from_dict(output)
            arabic_dff = pd.DataFrame.from_dict(arabic_output)
            
            self.info_logger.info(msg=f"Exporting the created dataframe to excel with name: 'eng_main_dataset.xlsx' and 'arb_main_dataset.xlsx'",
                            extra={"location": "main.py - power_bi_main_report"},)
            dff.to_excel("Powerbi_reports/eng_main_dataset.xlsx",index=False)
            arabic_dff.to_excel("Powerbi_reports/arb_main_dataset.xlsx",index=False)
        # Save excel
        except Exception as e:
            self.error_logger.error(
                msg="An Error Occured ..",
                exc_info=e,
                extra={"location": "main.py-audios_main"},
            )
        
    def create_excel_for_powerbi(self):
        try:
            path =LocalConfig()
            path = path.DATA_FOLDER + r"/audio_analytics"

            self.info_logger.info(
                    msg=f"starts iterating over audio_analytic for power_bi and merged_output .json",
                    extra={"location": "main.py-audios_main"},
                )
            
            All_audio_result = pd.DataFrame()
            arabic_All_audio_result = pd.DataFrame()
            calls_list = os.listdir(path)
            for calls in calls_list:
                powerbi_merged_path = f"{path}\{calls}\power_bi_merged_output.json"

                if ((is_file_present(folder_path= f"{path}\{calls}", filename= "merged_output.json")) and (is_file_present(folder_path= f"{path}\{calls}", filename= "power_bi_merged_output.json"))):
                    self.info_logger.info(msg=f"getting dataframe from power_bi_keyword for {calls} and appending it to to all_audio_result dataframe",
                    extra={"location": "main.py-create_excel_for_powerbi"})
                    
                    result_for_one_audio, arabic_result_for_one_audio = self.powerbi_report_keyword(powerbi_merged_jsonPath=powerbi_merged_path, audio_file=calls)
                    All_audio_result = All_audio_result._append(result_for_one_audio, ignore_index=True)
                    arabic_All_audio_result = arabic_All_audio_result._append(arabic_result_for_one_audio, ignore_index=True)

                    
            self.info_logger.info(msg=f"creating eng_dim_dataset excel using the data of All_audio_result dataframe",
                    extra={"location": "main.py-create_excel_for_powerbi"})
            
            All_audio_result.to_excel(f"Powerbi_reports/eng_dim_dataset.xlsx", index=False)
            arabic_All_audio_result.to_excel("Powerbi_reports/arb_dim_dataset.xlsx",index=False)

            
            self.info_logger.info(
                    msg=f"creating power_bi_main report using the mapping.json",
                    extra={"location": "main.py-create_excel_for_powerbi"},
                )
            self.power_bi_main_report(mapping_json_path=LocalConfig().DATA_FOLDER + "/audios_info\mappings.json")
            
        except Exception as e:
            self.error_logger.error(
                msg="An Error Occured ..",
                exc_info=e,
                extra={"location": "main.py-create_excel_for_powerbi"},
            )
            
if __name__ == "__main__":
    obj = Main()
    obj.create_excel_for_powerbi()