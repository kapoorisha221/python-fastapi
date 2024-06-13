import os
import subprocess, json
#from soundfile import SoundFile

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

# def get_audio_attributes(path):
#     """Method for getting audio attributes like samplerate, subtype, channels
#     Args:
#         path (str): audio path
#     Returns;
#         object : object using which we can get audio attributes
#     """
#     try:
#         sf = SoundFile(path)
#         info_logger.info(msg=F"Audio loded to Python SOundFile Successfully",extra={"location":"utils.py - get_audio_attributes"})
#         return sf
#     except Exception as e:
#         error_logger.error(msg="An Error Occured ..",exc_info=e,extra={"location":"utils.py - get_audio_attributes"})
        
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


def detect_silence(path,time):
    '''This function is a python wrapper to run the ffmpeg command in python and extranct the desired output
    
    path= Audio file path,
    time = silence time threshold
    
    returns = list of tuples with start and end point of silences   
    '''
    command="ffmpeg -i "+path+" -af silencedetect=n=-23dB:d="+str(time)+" -f null -"
    command = command.split()
    print("running command in shell")
    out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    s=stdout.decode("utf-8")
    k=s.split('[silencedetect @')
    if len(k)==1:
        #print(stderr)
        return None
        
    start,end=[],[]
    for i in range(1,len(k)):
        x=k[i].split(']')[1]
        if i%2==0:
            x=x.split('|')[0]
            x=x.split(':')[1].strip()
            end.append(float(x))
        else:
            x=x.split(':')[1]
            x=x.split('size')[0]
            x=x.replace('\r','')
            x=x.replace('\n','').strip()
            start.append(float(x))
    return list(zip(start,end))


def get_total_silence(audio_path):
    audio_path = normalize_path(audio_path)
    print("Audio path passed to detect the silence time: ", audio_path)
    silent_segments = detect_silence(path= audio_path, time= 1)
    print("silent segments", silent_segments)
    total_silence = 0
    for i in silent_segments:
        total_silence += (i[1] - i[0])

    print(f"Total Silence detected : {total_silence} secs")
    return total_silence

def normalize_path(path):
    """
    This function checks if the provided path contains backward slashes
    and replaces them with forward slashes.
    
    Args:
    path (str): The path to be normalized.
    
    Returns:
    str: The normalized path with forward slashes.
    """
    normalized_path = path.replace('\\', '/')
    
    return normalized_path




if __name__ == "__main__":
    #path = "C:\Users\GagandeepSingh1\Desktop\TE06.06.24\TE06.06.24\data\processed_data\161560999.wav"
    p = "../data/processed_data/161316483.wav"
    p1 = "../source/tempdata/161316483.wav"
    result = get_total_silence(audio_path= p1)
    print(result)
    
                

