import asyncio
import logging
import sys
from os import getenv
import requests

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold
import pickle

from utils.settings import settings

from db.sql import SQLManager


class Api:
    def __init__(self, api_host: str = "127.0.0.1", api_port: int = 8000) -> None:
        self.base_url = f"http://{api_host}:{api_port}"
        
    async def process_audio(self, train_type: str, file_path: str):
        response = requests.post(
            self.base_url+'/audio',
            params={
                "train_name": train_type
            },\
            headers={
                    'accept': 'application/json',
                },
            files={
                "data":open(file_path, "rb")
            }
        )
        if response.status_code == 422: 
            return  "None", "None"
        
        
        response = response.json()
        return response["answer"], response["queryText"]
    async def process_text(self, train_type: str, query: str) -> tuple[str, str]:
        response = requests.post(
            self.base_url+"/text", params={
                "text_query": query,
                "train_name": train_type
            }
        )
        if response.status_code == 422: 
            return  "None", "None"
        
        response = response.json()
        return response["answer"], response["queryText"]
    
    async def text_to_speech(self, text: str):
        response = requests.post(
            self.base_url + "/tts",
            params={
                "text": text
            }
        )
        data= response.json()
        print(data)
        return data["file"]
        

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()
db = SQLManager()
api = Api()
bot = Bot(settings.tg_token, parse_mode=ParseMode.MARKDOWN)

with open(settings.ml_embeds, "rb") as file:
    data = pickle.load(file)


train_series = list(data.keys())


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    if message.from_user:
        db.save_user(message.from_user)

    await message.answer(f"Введите серию поезда: ")



@dp.message()
async def handler(message: types.Message) -> None:
    state = db.get_users_state(message.from_user.id)
    logging.debug(message.text)
    logging.debug(state)
    kb = [
        [types.KeyboardButton(text="Далее"), types.KeyboardButton(text="Заново")],
        # [types.KeyboardButton(text="Вывести мое аудио текстом")],
        [types.KeyboardButton(text="Озвучить ответ")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)

    if state.state == "train":
        if message.text not in train_series:
            await message.answer("Состав не найден")
        elif message.text == "Заново":
            await message.answer(f"Введите серию поезда: ")
        else:
            state.train = message.text
            state.state = "voice"
            db.update_users_state(state)
            await message.answer(
                "Серия найдена! Пожалуйста, расскажите о неисправности с помощью голосового (до 30 секунд) или текстового сообщения"
            )
    elif state.state == "voice":
        logging.debug(message)
        
        if message.text == "Вывести мое аудио текстом":
            
            await message.answer(state.last_recognized_text)
        elif message.text == "Озвучить ответ":
            errors = [state.response_one, state.response_two, state.response_three]
            
            file_path = await api.text_to_speech(errors[state.index])
            
            await message.answer(errors[state.index], reply_markup=keyboard)
            await message.reply_document(types.FSInputFile(path=file_path, filename="foo.wav"))
            
        elif message.text == "Далее":
            if state.index < 2:
                state.index = state.index + 1
            else: 
                state.index = 0
            errors = [state.response_one, state.response_two, state.response_three]
            await message.answer(errors[state.index], reply_markup=keyboard)
        elif message.text == "Заново":
            state.state = "train"
            await message.answer(f"Введите серию поезда: ")
        if message.voice:
            state.index = 0
            logging.debug(message.voice)
            file_id = message.voice.file_id
            file = await bot.get_file(file_id)
            file_path = file.file_path
            logging.debug(file_path)
            await bot.download_file(file_path, f"data/{file.file_id}.mp3", timeout=30)
            state.voice_file = f"data/{file.file_id}.mp3"
            await message.answer(f"Обрабатываю запрос {state.train} {state.voice_file}")
            
            errors, query = await api.process_audio(state.train, state.voice_file)
            state.response_one, state.response_two,  state.response_three= errors
            
            state.last_recognized_text = query
            logging.info(type(state.response_one))
            await message.answer(state.response_one, reply_markup=keyboard)
        elif len(message.text) > 10 and message.text != "Озвучить ответ" and message.text != "Вывести мое аудио текстом" and message.text != "Заново":
            
            await message.answer("Обрабатываю запрос")
            
            #errors, query = ml.get_errors(message.text, state.train, index=state.index, useSpeachToText=False)
            errors, query = await api.process_text(query=message.text, train_type=state.train)
            state.last_recognized_text = query
            state.response_one, state.response_two,  state.response_three= errors
            errors = [state.response_one, state.response_two, state.response_three]
            await message.answer(state.response_one, reply_markup=keyboard)
            
        db.update_users_state(state)
        # call api


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
