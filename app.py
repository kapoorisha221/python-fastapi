import os
from fastapi import FastAPI, File, UploadFile
from typing import List
from config.config import *
import uvicorn

from main import Main  

app = FastAPI()

@app.post("/uploadfile/")
async def create_upload_file(files: List[UploadFile]):

    for file in files:
            print(f"filename :{file.filename}")
            print(LocalConfig().RAW_DATA_FOLDER)
            # file.save(os.path.join(LocalConfig().RAW_DATA_FOLDER, file.filename))
            with open(os.path.join(LocalConfig().RAW_DATA_FOLDER, file.filename), "wb") as f:
                f.write(await file.read())

    obj = Main()
    obj.audios_main()
    return {"filename": files[0].filename}

if __name__ == "__main__":
    uvicorn.run(app, port=8000)