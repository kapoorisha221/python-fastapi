import os, uvicorn, time
from fastapi import FastAPI, UploadFile,BackgroundTasks, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from fastapi.responses import RedirectResponse, JSONResponse
from datetime import datetime

from logs.logger import get_Error_Logger, get_Info_Logger, log_Garbage_Collector
from main import Main  
from config.config import LocalConfig

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
    
# @app.get("/")
# def redirect_to_docs():
#      return RedirectResponse("/docs")

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

        # Schedule background task
        s_time = time.time()
        print("start time__________________________",s_time)
        Process_Audio_files(agent_name, date_str)
        e_time = time.time()
        print("End time__________________________",e_time)
        Time_taken = e_time - s_time
        print("time__________________________",Time_taken)
        #background_tasks.add_task(Process_Audio_files, agent_name, date_str)
        info_logger.info(msg="got the files and scheduled Background Task", extra={"location": "app.py-create_upload_file"})
        return {"message": "Got the files, will start Processing them Now!!!!"}

    except Exception as e:
        error_logger.error(msg="An Error Occurred at post request..", exc_info=e, extra={"location": "app.py-create_upload_file"})
        raise HTTPException(status_code=500, detail="An error occurred while processing the request.")

# @app.get("/createreport")
# async def create_powerbi_reports():
#     try:
        
#           pass
#     except Exception as e:
#         error_logger.error(msg="An Error Occured at get request..",exc_info=e,extra={"location":"App.py-create_upload_file"})
#         return {"message": "An Error Occured while collecting the files!!"}
          

# from pyngrok import ngrok  
 
# ngrok.set_auth_token("2al4KKug9Lj9a6NNZxArDX0BMNH_618BhSscx74HW56SR4RAM")
 
# public_url = ngrok.connect(8000)
# print(f"FastAPI application is accessible at: {public_url}")

if __name__ == "__main__":
    uvicorn.run(app)