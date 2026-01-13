from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Condition, Color, BodyType, FuelType, PriceRange

@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    if sender.name != "car":
        return

    defaults = {
        Condition: [
            {"ru": "Новый", "kg": "Жаңы", "en": "New"},
            {"ru": "Б/У", "kg": "Б/У", "en": "Used"},
        ],
        Color: [
            {"ru": "Белый", "kg": "Ак", "en": "White"},
            {"ru": "Черный", "kg": "Кара", "en": "Black"},
            {"ru": "Серый", "kg": "Боз", "en": "Grey"},
            {"ru": "Серебристый", "kg": "Күмүш түс", "en": "Silver"},
            {"ru": "Синий", "kg": "Көк", "en": "Blue"},
            {"ru": "Красный", "kg": "Кызыл", "en": "Red"},
        ],
        BodyType: [
            {"ru": "Седан", "kg": "Седан", "en": "Sedan"},
            {"ru": "Хэтчбек", "kg": "Хэтчбек", "en": "Hatchback"},
            {"ru": "Универсал", "kg": "Универсал", "en": "Station Wagon"},
            {"ru": "Внедорожник (SUV)", "kg": "Жол тандабас", "en": "SUV"},
        ],
        FuelType: [
            {"ru": "Бензин", "kg": "Бензин", "en": "Petrol"},
            {"ru": "Дизель", "kg": "Дизель", "en": "Diesel"},
            {"ru": "Электро", "kg": "Электр", "en": "Electric"},
            {"ru": "Гибрид", "kg": "Гибрид", "en": "Hybrid"},
        ],
        PriceRange: [
            {"ru": "5000$ - 10000$", "kg": "5000$ - 10000$", "en": "5000$ - 10000$"},
            {"ru": "10000$ - 15000$", "kg": "10000$ - 15000$", "en": "10000$ - 15000$"},
            {"ru": "15000$ - 20000$", "kg": "15000$ - 20000$", "en": "15000$ - 20000$"},
        ],
    }

    for model, items in defaults.items():
        for item in items:
            # Маалыматты жаңыртуу же кошуу
            model.objects.get_or_create(
                name_ru=item["ru"],
                defaults={
                    "name_kg": item["kg"],
                    "name_en": item["en"],
                    "name": item["ru"] # Эски талаа үчүн
                }
            )