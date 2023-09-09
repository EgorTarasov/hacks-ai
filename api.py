from fastapi import FastAPI, UploadFile, Depends, HTTPException,status, File, Query
from contextlib import asynccontextmanager
from ml.pipeline import MLPipeLine
from ml.pipe import Text2Speech
from utils.settings import settings
import uvicorn
import uuid
import logging
import sys

import pickle


ml: None | MLPipeLine = None #MLPipeLine(settings.ml_train, settings.ml_embeds)
tts: None | Text2Speech = None #Text2Speech()
with open(settings.ml_embeds, "rb") as file:
    data = pickle.load(file)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global ml, tts
    # Load the ML model
    ml = MLPipeLine(settings.ml_train, settings.ml_embeds)
    tts = Text2Speech()
    yield
    # Clean up the ML models and release the resources
    ml = None
    tts = None
    
    
app = FastAPI(
    title='mr Misister РЖД api',
    lifespan=lifespan
)

train_series = list(data.keys())

@app.post("/audio")
async def process_audio(
    data: bytes = File(..., media_type="audio/mpeg"),
    train_name: str = Query(..., max_length=256),
    ):
    if train_name not in train_series:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid train_name value")
    try:
        file_path = f"data/api-{str(uuid.uuid4())}.wav" 
        with open(file_path, "wb") as file:
            file.write(data)
        
        errors, query = ml.get_errors(file_path, train_name)
        logging.info(errors)
        return {
            "answer": list(errors),
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
        logging.info(errors)
        return {
            "answer": list(errors),
            "queryText": query
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/tts")
async def tts(
    text: str = "",
):
    if len(text) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="empty text")
    
    try:
        file_name = tts(text)
        return{
            "text": text,
            "file": file_name
        } 
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
            

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logging.info("starting fastapi")
    uvicorn.run("api:app", reload=True)