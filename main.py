


import json
from src.audio.audio import *
from config.config import *
from utils import *
from src.adapters.transcription import *

class Main():

    def add_to_mapping(self, audio_file_path): 
        print("____________________audiofile_path_____________________________________________",audio_file_path)

        
        path = LocalConfig().DATA_FOLDER + "/" + "audios_info/mappings.json"
        with open(path) as fh:
            call_dict = json.load(fh)
        print("______________________call_dict___________________________________________",call_dict)
        next_call_number = len(call_dict) + 1

        next_call_name = 'Call_{}'.format(next_call_number) + ".wav"
        print("____________________id value:_________________________________________", next_call_name)
        audio_file = audio_file_path.split("/")[-1]

        print("____________audio_file______________", audio_file)
        call_dict[audio_file] = {"id" : next_call_name}

        audio_atrs = get_audio_attrs_for_report(audio_path= audio_file_path)
        call_dict[audio_file]["audio_duration"] = audio_atrs["audio_duration"]
        call_dict[audio_file]["audio_file_size"] = audio_atrs["audio_file_size"]

        print("_________________________________________________________________",call_dict)


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
            print(f"________________________path for the file {audio_file}_______________________is: ", path1)
            attrs = get_audio_attributes(path= path1)
            print(f"sample rate  {attrs.samplerate}")
            print(f"subtype : {attrs.subtype}")
            print(f"channels : {attrs.channels}")
    
            path2 = LocalConfig().PROCESSED_DATA_FOLDER + "/" + filename + ".wav"
            print("____________path2____________________ ",path2)
            # processing
            audio_processing(input_path= path1, output_path= path2)
             # get & store informations 
            self.add_to_mapping(audio_file_path= path2)

            # make folders for the audios where corresponding analytics will get stored
            folder = LocalConfig().DATA_FOLDER + "/audio_analytics/" + filename
            os.makedirs(folder, exist_ok= True)

            recognize_from_file(audio_file_path=path2,folder=folder)




    