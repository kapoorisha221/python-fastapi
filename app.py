import os
import time
from fastapi import FastAPI, UploadFile,BackgroundTasks
from typing import List

from fastapi.responses import RedirectResponse
from config.config import *
import uvicorn
from logs.logger import *

from main import Main  

app = FastAPI()

info_logger = get_Info_Logger()
error_logger = get_Error_Logger()


def Process_Audio_files():
    try:
        info_logger.info(msg="Checking for the Old Logs",extra={"location":"App.py - Process_Audio_files"})
        log_Garbage_Collector()
        obj = Main()
        obj.audios_main()
    except Exception as e:
         error_logger.error(msg="An Error Occured ..",exc_info=e,extra={"location":"App.py - Process_Audio_files"})
    
@app.get("/")
def redirect_to_docs():
     return RedirectResponse("/docs")
    
@app.post("/uploadfile/")
async def create_upload_file(files: List[UploadFile], background_tasks: BackgroundTasks):
    try:
        for file in files:
                with open(os.path.join(LocalConfig().RAW_DATA_FOLDER, file.filename), "wb") as f:
                    f.write(await file.read())

        background_tasks.add_task(Process_Audio_files)
        info_logger.info(msg="got the files and scheduled Background Task",extra={"location":"App.py-create_upload_file"})
        return {"message": "Got the files, will start Processing them Now!!!!"}
    except Exception as e:
        #  print(e)
         error_logger.error(msg="An Error Occured at post request..",exc_info=e,extra={"location":"App.py-create_upload_file"})
         return {"message": "An Error Occured while collecting the files!!"}

if __name__ == "__main__":
    host = "127.0.0.1"
    uvicorn.run(app,host=host, port=8000)