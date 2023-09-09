from fastapi import FastAPI, UploadFile, Depends, HTTPException,status, Query
from ml.pipeline import MLPipeLine
from ml.pipe import Text2Speech
from utils.settings import settings
import uvicorn
import uuid
import logging
import sys

import pickle

app = FastAPI(
    title='mr Misister РЖД api'
)
ml = MLPipeLine(settings.ml_train, settings.ml_embeds)
tts = Text2Speech()
with open(settings.ml_embeds, "rb") as file:
    data = pickle.load(file)


train_series = list(data.keys())

@app.post("/audio")
async def process_audio(
    audio_file: UploadFile,
    train_name: str = Query(..., max_length=256),
    
    ):
    if train_name not in train_series:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid train_name value")
    try:
        file_path = f"data/api-{str(uuid.uuid4())}.wav" 
        with open(file_path, "wb") as file:
            file.write(audio_file)
        
        errors, query = ml.get_errors(file_path, train_name)
        return {
            "answer": errors,
            "queryText": query
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/text")
async def process_text(
    text_query: str= Query(..., max_length=2048),
    train_name: str = Query(..., max_length=256),
):
    if train_name not in train_series:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid train_name value")
    try:

        
        errors, query = ml.get_errors(text_query, train_name, useSpeachToText=False)
        return {
            "answer": errors,
            "queryText": query
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logging.info("starting fastapi")
    uvicorn.run("api:app", reload=True)