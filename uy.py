from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import TOKEN, ADMINS, CHANNEL_ID

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Holatlarni belgilash
class AdState(StatesGroup):
    waiting_for_ad = State()

# Start komandasi
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("📋 E’lonlarni ko‘rish"),
        KeyboardButton("📞 Admin bilan bog‘lanish"),
        KeyboardButton("📝 E’lon yuborish")
    )
    await message.answer("Xush kelibsiz! Quyidagilardan birini tanlang:", reply_markup=kb)

# Kanalga olib o‘tish
@dp.message_handler(lambda msg: msg.text == "📋 E’lonlarni ko‘rish")
async def show_ads(message: types.Message):
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("📲 Kanalga o‘tish", url="https://t.me/tezkoruy"))
    await message.answer("E’lonlarimizni quyidagi kanalimizda ko‘rishingiz mumkin:", reply_markup=kb)

# Adminlar bilan bog‘lanish
@dp.message_handler(lambda msg: msg.text == "📞 Admin bilan bog‘lanish")
async def contact_admins(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("1️⃣ @TEZKORUY_Admin", url="https://t.me/TEZKORUY_Admin"),
        InlineKeyboardButton("2️⃣ @AXI5757", url="https://t.me/AXI5757")
    )
    await message.answer("Adminlardan biriga yozishingiz mumkin:", reply_markup=kb)

# E’lon yuborish boshlanishi
@dp.message_handler(lambda msg: msg.text == "📝 E’lon yuborish")
async def start_ad(message: types.Message):
    await message.answer("""шундай малумотлар ёзинг✅

3та ёки 10тагача расм🖼️
🏢 Квартира ёки Ховли 
🏢 5-Этаж
🚪 (X)Ҳоналик (X) м² 
🪚 Эвро ремонт 
🔥 Газ, 💦 Сув, ⚡️свет бор 
🛋 Жиҳозлари билан 
📁 Ҳужжатлари жойида 
💵 Нарҳи 45.000$ келишамиз

☎️ +9989x.XXX.xx.xx 

📍Манзил:

«@tezkoruy» шу малумотларни жонатинг👆""")
    await AdState.waiting_for_ad.set()

# E’lonni qabul qilish
@dp.message_handler(content_types=['text', 'photo'], state=AdState.waiting_for_ad)
async def receive_ad(message: types.Message, state: FSMContext):
    await state.finish()

    # Inline tugmalar
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("✅ Qabul qilish", callback_data=f"accept|{message.from_user.id}"),
        InlineKeyboardButton("❌ Rad etish", callback_data=f"reject|{message.from_user.id}")
    )

    for admin_id in ADMINS:
        if message.photo:
            await bot.send_photo(admin_id, message.photo[-1].file_id, caption=message.caption or "Rasmli e’lon", reply_markup=kb)
        else:
            await bot.send_message(admin_id, f"E’lon:\n{message.text}", reply_markup=kb)

    await message.answer("E’loningiz adminlarga yuborildi. Tasdiqlangach kanalga chiqadi ✅")

# Admin tasdiqlashi
@dp.callback_query_handler(lambda call: call.data.startswith("accept|") or call.data.startswith("reject|"))
async def handle_decision(call: CallbackQuery):
    action, user_id = call.data.split("|")
    message = call.message

    if action == "accept":
        # E’lonni kanalga yuborish
        if message.photo:
            await bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption=message.caption or "Tasdiqlangan e’lon")
        else:
            await bot.send_message(CHANNEL_ID, message.text)

        await call.answer("E’lon kanalga yuborildi ✅")
    else:
        await call.answer("E’lon rad etildi ❌")

    await call.message.edit_reply_markup(reply_markup=None)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
