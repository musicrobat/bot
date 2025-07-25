from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from datetime import datetime
import random
import jdatetime
import os

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

ADMINS = [123456789]
admin_list = set(ADMINS)
lotteries = {}
shabash_records = []

def get_main_menu(user_id):
    if user_id in admin_list:
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.row("🎯 مدیریت قرعه‌کشی", "🎲 اجرای قرعه‌کشی")
        kb.row("🗑 حذف قرعه‌کشی", "📊 مدیریت")
        kb.row("✨ ثبت شاباش", "📋 اعلام نتایج")
        kb.add("🔙 بازگشت")
        return kb
    else:
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("📋 اعلام آخرین قرعه‌کشی و شاباش")
        kb.add("📜 مشاهده تمام قرعه‌کشی‌ها")
        kb.add("🧾 مشاهده تمام شاباش‌ها")
        return kb

@dp.message_handler(lambda m: m.text == "📋 اعلام آخرین قرعه‌کشی و شاباش")
async def show_last_result(msg: types.Message):
    if not lotteries:
        await msg.answer("❌ هنوز قرعه‌کشی‌ای انجام نشده است.")
        return
    last_lottery = list(lotteries.items())[-1][1]
    winners = random.sample(last_lottery['participants'], min(len(last_lottery['participants']), 3))
    winners_text = "\n".join([f"🏆 {w}" for w in winners])
    related_shabash = [s for s in shabash_records if s['lottery_name'] == last_lottery['name']]
    shabash_text = ""
    if related_shabash:
        shabash_text = "\n📣 اعلام شاباش‌ها:\n"
        for s in related_shabash:
            shabash_text += f"از طرف {'آقا' if 'آقا' in s['sponsor_name'] else 'خانم'} {s['sponsor_name']} مبلغ {s['amount']} تومان به {'آقا' if 'آقا' in s['user'] else 'خانم'} {s['user']}\n"
    date_jalali = jdatetime.datetime.now().strftime("%Y/%m/%d")
    result = (
        f"📋 نتایج آخرین قرعه‌کشی:\n"
        f"🏷 نام چالش: {last_lottery['name']}\n"
        f"👤 گرداننده: {'، '.join(last_lottery['host'])}\n"
        f"📅 تاریخ: {date_jalali}\n\n"
        f"🏆 برندگان:\n{winners_text}\n"
        f"{shabash_text}"
    )
    await msg.answer(result)

@dp.message_handler(lambda m: m.text == "📜 مشاهده تمام قرعه‌کشی‌ها")
async def show_all_lotteries(msg: types.Message):
    if not lotteries:
        await msg.answer("❌ هیچ قرعه‌کشی‌ای ثبت نشده است.")
        return
    result = "📋 لیست قرعه‌کشی‌ها:\n"
    for name, data in lotteries.items():
        result += f"- {name} / گرداننده: {'، '.join(data['host'])}\n"
    await msg.answer(result)

@dp.message_handler(lambda m: m.text == "🧾 مشاهده تمام شاباش‌ها")
async def show_all_shabash(msg: types.Message):
    if not shabash_records:
        await msg.answer("📭 شاباشی ثبت نشده است.")
        return
    result = "📣 تمام شاباش‌ها:\n"
    for s in shabash_records:
        result += f"- چالش: {s['lottery_name']} / از طرف {s['sponsor_name']} مبلغ {s['amount']} به {s['user']}\n"
    await msg.answer(result)

@dp.message_handler(commands=['start'])
async def start_handler(msg: types.Message):
    kb = get_main_menu(msg.from_user.id)
    await msg.answer("به ربات خوش آمدید", reply_markup=kb)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
