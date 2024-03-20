from pydub import AudioSegment
import os, pickle, json
# import jsonschema
# from jsonschema import validate
from config.config import *
from soundfile import SoundFile
from datetime import datetime
import pandas as pd
import librosa

import matplotlib.pyplot as plt
from wordcloud import WordCloud
# from cosmos_db import AzureCosmos

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

def save_wordcloud(text, language, file = 'wordcloudimg1.png'):
    #word_cloud_ar = self.azure_translator.get_translations(word_cloud, 'en', detected_locale)
    worldcloud = ""
    if language == "en":
        worldcloud = WordCloud( background_color='white',
                            mode='RGB', width=2000, height=1000).generate(text)
    elif language == "ar":
        worldcloud = WordCloud(font_path= "./fonts/NotoNaskhArabic-Regular.ttf" , background_color='white',
                            mode='RGB', width=2000, height=1000).generate(text)
    plt.imshow(worldcloud)
    plt.axis("off")
    plt.savefig(file, bbox_inches='tight')
    plt.close()

def get_text_from_keyphrases(keyPhrase_ls):
    string = ""
    for ls in keyPhrase_ls:
        if isinstance(ls, list):
            text = " ".join(ls)
            string += text
    return string

        

def delete_file(file_path):
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Exception in delete_file() : {e}")
    

def load_pickle(path):
    with open(path, "rb") as fh:
        res = pickle.load(fh)
    return res


def do_logging(content):
    d = datetime.now()
    timestamp = d.strftime("%Y-%m-%d %H:%M:%S")
    r = timestamp + " --> " + content
    with open("./data/logging.txt", "a") as fh:
        fh.write(content)
        fh.write("\n")
        
def get_audio_attributes(path):
    """Method for getting audio attributes like samplerate, subtype, channels
    Args:
        path (str): audio path
    Returns;
        object : object using which we can get audio attributes
    """
    try:
        sf = SoundFile(path)
        return sf
    except Exception as e:
        print(f"Exception inside get_audio_attributes() : {e}")

def make_directories():
    try:
        folders = ["./data/logs", "./data/processed_data", "data/raw_data", "data/tts_output"]
        for folder in folders:
            os.makedirs(folder, exist_ok= True)
    except Exception as e:
        print(f"Excdeption inside make_directories() : {e}")
        
def convert_to_wav(path,output):
    """Method for converting the format of provided audio file to wav format
    """
    try:
        if path.split(".")[-1]=="mp3":
            audio = AudioSegment.from_mp3(path)
            audio.export(output,format="wav")
    except Exception as e:
        print(f"Exception inside convert_to_wav() : {e}")



def convert_to_mono(path,output):
    """Method for converting the number of channels to single channel of the provided audio input
    Args:
        path (str): audio path
        output_path (str): path where audio with 1 channel will get stored.
    """
    try:
        sound=AudioSegment.from_wav(path)
        sound=sound.set_channels(1)
        sound.export(output,format="wav")
    except Exception as e:
        print(f"Exception inside conver_to_mono() : {e}")

def delete_files(folder_path):
    """This function deleted all the files in a given folder 

    Args:
        folder_path (str): path of the folder
    """
    
    try:
        for file_name in os.listdir(folder_path):
            if not file_name.startswith("."):
                path = f"{folder_path}/{file_name}"
                print("deleting : ", path)
                os.remove(path)
    except Exception as e:
        print(f"Exception in delete_files() : {e}")

def clean_folders(folders):
    """This function clear the contents inside teh given folders
    """
    try:
        for foler in folders:
            delete_files(foler)
    except Exception as e:
        print(f"Exception inside clean_folders() : {e}")


def is_file_present(folder_path, filename):
    try:
        for file_name in os.listdir(folder_path):
            if not file_name.startswith("."):
                if file_name == filename:
                    return True
        return False
    except Exception as e:
        print(f"Exception in delete_files() : {e}")

def increase_current_tts_result_count():
    try:
        with open("/cognitive/projects/speech/PROJ-DEV-AI-CS-STT-TTS-REPO/data/tts_settings/tts.json") as fh:
            res = json.load(fh)
        res['current_tts_result_count'] += 1
        with open("/cognitive/projects/speech/PROJ-DEV-AI-CS-STT-TTS-REPO/data/tts_settings/tts.json", "w") as fh:
            res = json.dump(res, fh)
    except Exception as e:
        print(f"Exception increase_current_tts_result_count() : {e}")

def get_current_tts_result_count():
    with open("/cognitive/projects/speech/PROJ-DEV-AI-CS-STT-TTS-REPO/data/tts_settings/tts.json") as fh:
        res = json.load(fh)
        return res['current_tts_result_count']

######################### POWER BI ####################################
def get_audio_duration(path):
    return librosa.get_duration(path = path)
    
def get_audio_file_size(path):
    return os.path.getsize( path)

def convert_bytes(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
        
def get_token_numbers(text):
    return len(text.split())

def get_audio_attrs_for_report(audio_path):
    duration = get_audio_duration(audio_path)
    sz = get_audio_file_size(audio_path) 
    file_size = convert_bytes(sz)
    if 'KB' in file_size:
        file_size = file_size.replace("KB", "").strip()
        file_size = float(file_size)
    return {"audio_duration": duration, "audio_file_size": file_size}

def get_character_counts(text):
    return len([char for char in text])
    
def get_text_attrs_for_report(text):
    token_length = get_token_numbers(text)
    return {"token_length": token_length}


