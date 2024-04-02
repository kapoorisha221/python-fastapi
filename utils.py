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
