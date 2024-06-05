import os
from soundfile import SoundFile

from logs.logger import *


info_logger = get_Info_Logger()
error_logger = get_Error_Logger()

def is_file_present(folder_path, filename):
    try:
        for file_name in os.listdir(folder_path):
            if not file_name.startswith("."):
                if file_name == filename:
                    return True
        return False
    except Exception as e:
        # print(f"Exception in delete_files() : {e}")
        error_logger.error(msg="An Error Occured ..",exc_info=e,extra={"location":"utils.py - is_file_present"})

def get_audio_attributes(path):
    """Method for getting audio attributes like samplerate, subtype, channels
    Args:
        path (str): audio path
    Returns;
        object : object using which we can get audio attributes
    """
    try:
        sf = SoundFile(path)
        info_logger.info(msg=F"Audio loded to Python SOundFile Successfully",extra={"location":"utils.py - get_audio_attributes"})
        return sf
    except Exception as e:
        error_logger.error(msg="An Error Occured ..",exc_info=e,extra={"location":"utils.py - get_audio_attributes"})
        
        
def get_text_count_from_keyphrases(keyPhrase_ls):
    dic = {}
    for ls in keyPhrase_ls:
        if isinstance(ls, list):
            for kp in ls:
                if kp in dic.keys():
                    dic[kp] += 1
                else:
                    dic[kp] = 1
    output = []       
    for key, count in dic.items():
        d1 = {"text": key, "value": count}
        output.append(d1)
    return output


def convert_to_minutes(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
     
    return "%d:%02d:%02d" % (hour, minutes, seconds)

def utilization_precentage(transcription_path):
    with open(transcription_path, "r", encoding="utf-8") as fp:
        transcript_data = json.load(fp)

    total_duration = 0
    agent_duration = 0
    customer_duration = 0

    for dialogue in transcript_data["transcript"]:
        duration = float(dialogue["duration_to_play"])
        total_duration += duration
        if dialogue["speaker"] == "Agent":
            agent_duration += duration
        elif dialogue["speaker"] == "Customer":
            customer_duration += duration

    # Calculate the percentages
    agent_percentage = (agent_duration / total_duration) * 100
    customer_percentage = (customer_duration / total_duration) * 100

    # Rounding off the values
    agent_percentage = "{:.2f}".format(agent_percentage)
    customer_percentage = "{:.2f}".format(customer_percentage)

    print("agent_percentage", agent_percentage, "customer_percentage", customer_percentage)
    return agent_percentage, customer_percentage
