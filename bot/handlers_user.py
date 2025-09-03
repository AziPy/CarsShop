from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto
from asgiref.sync import sync_to_async
from car.models import CarContent, CONDITION_CHOICES, COLOR_CHOICES, BODY_CHOICES, FUEL_CHOICES, PRICE_CHOICES

user_choices = {}

def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start"])
    dp.register_message_handler(handle_choice)  # теперь все выборы через текст

async def start(message: types.Message):
    user_choices[message.from_user.id] = {}

    # клавиатура для выбора состояния
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for key, label in CONDITION_CHOICES:
        keyboard.add(KeyboardButton(label))

    await message.answer("Выберите состояние автомобиля:", reply_markup=keyboard)


async def handle_choice(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    if user_id not in user_choices:
        user_choices[user_id] = {}

    # --- Шаг 1: состояние ---
    if text in [label for _, label in CONDITION_CHOICES]:
        # сохраняем выбор
        for key, label in CONDITION_CHOICES:
            if label == text:
                user_choices[user_id]["condition"] = key
        # клавиатура для цвета
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for key, label in COLOR_CHOICES:
            keyboard.add(KeyboardButton(label))
        await message.answer("Выберите цвет:", reply_markup=keyboard)
        return

    # --- Шаг 2: цвет ---
    if text in [label for _, label in COLOR_CHOICES]:
        for key, label in COLOR_CHOICES:
            if label == text:
                user_choices[user_id]["color"] = key
        # клавиатура для кузова
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for key, label in BODY_CHOICES:
            keyboard.add(KeyboardButton(label))
        await message.answer("Выберите кузов:", reply_markup=keyboard)
        return

    # --- Шаг 3: кузов ---
    if text in [label for _, label in BODY_CHOICES]:
        for key, label in BODY_CHOICES:
            if label == text:
                user_choices[user_id]["body_type"] = key
        # клавиатура для топлива
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for key, label in FUEL_CHOICES:
            keyboard.add(KeyboardButton(label))
        await message.answer("Выберите топливо:", reply_markup=keyboard)
        return

    # --- Шаг 4: топливо ---
    if text in [label for _, label in FUEL_CHOICES]:
        for key, label in FUEL_CHOICES:
            if label == text:
                user_choices[user_id]["fuel_type"] = key
        # клавиатура для цен
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for key, label in PRICE_CHOICES:
            keyboard.add(KeyboardButton(label))
        await message.answer("Выберите диапазон цен:", reply_markup=keyboard)
        return

    # --- Шаг 5: цена ---
    if text in [label for _, label in PRICE_CHOICES]:
        for key, label in PRICE_CHOICES:
            if label == text:
                user_choices[user_id]["price_range"] = key

        choices = user_choices[user_id]

        # Асинхронный вызов ORM
        cars = await sync_to_async(list)(
            CarContent.objects.filter(
                condition=choices["condition"],
                color=choices["color"],
                body_type=choices["body_type"],
                fuel_type=choices["fuel_type"],
                price_range=choices["price_range"]
            )
        )

        if cars:
            for car in cars:
                # --- Фото ---
                photos = [getattr(car, f"photo{i}").path for i in range(1, 6) if getattr(car, f"photo{i}")]
                if len(photos) > 1:
                    media = [InputMediaPhoto(open(p, "rb")) for p in photos]
                    await message.answer_media_group(media)
                elif len(photos) == 1:
                    with open(photos[0], "rb") as photo:
                        await message.answer_photo(photo)

                # --- Видео ---
                if car.video:
                    with open(car.video.path, "rb") as video:
                        await message.answer_video(video)

                # --- Текст ---
                text_info = (
                    f"🚘 {car.title}\n\n"
                    f"{car.description or 'Без описания'}\n\n"
                    f"💰 Цена: {car.get_price_range_display()}\n"
                    f"⚙️ Кузов: {car.get_body_type_display()}\n"
                    f"🎨 Цвет: {car.get_color_display()}\n"
                    f"⛽ Топливо: {car.get_fuel_type_display()}\n"
                    f"📌 Состояние: {car.get_condition_display()}\n"
                    f"👤 Владелец: {car.user}"
                )
                await message.answer(text_info)
        else:
            await message.answer("🚘 Машин с такими параметрами пока нет.")

        # Чистим выбор и убираем клавиатуру
        user_choices.pop(user_id, None)
        await message.answer("🔎 Поиск завершён. Введите /start для нового поиска.", reply_markup=types.ReplyKeyboardRemove())
