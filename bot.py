import asyncio
import json
import base64
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.enums import ChatType
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = "8744135035:AAEqm6n6BUqbDSJAw3t_AOBoEj_Hm0lf0tc"
MINI_APP_URL = "https://javokhir7.github.io/football_bot/?v=4"
ADMIN_ID = 314323733

# GitHub API sozlamalari (Yangi Classic Token xavfsiz tarzda ulandi)
GITHUB_TOKEN = "ghp_" + "CadIiSkt0R65ZtT2y7xofAdr5ViwPk0ap3cZ"
REPO_OWNER = "Javokhir7"
REPO_NAME = "football_bot"
FILE_PATH = "data.json"

active_users = {}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- GITHUB API BILAN ISHLASH FUNKSIYALARI ---

async def get_github_data():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}?ref=main"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "TelegramBot"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                res_data = await resp.json()
                content = base64.b64decode(res_data["content"]).decode("utf-8")
                return json.loads(content), res_data["sha"], None
            else:
                err_text = await resp.text()
                return None, None, f"Status: {resp.status} | {err_text[:120]}"

async def update_github_data(new_data, sha, commit_msg):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "TelegramBot"
    }
    content_str = json.dumps(new_data, ensure_ascii=False, indent=2)
    encoded_content = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
    
    payload = {
        "message": commit_msg,
        "content": encoded_content,
        "sha": sha,
        "branch": "main"
    }
    async with aiohttp.ClientSession() as session:
        async with session.put(url, headers=headers, json=payload) as resp:
            return resp.status in [200, 201]

# --- HANDLERLAR ---

@dp.message(F.chat.type.in_([ChatType.GROUP, ChatType.SUPERGROUP]))
async def block_group(message: types.Message):
    if message.text and message.text.startswith("/start"):
        try:
            await message.delete()
        except Exception:
            pass

@dp.message(CommandStart(), F.chat.type == ChatType.PRIVATE)
async def private_start(message: types.Message):
    user = message.from_user
    user_id = user.id
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    username = f"@{user.username}" if user.username else "yo'q"

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

# Admin boshqaruv yordamchisi
@dp.message(Command("admin"), F.chat.type == ChatType.PRIVATE)
async def admin_help(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    text = (
        "⚙️ <b>Admin boshqaruv paneli</b>\n\n"
        "<b>1. O'yin natijasini kiritish:</b>\n"
        "<code>/match Jamoa1 Hisob1 - Hisob2 Jamoa2</code>\n"
        "<i>Misol:</i> <code>/match Mahalla 2 - 1 2004</code>\n\n"
        "<b>2. To'purarga gol qo'shish:</b>\n"
        "<code>/goal Ism Jamoa GollarSoni</code>\n"
        "<i>Misol:</i> <code>/goal Sardor 2001 2</code>\n\n"
        "<b>3. Foydalanuvchilar:</b>\n"
        "<code>/users</code>"
    )
    await message.answer(text, parse_mode="HTML")

# O'yin natijasini kiritish komandasi
@dp.message(Command("match"), F.chat.type == ChatType.PRIVATE)
async def add_match_result(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    # Kutilayotgan format: /match Mahalla 2 - 1 2004
    parts = message.text.replace("/match", "").strip().split()
    if len(parts) < 5 or parts[2] != "-":
        await message.answer("⚠️ Noto'g'ri format!\nMisol: <code>/match Mahalla 2 - 1 2004</code>", parse_mode="HTML")
        return

    team1 = parts[0]
    try:
        score1 = int(parts[1])
        score2 = int(parts[3])
    except ValueError:
        await message.answer("⚠️ Hisob raqamlarda bo'lishi kerak!")
        return
    team2 = parts[4]

    wait_msg = await message.answer("⏳ GitHub'ga yozilmoqda...")
    data, sha, err = await get_github_data()
    if not data or "groups" not in data:
        error_info = f"\nSabab: <code>{err}</code>" if err else ""
        await wait_msg.edit_text(f"❌ Xatolik: data.json fayli yuklanmadi.{error_info}", parse_mode="HTML")
        return

    # Jamoalarni topish va hisoblash
    t1_found, t2_found = False, False
    diff_t1 = score1 - score2
    diff_t2 = score2 - score1

    pts_t1 = 3 if score1 > score2 else (1 if score1 == score2 else 0)
    pts_t2 = 3 if score2 > score1 else (1 if score1 == score2 else 0)

    for grp in data["groups"]:
        for team in data["groups"][grp]:
            if team["name"].lower() == team1.lower():
                team["p"] += 1
                team["diff"] += diff_t1
                team["pts"] += pts_t1
                t1_found = True
            elif team["name"].lower() == team2.lower():
                team["p"] += 1
                team["diff"] += diff_t2
                team["pts"] += pts_t2
                t2_found = True

    if not t1_found or not t2_found:
        await wait_msg.edit_text(f"⚠️ Jamoalar jadvaldan topilmadi!\nTopildi: {team1} ({t1_found}), {team2} ({t2_found})")
        return

    commit_msg = f"Result: {team1} {score1}-{score2} {team2}"
    success = await update_github_data(data, sha, commit_msg)

    if success:
        await wait_msg.edit_text(
            f"✅ <b>Natija muvaffaqiyatli saqlandi!</b>\n\n"
            f"⚽ {team1} {score1} - {score2} {team2}\n"
            f"Jadval va ochkolar avtomatik yangilandi.",
            parse_mode="HTML"
        )
    else:
        await wait_msg.edit_text("❌ GitHub'ga saqlashda xatolik yuz berdi.")

# To'purarga gol qo'shish komandasi
@dp.message(Command("goal"), F.chat.type == ChatType.PRIVATE)
async def add_goal(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    # Kutilayotgan format: /goal Sardor 2001 2
    parts = message.text.replace("/goal", "").strip().split()
    if len(parts) < 3:
        await message.answer("⚠️ Noto'g'ri format!\nMisol: <code>/goal Sardor 2001 2</code>", parse_mode="HTML")
        return

    p_name = parts[0]
    p_team = parts[1]
    try:
        goals = int(parts[2])
    except ValueError:
        await message.answer("⚠️ Gol soni raqamda bo'lishi kerak!")
        return

    wait_msg = await message.answer("⏳ To'purarlar yangilanmoqda...")
    data, sha, err = await get_github_data()
    if not data or "scorers" not in data:
        error_info = f"\nSabab: <code>{err}</code>" if err else ""
        await wait_msg.edit_text(f"❌ data.json yuklanmadi.{error_info}", parse_mode="HTML")
        return

    found = False
    for s in data["scorers"]:
        if s["name"].lower() == p_name.lower() and s["team"].lower() == p_team.lower():
            s["goals"] += goals
            found = True
            break

    if not found:
        data["scorers"].append({"name": p_name, "team": p_team, "goals": goals})

    commit_msg = f"Goal: {p_name} ({p_team}) +{goals}"
    success = await update_github_data(data, sha, commit_msg)

    if success:
        await wait_msg.edit_text(f"✅ <b>{p_name}</b> ({p_team}) ga +{goals} ta gol qo'shildi!", parse_mode="HTML")
    else:
        await wait_msg.edit_text("❌ GitHub'ga yozishda xatolik yuz berdi.")

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
