import os, uvicorn, time, json
from fastapi import FastAPI, UploadFile,BackgroundTasks, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from fastapi.responses import JSONResponse
from datetime import datetime

from logs.logger import get_Error_Logger, get_Info_Logger, log_Garbage_Collector
from main import Main  
from config.config import LocalConfig

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
info_logger = get_Info_Logger()
error_logger = get_Error_Logger()


def Process_Audio_files(agent_name, call_date):
    try:
        info_logger.info(msg="Checking for the Old Logs",extra={"location":"App.py - Process_Audio_files"})
        log_Garbage_Collector()
        obj = Main()
        obj.audios_main(agent_name, call_date)
    except Exception as e:
         error_logger.error(msg="An Error Occured ..",exc_info=e,extra={"location":"App.py - Process_Audio_files"})
    

########################################## Routes ###########################################################################
@app.post("/uploadfile/")
async def create_upload_file(
    files: List[UploadFile] = File(...),
    agent_name: str = Form(...),
    date_str: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks
):
    try:
        # Validate and convert date string to date object
        try:
            date = datetime.strptime(date_str, "%d-%m-%Y").date()
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="Invalid date format, expected YYYY-MM-DD"
            )
        # Process files
        for file in files:
            with open(os.path.join(LocalConfig().RAW_DATA_FOLDER, file.filename), "wb") as f:
                contents = await file.read()
                f.write(contents)

        Process_Audio_files(agent_name, date_str)
        info_logger.info(msg="got the files and scheduled Background Task", extra={"location": "app.py-create_upload_file"})
        return {"message": "Got the files, will start Processing them Now!!!!"}

    except Exception as e:
        error_logger.error(msg="An Error Occurred at post request..", exc_info=e, extra={"location": "app.py-create_upload_file"})
        raise HTTPException(status_code=500, detail="An error occurred while processing the request.")


@app.get("/readallaudios")
def read_all_audios():
    audio_source_path = ""
    

@app.post("/getfiledata/")
async def get_file(file_lang: str= Form(...),folder_name: str = Form(...)):
    if file_lang == "ar":
        file_name = "arabic_power_bi_merged_output.json"
    elif file_lang =="en":
        file_name = "power_bi_merged_output.json"

    folder_path = LocalConfig().DATA_FOLDER + "/" +"audio_analytics" +"/"+ folder_name 
    file_path = os.path.join(folder_path, file_name)
    file_path = folder_path + "/" + file_name

    if not os.path.exists(folder_path):
        raise HTTPException(status_code=404, detail="Folder not found")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # with open(file_path, 'r') as file:
        #     data = file.read()
        #     json_data = json.loads(data)
        with open(file=file_path, mode="r", encoding="utf-8") as fh:
            json_data = json.load(fh)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

    return JSONResponse(content=json_data)


@app.get("/getaudiolist")
async def get_audio_list():
    audio_data_path = "data/audios_info/mappings.json"
    try:
        with open(audio_data_path, "r") as mapping:
            data = mapping.read()
            json_data = json.loads(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
    return JSONResponse(content=json_data)
          

from pyngrok import ngrok  
ngrok.set_auth_token("2al4KKug9Lj9a6NNZxArDX0BMNH_618BhSscx74HW56SR4RAM")
public_url = ngrok.connect(8000)
print(f"FastAPI application is accessible at: {public_url}")


if __name__ == "__main__":
    uvicorn.run(app)