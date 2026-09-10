import asyncio
import json
import base64
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.enums import ChatType
from aiogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    WebAppInfo, 
    BotCommand, 
    BotCommandScopeDefault, 
    BotCommandScopeChat
)

BOT_TOKEN = "8744135035:AAEqm6n6BUqbDSJAw3t_AOBoEj_Hm0lf0tc"
MINI_APP_URL = "https://javokhir7.github.io/football_bot/?v=7"

# Ikkala admin ID raqamlari
ADMIN_IDS = [314323733, 5394390497]

# GitHub API sozlamalari
GITHUB_TOKEN = "ghp_" + "CadIiSkt0R65ZtT2y7xofAdr5ViwPk0ap3cZ"
REPO_OWNER = "Javokhir7"
REPO_NAME = "football_bot"
FILE_PATH = "data.json"

active_users = {}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- GITHUB API BILAN ISHLASH ---

async def get_github_file(path=FILE_PATH):
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}?ref=main"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "RavalliqBot",
        "Cache-Control": "no-cache"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, headers=headers) as resp:
            if resp.status == 200:
                res = await resp.json()
                content = base64.b64decode(res["content"])
                return content, res["sha"], None
            err_text = await resp.text()
            return None, None, f"Status: {resp.status} | {err_text[:100]}"

async def update_github_file(content_bytes, sha, commit_msg, path=FILE_PATH):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "RavalliqBot"
    }
    encoded = base64.b64encode(content_bytes).decode("utf-8")
    payload = {
        "message": commit_msg,
        "content": encoded,
        "branch": "main"
    }
    if sha:
        payload["sha"] = sha

    async with aiohttp.ClientSession() as session:
        async with session.put(url, headers=headers, json=payload) as resp:
            return resp.status in [200, 201]

# --- KOMANDALAR MENYUSINI O'RNATISH ---

async def set_bot_commands(bot: Bot):
    # Oddiy foydalanuvchilar ko'radigan menyu
    user_commands = [
        BotCommand(command="start", description="🏆 Chempionat jadvalini ochish")
    ]
    await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())

    # Adminlar uchun to'liq menyu
    admin_commands = [
        BotCommand(command="start", description="🏆 Jadvalni ochish"),
        BotCommand(command="match", description="⚽ Guruh o'yini hisobini kiritish"),
        BotCommand(command="playoff", description="🏆 Play-off natijasini kiritish"),
        BotCommand(command="newday", description="📅 Yangi taqvim qo'shish"),
        BotCommand(command="goal", description="🎯 To'purarga gol qo'shish"),
        BotCommand(command="admin", description="⚙️ Boshqaruv qo'llanmasi"),
        BotCommand(command="admins", description="🛡 Adminlar ro'yxati"),
        BotCommand(command="users", description="👥 Foydalanuvchilar soni")
    ]
    for admin_id in ADMIN_IDS:
        try:
            await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=admin_id))
        except Exception:
            pass

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

    if is_new and user_id not in ADMIN_IDS:
        admin_alert = (
            f"🚨 <b>Yangi foydalanuvchi kirdi!</b>\n\n"
            f"👤 <b>Ism:</b> {full_name}\n"
            f"🔗 <b>Username:</b> {username}\n"
            f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
            f"📊 <b>Jami foydalanuvchilar:</b> {len(active_users)}"
        )
        for adm in ADMIN_IDS:
            try:
                await bot.send_message(chat_id=adm, text=admin_alert, parse_mode="HTML")
            except Exception:
                pass

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="🏆 Chempionat jadvalini ochish", web_app=WebAppInfo(url=MINI_APP_URL))
        ]]
    )
    text = (
        "🏆 <b>Ravalliq Chempionati</b>\n\n"
        "Turnir jadvali, to'purarlar va o'yinlar taqvimini ko'rish uchun pastdagi tugmani bosing:"
    )
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

@dp.message(Command("admin"), F.chat.type == ChatType.PRIVATE)
async def admin_help(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    text = (
        "⚙️ <b>Admin boshqaruv paneli</b>\n\n"
        "<b>1. Guruh o'yini hisobini kiritish:</b>\n"
        "<code>/match Mahalla 2 - 1 2004</code>\n"
        "<i>(Jadval ham, taqvimdagi vaqt ham avtomatik almashadi)</i>\n\n"
        "<b>2. Yangi o'yinlar taqvimini kiritish:</b>\n"
        "<code>/newday 13-Sentyabr (Yakshanba) | 1986 18:30 2005, Mahalla 19:10 2004</code>\n\n"
        "<b>3. Play-off o'yinini kiritish:</b>\n"
        "<code>/playoff r16 1 1994 3 - 1 1991</code>\n"
        "<i>(Bosqichlar: r16, qf, sf, f)</i>\n\n"
        "<b>4. MVP yangilash:</b>\n"
        "Botga yangi MVP rasmini yuboring va izohiga:\n"
        "<code>Ism Familiya | Jamoa | Tavsif</code> deb yozing.\n\n"
        "<b>5. To'purarga gol qo'shish:</b>\n"
        "<code>/goal Sardor 2001 2</code>\n\n"
        "<b>6. Adminlarni ko'rish:</b> <code>/admins</code>\n"
        "<b>7. Foydalanuvchilar:</b> <code>/users</code>"
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("admins"), F.chat.type == ChatType.PRIVATE)
async def list_admins(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    text = "🛡 <b>Botingiz adminlari:</b>\n\n"
    for idx, adm_id in enumerate(ADMIN_IDS, 1):
        try:
            chat = await bot.get_chat(adm_id)
            u_name = f"(@{chat.username})" if chat.username else ""
            text += f"{idx}. <b>{chat.full_name}</b> {u_name} — <code>{adm_id}</code>\n"
        except Exception:
            text += f"{idx}. ID: <code>{adm_id}</code>\n"
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("match"), F.chat.type == ChatType.PRIVATE)
async def add_match_result(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

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
    raw_data, sha, err = await get_github_file(FILE_PATH)
    if not raw_data:
        await wait_msg.edit_text(f"❌ data.json o'qilmadi: {err}")
        return
    data = json.loads(raw_data.decode("utf-8"))

    # 1. Turnir jadvalini yangilash
    t1_found, t2_found = False, False
    diff_t1 = score1 - score2
    diff_t2 = score2 - score1

    pts_t1 = 3 if score1 > score2 else (1 if score1 == score2 else 0)
    pts_t2 = 3 if score2 > score1 else (1 if score1 == score2 else 0)

    for grp in data.get("groups", {}).values():
        for team in grp:
            if team["name"].strip().lower() == team1.strip().lower():
                team["p"] += 1
                team["diff"] += diff_t1
                team["pts"] += pts_t1
                t1_found = True
            elif team["name"].strip().lower() == team2.strip().lower():
                team["p"] += 1
                team["diff"] += diff_t2
                team["pts"] += pts_t2
                t2_found = True

    if not t1_found or not t2_found:
        await wait_msg.edit_text(f"⚠️ Jamoalar jadvaldan topilmadi!\nTopildi: {team1} ({t1_found}), {team2} ({t2_found})")
        return

    # 2. O'yinlar taqvimini (matches) yangilash
    schedule_updated = False
    if "matches" in data:
        for day in data["matches"]:
            for m in day.get("list", []):
                cond1 = (m["t1"].strip().lower() == team1.strip().lower() and m["t2"].strip().lower() == team2.strip().lower())
                cond2 = (m["t1"].strip().lower() == team2.strip().lower() and m["t2"].strip().lower() == team1.strip().lower())
                if cond1:
                    m["time"] = f"{score1} - {score2}"
                    schedule_updated = True
                    break
                elif cond2:
                    m["time"] = f"{score2} - {score1}"
                    schedule_updated = True
                    break
            if schedule_updated:
                break

    commit_msg = f"Match: {team1} {score1}-{score2} {team2}"
    success = await update_github_file(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"), sha, commit_msg)

    if success:
        note = " (taqvimdagi o'yin vaqti ham yangilandi)" if schedule_updated else ""
        await wait_msg.edit_text(
            f"✅ <b>Natija muvaffaqiyatli saqlandi!</b>\n\n"
            f"⚽ {team1} {score1} - {score2} {team2}\n"
            f"Turnir jadvali va ochkolar avtomatik yangilandi{note}.",
            parse_mode="HTML"
        )
    else:
        await wait_msg.edit_text("❌ GitHub'ga saqlashda xatolik yuz berdi.")

@dp.message(Command("newday"), F.chat.type == ChatType.PRIVATE)
async def newday_handler(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        content = message.text.replace("/newday", "").strip()
        date_part, matches_part = content.split("|")
        date_str = date_part.strip()
        
        matches_list = []
        for m_str in matches_part.split(","):
            t1, time_str, t2 = m_str.strip().split()
            matches_list.append({"t1": t1, "t2": t2, "time": time_str})
    except Exception:
        await message.answer("⚠️ Format: <code>/newday 13-Sentyabr (Yakshanba) | 1986 18:30 2005, Mahalla 19:10 2004</code>", parse_mode="HTML")
        return

    wait_msg = await message.answer("⏳ Taqvimga qo'shilmoqda...")
    raw_data, sha, err = await get_github_file(FILE_PATH)
    if not raw_data:
        await wait_msg.edit_text(f"❌ Xatolik: {err}")
        return
    data = json.loads(raw_data.decode("utf-8"))

    if "matches" not in data:
        data["matches"] = []
    data["matches"].append({"date": date_str, "list": matches_list})

    success = await update_github_file(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"), sha, f"New schedule: {date_str}")
    if success:
        await wait_msg.edit_text(f"✅ <b>{date_str}</b> o'yinlar taqvimi muvaffaqiyatli qo'shildi!", parse_mode="HTML")
    else:
        await wait_msg.edit_text("❌ Saqlashda xatolik yuz berdi.")

@dp.message(Command("playoff"), F.chat.type == ChatType.PRIVATE)
async def playoff_handler(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    parts = message.text.replace("/playoff", "").strip().split()
    if len(parts) < 7 or parts[4] != "-":
        await message.answer("⚠️ Format: <code>/playoff r16 1 1994 3 - 1 1991</code>\n(Bosqichlar: r16, qf, sf, f)", parse_mode="HTML")
        return

    stage, idx_str, t1, s1, s2, t2 = parts[0].lower(), parts[1], parts[2], int(parts[3]), int(parts[5]), parts[6]
    match_idx = int(idx_str) - 1

    wait_msg = await message.answer("⏳ Play-off yangilanmoqda...")
    raw_data, sha, err = await get_github_file(FILE_PATH)
    if not raw_data:
        await wait_msg.edit_text(f"❌ Xatolik: {err}")
        return
    data = json.loads(raw_data.decode("utf-8"))

    if "playoff" not in data or stage not in data["playoff"]:
        await wait_msg.edit_text("❌ data.json ichida play-off bosqichi topilmadi.")
        return

    winner = t1 if s1 > s2 else t2
    data["playoff"][stage][match_idx] = {
        "t1": t1, "s1": str(s1),
        "t2": t2, "s2": str(s2),
        "winner": winner
    }

    # G'olibni keyingi bosqichga o'tkazish
    next_stage_map = {"r16": "qf", "qf": "sf", "sf": "f"}
    if stage in next_stage_map:
        next_stage = next_stage_map[stage]
        next_idx = match_idx // 2
        is_t1 = (match_idx % 2 == 0)
        
        target = data["playoff"][next_stage][next_idx]
        if is_t1:
            target["t1"] = winner
        else:
            target["t2"] = winner
    elif stage == "f":
        data["playoff"]["champion"] = winner

    success = await update_github_file(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"), sha, f"Playoff {stage} update")
    if success:
        await wait_msg.edit_text(f"✅ Play-off yangilandi!\n🏆 G'olib: <b>{winner}</b>", parse_mode="HTML")
    else:
        await wait_msg.edit_text("❌ Saqlashda xatolik yuz berdi.")

@dp.message(F.photo, F.chat.type == ChatType.PRIVATE)
async def mvp_photo_handler(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    caption = message.caption or ""
    if "|" not in caption:
        await message.answer("⚠️ MVP uchun rasm tagiga quyidagicha yozing:\n<code>Ism Familiya | Jamoa | Tavsif</code>", parse_mode="HTML")
        return

    c_parts = [p.strip() for p in caption.split("|")]
    name = c_parts[0]
    team = c_parts[1] if len(c_parts) > 1 else ""
    desc = c_parts[2] if len(c_parts) > 2 else "Turning eng yaxshi o'yinchisi"

    wait_msg = await message.answer("⏳ MVP rasmi yuklanmoqda...")

    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    img_bytes = await bot.download_file(file_info.file_path)

    # 1. mvp.jpg faylini GitHub'ga yuklash
    _, img_sha, _ = await get_github_file("mvp.jpg")
    await update_github_file(img_bytes.read(), img_sha, "Update MVP photo", "mvp.jpg")

    # 2. data.json faylida MVP ma'lumotlarini yangilash
    raw_data, json_sha, _ = await get_github_file(FILE_PATH)
    data = json.loads(raw_data.decode("utf-8"))
    data["mvp"] = {
        "title": desc,
        "name": name,
        "team": team,
        "image": "mvp.jpg"
    }
    await update_github_file(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"), json_sha, f"Update MVP: {name}")
    await wait_msg.edit_text(f"✅ <b>Yangi MVP o'rnatildi:</b>\n👤 {name} ({team})", parse_mode="HTML")

@dp.message(Command("goal"), F.chat.type == ChatType.PRIVATE)
async def add_goal(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

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
    raw_data, sha, err = await get_github_file(FILE_PATH)
    if not raw_data:
        await wait_msg.edit_text(f"❌ data.json yuklanmadi: {err}", parse_mode="HTML")
        return
    data = json.loads(raw_data.decode("utf-8"))

    found = False
    for s in data.get("scorers", []):
        if s["name"].strip().lower() == p_name.strip().lower() and s["team"].strip().lower() == p_team.strip().lower():
            s["goals"] += goals
            found = True
            break

    if not found:
        data.setdefault("scorers", []).append({"name": p_name, "team": p_team, "goals": goals})

    commit_msg = f"Goal: {p_name} ({p_team}) +{goals}"
    success = await update_github_file(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"), sha, commit_msg)

    if success:
        await wait_msg.edit_text(f"✅ <b>{p_name}</b> ({p_team}) ga +{goals} ta gol qo'shildi!", parse_mode="HTML")
    else:
        await wait_msg.edit_text("❌ GitHub'ga yozishda xatolik yuz berdi.")

@dp.message(Command("users"), F.chat.type == ChatType.PRIVATE)
async def list_users(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    if not active_users:
        await message.answer("Hozircha hech kim kirmadi.")
        return

    report = f"👥 <b>Jami kirganlar soni:</b> {len(active_users)}\n\n"
    for idx, (uid, data) in enumerate(active_users.items(), 1):
        report += f"{idx}. {data['name']} ({data['username']}) - <code>{uid}</code>\n"

    await message.answer(report, parse_mode="HTML")

async def main():
    await set_bot_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
