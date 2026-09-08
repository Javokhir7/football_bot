import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.enums import ChatType

BOT_TOKEN = "8744135035:AAEqm6n6BUqbDSJAw3t_AOBoEj_Hm0lf0tc"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 1. GURUHLARNI TO'LIQ BLOKLASH (Guruhda nima yozilishidan qat'i nazar bot jim turadi)
@dp.message(F.chat.type.in_([ChatType.GROUP, ChatType.SUPERGROUP]))
async def block_all_group_messages(message: types.Message):
    # Agar kimdir /start yozgan bo'lsa, xabarini guruhdan o'chirib tashlaydi (agar bot admin bo'lsa)
    if message.text and message.text.startswith("/start"):
        try:
            await message.delete()
        except Exception:
            pass
    return  # GURUHGA UMUMAN JAVOB YOZMAYDI!

# 2. FAQAT SHAXSIYDA ISHLAYDI (Botning lichkasida start bosilganda)
@dp.message(CommandStart(), F.chat.type == ChatType.PRIVATE)
async def private_start(message: types.Message):
    await message.answer(
        f"Assalomu alaykum, {message.from_user.first_name}!\n"
        "Ravalliq chempionati botiga xush kelibsiz. Turnir jadvali va o'yinlarni ko'rish uchun quyidagi tugmani bosing."
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
