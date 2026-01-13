import os
import asyncio
import re  # Бааларды иштетүү үчүн керек
from aiogram import Router, F, Bot
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    InputMediaPhoto, FSInputFile, BufferedInputFile,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
from asgiref.sync import sync_to_async
from car.models import CarContent, Condition, Color, BodyType, FuelType, PriceRange

router = Router()

# ================== Котормо сөздүгү (MAPPING) ==================
MAPPING = {
    "Новый": {"kg": "Жаңы", "en": "New"},
    "Б/У": {"kg": "Б/У", "en": "Used"},
    "Белый": {"kg": "Ак", "en": "White"},
    "Черный": {"kg": "Кара", "en": "Black"},
    "Серый": {"kg": "Боз", "en": "Grey"},
    "Серебристый": {"kg": "Күмүш түс", "en": "Silver"},
    "Синий": {"kg": "Көк", "en": "Blue"},
    "Красный": {"kg": "Кызыл", "en": "Red"},
    "Зеленый": {"kg": "Жашыл", "en": "Green"},
    "Желтый": {"kg": "Сары", "en": "Yellow"},
    "Коричневый": {"kg": "Күрөң", "en": "Brown"},
    "Оранжевый": {"kg": "Кызгылт сары", "en": "Orange"},
    "Фиолетовый": {"kg": "Сыя түс", "en": "Purple"},
    "Золотой": {"kg": "Алтын түс", "en": "Gold"},
    "Седан": {"kg": "Седан", "en": "Sedan"},
    "Хэтчбек": {"kg": "Хэтчбек", "en": "Hatchback"},
    "Универсал": {"kg": "Универсал", "en": "Station Wagon"},
    "Внедорожник (SUV)": {"kg": "Жол тандабас (SUV)", "en": "SUV"},
    "Кроссовер": {"kg": "Кроссовер", "en": "Crossover"},
    "Купе": {"kg": "Купе", "en": "Coupe"},
    "Кабриолет": {"kg": "Кабриолет", "en": "Convertible"},
    "Пикап": {"kg": "Пикап", "en": "Pickup"},
    "Минивэн": {"kg": "Минивэн", "en": "Minivan"},
    "Бензин": {"kg": "Бензин", "en": "Petrol"},
    "Дизель": {"kg": "Дизель", "en": "Diesel"},
    "Электро": {"kg": "Электр", "en": "Electric"},
    "Гибрид": {"kg": "Гибрид", "en": "Hybrid"},
    "Газ": {"kg": "Газ", "en": "Gas"},
}


def to_lang(text, lang):
    if lang == "ru": return text
    return MAPPING.get(text, {}).get(lang, text)


def from_lang(text):
    for ru_name, translations in MAPPING.items():
        if text in translations.values():
            return ru_name
    return text


# ================== Тексттердин топтому ==================
TEXTS = {
    "kg": {
        "start": "Тилди тандаңыз:",
        "condition": "Абалын тандаңыз:",
        "color": "Түсүн тандаңыз:",
        "body_type": "Кузовдун түрүн тандаңыз:",
        "fuel_type": "Күйүүчү майдын түрүн тандаңыз:",
        "price_range": "Баа диапазонун тандаңыз:",
        "not_found": "🚘 Машина табылган жок. Башкача издеп көрөсүзбү?",
        "search_done": "🔎 Издөө аяктады. Дагы издейсизби?",
        "restart": "🔄 Жаңыдан издөө",
        "change_lang": "🌐 Тилди өзгөртүү",
        "back": "⬅️ Артка",
        "recommendation": "💡 <b>Сизге сунушталган башка варианттар:</b>\n\n",
        "car_count": "Машина",
        "from": "ичинен",
        "no_desc": "Түшүндүрмөсү жок",
        "owner": "Ээси",
        "price_label": "Баасы",
        "color_label": "Түсү",
        "fuel_label": "Майлоочу май",
        "body_label": "Кузов",
        "cond_label": "Абалы"
    },
    "ru": {
        "start": "Выберите язык:",
        "condition": "Выберите состояние:",
        "color": "Выберите цвет:",
        "body_type": "Выберите тип кузова:",
        "fuel_type": "Выберите тип топлива:",
        "price_range": "Выберите ценовой диапазон:",
        "not_found": "🚘 Машин не найдено. Попробуете другой поиск?",
        "search_done": "🔎 Поиск завершён. Искать ещё?",
        "restart": "🔄 Начать заново",
        "change_lang": "🌐 Изменить язык",
        "back": "⬅️ Назад",
        "recommendation": "💡 <b>Другие подходящие варианты:</b>\n\n",
        "car_count": "Машина",
        "from": "из",
        "no_desc": "Без описания",
        "owner": "Владелец",
        "price_label": "Цена",
        "color_label": "Цвет",
        "fuel_label": "Топливо",
        "body_label": "Кузов",
        "cond_label": "Состояние"
    },
    "en": {
        "start": "Choose language:",
        "condition": "Choose condition:",
        "color": "Choose color:",
        "body_type": "Choose body type:",
        "fuel_type": "Choose fuel type:",
        "price_range": "Choose price range:",
        "not_found": "🚘 No cars found. Try another search?",
        "search_done": "🔎 Search finished. Search again?",
        "restart": "🔄 Start again",
        "change_lang": "🌐 Change language",
        "back": "⬅️ Back",
        "recommendation": "💡 <b>Other recommendations for you:</b>\n\n",
        "car_count": "Car",
        "from": "of",
        "no_desc": "No description",
        "owner": "Owner",
        "price_label": "Price",
        "color_label": "Color",
        "fuel_label": "Fuel",
        "body_label": "Body",
        "cond_label": "Condition"
    }
}

user_choices = {}
user_steps = {}
user_langs = {}

STEPS_CONFIG = [
    ("condition", Condition),
    ("color", Color),
    ("body_type", BodyType),
    ("fuel_type", FuelType),
    ("price_range", PriceRange),
]


# ================== UI Helpers ==================
def get_lang_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Кыргызча 🇰🇬"), KeyboardButton(text="Русский 🇷🇺")],
            [KeyboardButton(text="English 🇺🇸")]
        ],
        resize_keyboard=True
    )


def make_step_keyboard(items, lang, step_index, row_width=2):
    keyboard = []
    row = []
    for i, item in enumerate(items, start=1):
        row.append(KeyboardButton(text=item))
        if i % row_width == 0:
            keyboard.append(row)
            row = []
    if row: keyboard.append(row)
    controls = []
    if step_index > 0:
        controls.append(KeyboardButton(text=TEXTS[lang]["back"]))
    controls.append(KeyboardButton(text=TEXTS[lang]["change_lang"]))
    keyboard.append(controls)
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_restart_keyboard(lang):
    buttons = [[InlineKeyboardButton(text=TEXTS[lang]["restart"], callback_data="restart_search")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ================== Handlers ==================

@router.message(F.text == "/start")
@router.message(F.text.in_([TEXTS["kg"]["change_lang"], TEXTS["ru"]["change_lang"], TEXTS["en"]["change_lang"]]))
async def start_cmd(message: Message):
    await message.answer("Выберите язык / Тилди тандаңыз / Choose language:", reply_markup=get_lang_keyboard())


@router.message(F.text.in_(["Кыргызча 🇰🇬", "Русский 🇷🇺", "English 🇺🇸"]))
async def set_language(message: Message):
    user_id = message.from_user.id
    lang = "kg" if "Кыргызча" in message.text else "ru" if "Русский" in message.text else "en"
    user_langs[user_id] = lang
    user_choices[user_id] = {}
    user_steps[user_id] = 0
    await ask_step(message, 0)


async def ask_step(message: Message, step_index: int):
    user_id = message.from_user.id
    lang = user_langs.get(user_id, "ru")
    key, model = STEPS_CONFIG[step_index]
    rows = await sync_to_async(lambda: list(model.objects.all()))()
    names = [to_lang(r.name, lang) for r in rows]
    question = TEXTS[lang][key]
    await message.answer(question, reply_markup=make_step_keyboard(names, lang, step_index))


@router.message()
async def handle_choice(message: Message, bot: Bot):
    user_id = message.from_user.id
    lang = user_langs.get(user_id, "ru")
    text = (message.text or "").strip()

    if user_id not in user_steps: return

    if text == TEXTS[lang]["back"]:
        if user_steps[user_id] > 0:
            user_steps[user_id] -= 1
            prev_key = STEPS_CONFIG[user_steps[user_id]][0]
            user_choices[user_id].pop(prev_key, None)
            await ask_step(message, user_steps[user_id])
            return

    step_index = user_steps[user_id]
    key, model = STEPS_CONFIG[step_index]
    original_name = from_lang(text)
    obj = await sync_to_async(lambda: model.objects.filter(name=original_name).first())()

    if not obj:
        if text != TEXTS[lang]["change_lang"]:
            await ask_step(message, step_index)
        return

    user_choices[user_id][key] = obj
    user_steps[user_id] += 1

    if user_steps[user_id] < len(STEPS_CONFIG):
        await ask_step(message, user_steps[user_id])
    else:
        await perform_search(message, bot, lang)


async def perform_search(message: Message, bot: Bot, lang: str):
    user_id = message.from_user.id
    # Тандалган бааны эстеп калабыз
    selected_price_obj = user_choices[user_id].get("price_range")

    try:
        cars = await orm_find_cars(user_choices[user_id])
        if not cars:
            await message.answer(TEXTS[lang]["not_found"], reply_markup=get_restart_keyboard(lang))
        else:
            for idx, car in enumerate(cars, start=1):
                # Эгер машина тандалган баа диапазонунда болбосо, сунуш экенин эскертебиз
                prefix = ""
                if car.price_range_id != selected_price_obj.id:
                    prefix = TEXTS[lang]["recommendation"]

                text_info = (
                    f"🚘 <b>{TEXTS[lang]['car_count']} {idx} {TEXTS[lang]['from']} {len(cars)}</b>\n\n"
                    f"{prefix}"
                    f"<b>{car.title}</b>\n"
                    f"{car.description or TEXTS[lang]['no_desc']}\n"
                    f"💰 {TEXTS[lang]['price_label']}: {car.price_range.name}\n"
                    f"⚙️ {TEXTS[lang]['body_label']}: {to_lang(car.body_type.name, lang)}\n"
                    f"🎨 {TEXTS[lang]['color_label']}: {to_lang(car.color.name, lang)}\n"
                    f"⛽ {TEXTS[lang]['fuel_label']}: {to_lang(car.fuel_type.name, lang)}\n"
                    f"📌 {TEXTS[lang]['cond_label']}: {to_lang(car.condition.name, lang)}\n"
                    f"👤 {TEXTS[lang]['owner']}: @{car.owner_username or '---'}"
                )

                media = []
                photo_fields = sorted([f.name for f in car._meta.fields if "photo" in f.name])
                for field_name in photo_fields:
                    photo_field = getattr(car, field_name)
                    if photo_field and hasattr(photo_field, 'path') and os.path.exists(photo_field.path):
                        try:
                            with open(photo_field.path, 'rb') as f:
                                file_data = f.read()
                                media.append(InputMediaPhoto(
                                    media=BufferedInputFile(file_data, filename=f"p{idx}_{field_name}.jpg"),
                                    caption=text_info if not media else None,
                                    parse_mode="HTML"
                                ))
                        except:
                            continue

                if not media:
                    await message.answer(text_info, parse_mode="HTML")
                elif len(media) == 1:
                    await bot.send_photo(message.chat.id, photo=media[0].media, caption=text_info, parse_mode="HTML")
                else:
                    await bot.send_media_group(message.chat.id, media=media[:10])

                if car.video and hasattr(car.video, 'path') and os.path.exists(car.video.path):
                    await asyncio.sleep(0.5)
                    try:
                        await bot.send_video(message.chat.id, FSInputFile(car.video.path))
                    except:
                        pass

            await message.answer(TEXTS[lang]["search_done"], reply_markup=get_restart_keyboard(lang))
    except Exception as e:
        await message.answer(f"⚠️ Error: {e}")

    user_choices.pop(user_id, None)
    user_steps.pop(user_id, None)


@router.callback_query(F.data == "restart_search")
async def restart_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_choices[user_id] = {}
    user_steps[user_id] = 0
    await callback.answer()
    await ask_step(callback.message, 0)


# ================== Фильтрация логикасы ==================

def extract_min_price(price_string):
    """Тексттен эң кичине санды бөлүп алуу (мис: '15000$ - 20000$' -> 15000)"""
    nums = re.findall(r'\d+', price_string)
    return int(nums[0]) if nums else 0


@sync_to_async
def orm_find_cars(choices: dict):
    price_obj = choices.get("price_range")
    if not price_obj: return []

    # 1. Тандалган баадагы машиналарды табуу (Биринчи кезекте булар чыгат)
    exact_cars = list(CarContent.objects.select_related(
        "condition", "color", "body_type", "fuel_type", "price_range"
    ).filter(price_range_id=price_obj.id))

    # 2. Башка бардык машиналарды алуу
    other_cars = list(CarContent.objects.select_related(
        "condition", "color", "body_type", "fuel_type", "price_range"
    ).exclude(price_range_id=price_obj.id))

    # 3. Башка машиналарды баасы боюнча сорттойбуз (Кымбатынан арзанына)
    # Сорттоо үчүн тексттен бааны бөлүп алуу функциясын колдонобуз
    other_cars.sort(key=lambda x: extract_min_price(x.price_range.name), reverse=True)

    # Эки тизмени бириктиребиз
    return exact_cars + other_cars