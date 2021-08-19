import re
import requests
import json
from aiogram import Bot, Dispatcher, types, executor
from aiogram.bot.api import TelegramAPIServer
from aiogram.utils.parts import safe_split_text
from aiogram.utils.markdown import hcode
from config import TOKEN, WEBHOOK_PATH, WEBHOOK_URL

server = TelegramAPIServer.from_base("http://localhost:8081")
bot = Bot(token=TOKEN, parse_mode="HTML", server=server)
dp = Dispatcher(bot)



def check_url(url: str):
    r = re.findall(r'(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?', url)
    return bool(r)

@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.answer("Hi! Send me a url in this fomat: http(s)://example.com\nBot sends site content if it is in json format")

@dp.message_handler(content_types=types.ContentType.TEXT)
async def url(message: types.Message):
    url = message.text
    if not check_url(url):
        await message.answer("Wrong url!")
        return
    r = requests.get(url, stream=True)
    if r.headers.get("Content-Length"):
        if not int(r.headers['Content-Length']) < 100_000:
            await message.answer("Response content-length is too long")
            return
    if not r.headers['Content-Type']=="application/json":
        await message.answer("Response content-type is not in json format")
        return
    for i in safe_split_text(json.dumps(r.json(), indent=2)):
        await message.answer(hcode(i))


async def on_startup(*args):
    webhook_info = await dp.bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await dp.bot.set_webhook(WEBHOOK_URL)

executor.start_webhook(dp, webhook_path=WEBHOOK_PATH, on_startup=on_startup, host="localhost", port=3000)
