from flask import Flask, request,jsonify, send_file, make_response
# from flask_ngrok import run_with_ngrok 
from config.config import *
from flask_cors import CORS, cross_origin
from main import Main
import os, re, base64, logging, time
from utils import *

logging.basicConfig(filename= f"data/logs/Speech.log",
                    filemode= "a",
                    format= "%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
                    datefmt= "%H:%M:%S",
                    level= logging.INFO)

logger = logging.getLogger("ct-logger")


app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return "Hello world"

@app.route("/upload_audio_files", methods = ["POST"])
def upload():
    files = request.files.getlist("input")
    for file in files:
        print(f"filename :{file.filename}")
        file.save(os.path.join(LocalConfig().RAW_DATA_FOLDER, file.filename))

    obj = Main()
    obj.audios_main()
    # for file in os.listdir(LocalConfig().RAW_DATA_FOLDER):
    #     audio_path = LocalConfig().RAW_DATA_FOLDER + "/" + file
    #     filename = file.split(".")[:-1][0]
    #     print(filename)
    #     output_path = LocalConfig().PROCESSED_DATA_FOLDER + "/" + filename + ".wav"
    #     convert_to_wav(path= audio_path, output= output_path)

    return {"status": "success", "message": "audio files uploaded successfully"}

    # pass

@app.route("/list_audio_files", methods = ["GET"])
def list_audio_files():

    audio_files = os.listdir(LocalConfig().RAW_DATA_FOLDER)

    return {"audio_files": audio_files}

@app.route("/get_audio", methods = ["POST"])
def get_audio():
    audio_file = request.form['uuid']
    try:
        audio_file_name = audio_file.split(".")[:-1][0]
    except IndexError as e:
        audio_file_name = audio_file


    try:
        audio_path = LocalConfig().PROCESSED_DATA_FOLDER + "/" + audio_file_name + ".wav" 
        response = send_file(path_or_file= audio_path,
                                mimetype= "audio/wav",
                                as_attachment= True)
    except:
        print("Exception")
        audio_path = LocalConfig().RAW_DATA_FOLDER + "/" + audio_file_name + ".mp3"
        response = send_file(audio_path,as_attachment=True)
        
    return response

@app.route("/get_analytics", methods = ["POST", "GET"])
def stt():
    audio_file = request.form['uuid']
    print(f"audio file : {audio_file}")

    with open(file= "./data/analytics/samplecopy_2.json", mode= "r") as fp:
        d = json.load(fp= fp)

    return d
    
    # pass



if __name__ == "__main__":
    app.run(port=8080, debug= True)