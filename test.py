from pydub import AudioSegment
from soundfile import SoundFile
import soundfile 
from utils import *
path = r"C:\Users\GagandeepSingh\Etisalat STT TTS POC\C3808142.mp3"
output = r"C:\Users\GagandeepSingh\Etisalat STT TTS POC\C3808142.wav"
from utils import *

def convert_wav(path,output):
    if path.split(".")[-1]=="mp3":
        audio = AudioSegment.from_mp3(path)
        audio.export(output,format="wav")

def detect_number_of_channels(path):
    audio=AudioSegment.from_file(path)
    print(audio.channels)


def convert_to_mono(path,output):
    sound=AudioSegment.from_wav(path)
    sound=sound.set_channels(1)
    sound.export(output,format="wav")

def change_sample_rate(audio_path, output_path):
    """Method for changing the sample rate of the provided audio input
    """
    try:
        print("Entered change_sample_rate")
        data, samplerate=soundfile.read(audio_path)
        # saving the audio file to the output path
        soundfile.write(file= output_path,data= data, samplerate= 10000)
        print("End")
    except Exception as e:
        print(f"Exception isnide change_sample_rate() : {e}")

def change_subtype(audio_path, output_path):
    """Method for changing the subtype of the provided audio path
    """
    try:
        print("Entered change_bit_rate")
        data, samplerate=soundfile.read(audio_path)
        # saving the audio file to the audio path
        soundfile.write(file= output_path, data= data, samplerate= samplerate, subtype= "PCM_32")
        print("End")
    except Exception as e:
        print(f"Exception inside change_bit_rate() : {e}")

def print_audio_attrs(path):
    sf = get_audio_attributes(path)
    print(sf.samplerate)
    print(sf.channels)
    print(sf.subtype)

if __name__ == "__main__":
    # print_audio_attrs(path = "english_male_test_app_out_5sec.wav")

    # audio_path = "english_male_test_app_out_5sec.wav"
    # op = "test.wav"
    # change_sample_rate(audio_path= audio_path, output_path= op)
    # audio_path= op
    # op = "test.wav"
    # change_subtype(audio_path= op, output_path= op)
    print_audio_attrs(path = "./data/raw_data/test.wav")
    print_audio_attrs(path = "./data/processed_data/test.wav")
    # convert_wav(path, output)
    # detect_number_of_channels(path= path)
   # r = open(r"output\tts_result.wav", "rb").read()
    
    #detect_number_of_channels(path = "C:\Users\GagandeepSingh\Etisalat STT TTS POC\data\raw_data\audio_hindi.wav")
   
