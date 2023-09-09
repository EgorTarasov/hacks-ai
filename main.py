import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold
import pickle

from utils.settings import settings

from db.sql import SQLManager
from ml.pipeline import MLPipeLine
from ml.pipe import Text2Speech

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()
db = SQLManager()
bot = Bot(settings.tg_token, parse_mode=ParseMode.MARKDOWN)
ml = MLPipeLine(settings.ml_train, settings.ml_embeds)
tts = Text2Speech()

with open(settings.ml_embeds, "rb") as file:
    data = pickle.load(file)
    print(list(data.keys()))

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
        [types.KeyboardButton(text="Вывести мое аудио текстом")],
        [types.KeyboardButton(text="Озвучить ответ")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)

    if state.state == "train":
        if message.text not in train_series:
            await message.answer("Состав не найден")
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
            file_path = tts(errors[state.index])
            
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
        elif message.voice:
            state.index = 0
            logging.debug(message.voice)
            file_id = message.voice.file_id
            file = await bot.get_file(file_id)
            file_path = file.file_path

            await bot.download_file(file_path, f"data/{file.file_id}.mp3")
            state.voice_file = f"data/{file.file_id}.mp3"
            await message.answer("Обрабатываю запрос")
            errors, query = ml.get_errors(state.voice_file, state.train, index=state.index)
            state.response_one = errors[0]
            state.response_two = errors[1]
            state.response_three = errors[2]
            errors = [state.response_one, state.response_two, state.response_three]
            state.last_recognized_text = query
           
            
            await message.answer(errors[state.index], reply_markup=keyboard)
        else:
            await message.answer("Обрабатываю запрос")
            errors, query = ml.get_errors(message.text, state.train, index=state.index, useSpeachToText=False)
            state.last_recognized_text = query
            state.response_one = errors[0]
            state.response_two = errors[1]
            state.response_three = errors[2]
            errors = [state.response_one, state.response_two, state.response_three]
            await message.answer(errors[state.index], reply_markup=keyboard)
            
        db.update_users_state(state)
        # call api


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
