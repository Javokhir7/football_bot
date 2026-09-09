import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.enums import ChatType
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = "8744135035:AAEqm6n6BUqbDSJAw3t_AOBoEj_Hm0lf0tc"
# Yangi ma'lumotlar keshda qolib ketmasligi uchun versiya belgisi qo'shildi
MINI_APP_URL = "https://bucolic-sable-54bbe2.netlify.app/?v=5"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 1. GURUHDA KIMDIR START BOSSA: Bot jim turadi va spam bo'lmasligi uchun yozuvni o'chiradi
@dp.message(F.chat.type.in_([ChatType.GROUP, ChatType.SUPERGROUP]))
async def block_group(message: types.Message):
    if message.text and message.text.startswith("/start"):
        try:
            await message.delete()
        except Exception:
            pass
    return

# 2. SHAXSIYDA START BOSILGANDA: Aynan o'sha tugmali xabarni chiqaradi
@dp.message(CommandStart(), F.chat.type == ChatType.PRIVATE)
async def private_start(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏆 Chempionat jadvalini ochish",
                    web_app=WebAppInfo(url=MINI_APP_URL)
                )
            ]
        ]
    )

    text = (
        "🏆 <b>Ravalliq Chempionati</b>\n\n"
        "Turnir jadvali, to'purarlar va o'yinlar taqvimi ko'rish uchun pastdagi tugmani bosing:"
    )

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
