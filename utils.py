import os
from soundfile import SoundFile

def is_file_present(folder_path, filename):
    try:
        for file_name in os.listdir(folder_path):
            if not file_name.startswith("."):
                if file_name == filename:
                    return True
        return False
    except Exception as e:
        print(f"Exception in delete_files() : {e}")

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