import logging
from aiogram import Bot, Dispatcher, executor, types
import openai
import os

API_TOKEN = os.getenv('API_TOKEN')  # Telegram bot token
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # OpenAI API key

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

openai.api_key = OPENAI_API_KEY

USER_LIMIT = 5
user_requests = {}

WELCOME_TEXT = (
    "Привет! Я ContentPalAI — бот для генерации контента.\n"
    "Отправь тему, и я помогу создать пост, заголовок, хештеги и идеи для соцсетей.\n"
    "У тебя есть 5 бесплатных запросов в день."
)

async def check_limit(user_id):
    count = user_requests.get(user_id, 0)
    if count >= USER_LIMIT:
        return False
    user_requests[user_id] = count + 1
    return True

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply(WELCOME_TEXT)

@dp.message_handler()
async def generate_content(message: types.Message):
    user_id = message.from_user.id
    if not await check_limit(user_id):
        await message.reply("Ты превысил лимит бесплатных запросов на сегодня. Попробуй завтра или свяжись с владельцем бота.")
        return

    prompt = (
        "Ты — профессиональный копирайтер. "
        "Создай короткий, цепляющий пост для соцсетей по теме:\n"
        f"{message.text}\n\n"
        "Пост должен быть привлекательным и лаконичным."
    )

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7,
        )
        text = response.choices[0].text.strip()
        await message.reply(text)
    except Exception as e:
        await message.reply("Произошла ошибка при генерации текста, попробуй позже.")
        logging.error(f"OpenAI error: {e}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
