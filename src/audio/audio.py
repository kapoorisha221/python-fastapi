import librosa
import soundfile as sf
import uuid
from config.config import *
import mutagen 
from mutagen.wave import WAVE 


def mp3_to_wav(mp3_file, wav_file):

    mp3_file = mp3_file
    # wav_file = "data/audio_input/input.wav"
    format_options = {
    "sample_width": 1,  # 1 byte per sample
    "sample_rate": 16000,  # 16 kHz sample rate
    "channels": 1  # mono audio
    }

# Load the MP3 file using librosa
    audio, sr = librosa.load(mp3_file, sr=format_options["sample_rate"])

# Export the audio to WAV format using soundfile
    with sf.SoundFile(wav_file, mode='w', samplerate=format_options["sample_rate"], channels=format_options["channels"]) as file:
        file.write(audio)
    

def audio_processing(input_path, output_path):
   
    format_options = {
    "sample_width": 1,  # 1 byte per sample
    "sample_rate": 16000,  # 16 kHz sample rate
    "channels": 1,  # mono audio
    "subtype": "" # encoding like PCM_16, u-law
    }
    # Load the MP3 file using librosa
    audio, sr = librosa.load(input_path, sr=format_options["sample_rate"])

    # Export the audio to WAV format using soundfile
    with sf.SoundFile(output_path, mode='w', samplerate=format_options["sample_rate"], channels=format_options["channels"]) as file:
        file.write(audio)

    # change subtype if needed
        

def change_subtype(input_path, output_path):
    """Method for changing the subtype of the provided audio path
    """
    try:
        print("Entered change_bit_rate")
        data, samplerate=sf.read(input_path)
        # saving the audio file to the audio path
        sf.write(file= output_path, data= data, samplerate= samplerate, subtype=FileConfig().DESIRED_SUBTYPE)
        print("End")
    except Exception as e:
        print(f"Exception inside change_bit_rate() : {e}")

# def get_audio_duration(path):
#     y, sr = librosa.load(librosa.ex(path))
#     return librosa.get_duration(y=y, sr=sr)

def audio_duration(length): 
    hours = length // 3600  # calculate in hours 
    length %= 3600
    mins = length // 60  # calculate in minutes 
    length %= 60
    seconds = length  # calculate in seconds 
  
    return hours, mins, seconds  # returns the duration 

def get_audio_duration_in_seconds(path):
    audio = WAVE(path) 
    
    # contains all the metadata about the wavpack file 
    audio_info = audio.info 
    length = int(audio_info.length) 
    hours, mins, seconds = audio_duration(length) 
    print('Total Duration: {}:{}:{}'.format(hours, mins, seconds)) 
    total_seconds = (hours*60*60) + (mins * 60) + seconds
    print(f"total seconds : {total_seconds}")
    return total_seconds

# def get_audio_file_size(path):
#     return os.path.getsize( path)

# def convert_bytes(num):
#     for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
#         if num < 1024.0:
#             return "%3.1f %s" % (num, x)
#         num /= 1024.0

def get_audio_file_size_in_KB(path):
    # Define the audio file path
    audio_file_path = "data/processed_data/Call 1.wav"

    # Get the file size in bytes
    file_size_bytes = os.path.getsize(audio_file_path)

    # Convert the file size to KB
    file_size_kb = file_size_bytes / 1024

    # # Print the file size in KB
    # print(f"The size of the audio file is {file_size_kb:.2f} KB")

    return file_size_kb 
def get_token_numbers(text):
    return len(text.split())

def get_audio_attrs_for_report(audio_path):
    duration = get_audio_duration_in_seconds(path= audio_path)
    file_size = get_audio_file_size_in_KB(path= audio_path)  
    return {"audio_duration": duration, "audio_file_size": file_size}
