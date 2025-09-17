from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Condition, Color, BodyType, FuelType, PriceRange

@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    if sender.name != "car":
        return

    defaults = {
        Condition: ["Новый", "Б/У"],
        Color: ["Белый", "Черный", "Серый", "Серебристый", "Синий",
                "Красный", "Зеленый", "Желтый", "Коричневый", "Оранжевый",
                "Фиолетовый", "Золотой"],
        BodyType: ["Седан", "Хэтчбек", "Универсал", "Внедорожник (SUV)",
                   "Кроссовер", "Купе", "Кабриолет", "Пикап", "Минивэн"],
        FuelType: ["Бензин", "Дизель", "Электро", "Гибрид", "Газ"],
        PriceRange: ["5000$ - 10000$", "10000$ - 15000$", "15000$ - 20000$",
                     "20000$ - 25000$", "25000$ - 30000$", "30000$ - 35000$",
                     "35000$ - 40000$", "40000$ - 45000$", "45000$ - 50000$",
                     "50000$ - 60000$"],
    }

    for model, items in defaults.items():
        for name in items:
            model.objects.get_or_create(name=name)
