import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode

from keyboards import main_menu

BOT_TOKEN = "8744135035:AAEqm6n6BUqbDSJAw3t_AOBoEj_Hm0lf0tc"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Shaxsiy chatda va guruhda ishlaydi
@dp.message(CommandStart())
@dp.message(Command("jadval", "start", "menu"))
@dp.message(F.text.lower().contains("jadval"))
async def send_welcome(message: types.Message):
    await message.reply(
        "🏆 **Ravalliq Chempionati**\n\n"
        "Turnir jadvali, to'purarlar va o'yinlar taqvimini ko'rish uchun pastdagi tugmani bosing:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_menu
    )

async def main():
    logging.basicConfig(level=logging.INFO)
    print(">>> Bot ishga tushdi va xabarlarni kutyapti...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())