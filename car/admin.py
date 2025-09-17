from django.contrib import admin
from .models import CarContent, Condition, Color, BodyType, FuelType, PriceRange

@admin.register(CarContent)
class CarContentAdmin(admin.ModelAdmin):
    list_display = ("title", "condition", "color", "body_type", "fuel_type", "price_range")

admin.site.register(Condition)
admin.site.register(Color)
admin.site.register(BodyType)
admin.site.register(FuelType)
admin.site.register(PriceRange)
