import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.enums import ChatType
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = "8744135035:AAEqm6n6BUqbDSJAw3t_AOBoEj_Hm0lf0tc"
MINI_APP_URL = "https://javokhir7.github.io/football_bot/?v=3"

# Sizning shaxsiy Telegram ID raqamingiz:
ADMIN_ID = 314323733

# Kirgan foydalanuvchilar ro'yxati
active_users = {}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 1. Guruhda start bosilsa, jim turadi va ortiqcha xabarni o'chiradi
@dp.message(F.chat.type.in_([ChatType.GROUP, ChatType.SUPERGROUP]))
async def block_group(message: types.Message):
    if message.text and message.text.startswith("/start"):
        try:
            await message.delete()
        except Exception:
            pass
    return

# 2. Shaxsiyda /start bosilganda
@dp.message(CommandStart(), F.chat.type == ChatType.PRIVATE)
async def private_start(message: types.Message):
    user = message.from_user
    user_id = user.id
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    username = f"@{user.username}" if user.username else "yo'q"

    # Yangi foydalanuvchi bo'lsa, sizga xabar yuboradi
    is_new = user_id not in active_users
    active_users[user_id] = {"name": full_name, "username": username}

    if is_new and user_id != ADMIN_ID:
        admin_alert = (
            f"🚨 <b>Yangi foydalanuvchi kirdi!</b>\n\n"
            f"👤 <b>Ism:</b> {full_name}\n"
            f"🔗 <b>Username:</b> {username}\n"
            f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
            f"📊 <b>Jami foydalanuvchilar:</b> {len(active_users)}"
        )
        try:
            await bot.send_message(chat_id=ADMIN_ID, text=admin_alert, parse_mode="HTML")
        except Exception:
            pass

    # Foydalanuvchiga ochiladigan menyu
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
        "Turnir jadvali, to'purarlar va o'yinlar taqvimini ko'rish uchun pastdagi tugmani bosing:"
    )
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

# 3. Faqat sizga kirganlar ro'yxatini ko'rsatuvchi buyruq (/users)
@dp.message(Command("users"), F.chat.type == ChatType.PRIVATE)
async def list_users(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    if not active_users:
        await message.answer("Hozircha hech kim kirmadi.")
        return

    report = f"👥 <b>Jami kirganlar soni:</b> {len(active_users)}\n\n"
    for idx, (uid, data) in enumerate(active_users.items(), 1):
        report += f"{idx}. {data['name']} ({data['username']}) - <code>{uid}</code>\n"

    await message.answer(report, parse_mode="HTML")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
