from aiogram import types, Dispatcher
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    InputMediaPhoto, InputFile
)
from asgiref.sync import sync_to_async
from car.models import CarContent, Condition, Color, BodyType, FuelType, PriceRange

# ================= Состояние пользователя =================
user_choices = {}
user_steps = {}

STEPS = [
    ("condition", Condition, "состояние"),
    ("color", Color, "цвет"),
    ("body_type", BodyType, "тип кузова"),
    ("fuel_type", FuelType, "тип топлива"),
    ("price_range", PriceRange, "ценовой диапазон"),
]

# ================= ORM Helpers =================
@sync_to_async
def orm_all(model):
    return list(model.objects.all())

@sync_to_async
def orm_get_by_name(model, name: str):
    return model.objects.filter(name=name).first()

@sync_to_async
def orm_find_cars(choices: dict):
    return list(
        CarContent.objects.select_related(
            "condition", "color", "body_type", "fuel_type", "price_range"
        ).filter(
            condition=choices["condition"],
            color=choices["color"],
            body_type=choices["body_type"],
            fuel_type=choices["fuel_type"],
            price_range=choices["price_range"],
        )
    )

# ================= UI Helpers =================
def make_keyboard(items, row_width=2):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    row = []
    for i, item in enumerate(items, start=1):
        row.append(KeyboardButton(item))
        if i % row_width == 0:
            kb.row(*row)
            row = []
    if row:
        kb.row(*row)
    return kb

async def ask_step(message: types.Message, step_index: int):
    key, model, human = STEPS[step_index]
    rows = await orm_all(model)
    names = [r.name for r in rows]
    await message.answer(f"Выберите {human}:", reply_markup=make_keyboard(names))

# ================= Handlers =================
def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start"])
    dp.register_message_handler(cancel, commands=["cancel"])
    dp.register_message_handler(handle_choice)

async def start(message: types.Message):
    user_id = message.from_user.id
    user_choices[user_id] = {}
    user_steps[user_id] = 0
    await ask_step(message, 0)

async def cancel(message: types.Message):
    user_id = message.from_user.id
    user_choices.pop(user_id, None)
    user_steps.pop(user_id, None)
    await message.answer(
        "❌ Поиск отменён. Нажмите /start для нового поиска.",
        reply_markup=ReplyKeyboardRemove(),
    )

async def handle_choice(message: types.Message):
    user_id = message.from_user.id
    text = (message.text or "").strip()

    if user_id not in user_steps:
        user_choices[user_id] = {}
        user_steps[user_id] = 0

    step_index = user_steps[user_id]
    key, model, human = STEPS[step_index]

    obj = await orm_get_by_name(model, text)
    if not obj:
        await message.answer(f"❗ Нет варианта «{text}». Выберите {human} с клавиатуры.")
        await ask_step(message, step_index)
        return

    user_choices[user_id][key] = obj
    step_index += 1

    if step_index < len(STEPS):
        user_steps[user_id] = step_index
        await ask_step(message, step_index)
        return

    # ==== Поиск авто ====
    cars = await orm_find_cars(user_choices[user_id])
    if not cars:
        await message.answer("🚘 Машин с такими параметрами пока нет.", reply_markup=ReplyKeyboardRemove())
    else:
        for car in cars:
            # ---- Фото ----
            photos = [getattr(car, f"photo{i}") for i in range(1, 6) if getattr(car, f"photo{i}")]
            try:
                if len(photos) == 1:
                    await message.answer_photo(InputFile(photos[0].path))
                elif len(photos) > 1:
                    media = [InputMediaPhoto(media=InputFile(p.path)) for p in photos[:10]]
                    await message.answer_media_group(media)
            except Exception as e:
                await message.answer(f"⚠️ Ошибка при отправке фото {car.title}: {e}")

            # ---- Видео ----
            if car.video:
                await message.answer_video(InputFile(car.video.path))

            # ---- Текст ----
            text_info = (
                f"🚘 {car.title}\n"
                f"{car.description or 'Без описания'}\n"
                f"💰 Цена: {car.price_range}\n"
                f"⚙️ Кузов: {car.body_type}\n"
                f"🎨 Цвет: {car.color}\n"
                f"⛽ Топливо: {car.fuel_type}\n"
                f"📌 Состояние: {car.condition}\n"
                f"👤 Владелец: {car.owner_username or 'Не указан'}"
            )
            await message.answer(text_info)

    # ---- Сброс ----
    user_choices.pop(user_id, None)
    user_steps.pop(user_id, None)
    await message.answer(
        "🔎 Поиск завершён. Нажмите /start для нового поиска.",
        reply_markup=ReplyKeyboardRemove(),
    )
