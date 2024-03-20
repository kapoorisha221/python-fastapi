# from IPython import display as disp
from config.config import *
# import torch
# from pydub import AudioSegment as sm
# from pydub.utils import mediainfo
import os
import soundfile
# import torchaudio
# from denoiser import pretrained
# from denoiser.dsp import convert_audio
from utils import *

class SpeechPreprocessing():
    def __init__(self, audio_path) -> None:
        # Audio path where input audio(raw) is stored
        self.audio_path = audio_path
        # Current path from which audio data is read for audio pre-processing
        self.current_path = self.audio_path
        
        self.file_name = self.audio_path.split("/")[-1]
        # Output path where processed audio will get stored
        self.output_path = os.path.join(LocalConfig().PROCESSED_DATA_FOLDER, self.file_name)

    # def denoising(self):
    #     """Method for reducing the noise in the provided audio input
    #     """
    #     try:
    #         print("Entered Denoising")
    #         #loading the denoiser model 
    #         model=pretrained.dns64()

    #         #extracting the attributes of the audio file
    #         wav, sr=torchaudio.load(self.current_path)
    #         wav=convert_audio(wav,sr,model.sample_rate,model.chin)
            
    #         with torch.no_grad():
    #             denoised=model(wav[None])[0]
            
    #         # saving the denoised audio file to the output path 
    #         torchaudio.save(self.output_path, denoised.data.cpu(), model.sample_rate)
    #         print("End")
    #     except Exception as e:
    #         print(f"Exception inside denoising : {e}")

    def change_sample_rate(self):
        """Method for changing the sample rate of the provided audio input
        """
        try:
            print("Entered change_sample_rate")
            data, samplerate=soundfile.read(self.current_path)
            # saving the audio file to the output path
            soundfile.write(file= self.output_path,data= data, samplerate= FileConfig().DESIRED_SAMPLE_RATE)
            print("End")
        except Exception as e:
            print(f"Exception isnide change_sample_rate() : {e}")

    def change_subtype(self):
        """Method for changing the subtype of the provided audio path
        """
        try:
            print("Entered change_bit_rate")
            data, samplerate=soundfile.read(self.current_path)
            # saving the audio file to the audio path
            soundfile.write(file= self.output_path, data= data, samplerate= samplerate, subtype=FileConfig().DESIRED_SUBTYPE)
            print("End")
        except Exception as e:
            print(f"Exception inside change_bit_rate() : {e}")

    def processing_main(self):
        """Method for inout audio pre-processing
        """
        try:
            print(f"audio path : {self.audio_path}")
            print(f"output path : {self.output_path}")

            # # Denoising
            # if FileConfig().IS_DENOISING:
            #     self.denoising()
            #     self.current_path = self.output_path
            
            sf = get_audio_attributes(path= self.current_path)
            print(f"subtype : {sf.subtype}")
            print(f"samplerate : {sf.samplerate}")
            # Change subtype of audio file
            if sf.subtype not in FileConfig().ALLOWED_SUBTYPES:
                self.change_subtype()
                self.current_path = self.output_path

            
            # Change Sample rate of audio file 
            if sf.samplerate not in FileConfig().ALLOWED_SAMPLE_RATES:
                self.change_sample_rate()
                self.current_path = self.output_path
            
            if self.audio_path == self.current_path:
                return self.audio_path
                
            return self.output_path
        except Exception as e:
            print(f"Exception inside processing_main() : {e}")
