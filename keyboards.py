from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

APP_DIRECT_URL = "https://t.me/ravalliq_bot/ravalliq"

main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🏆 Chempionat jadvalini ochish",
                url=APP_DIRECT_URL
            )
        ]
    ]
)