from django.db import models

class Condition(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.name

class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.name

class BodyType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.name

class FuelType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.name

class PriceRange(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.name

class CarContent(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    condition = models.ForeignKey(Condition, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    body_type = models.ForeignKey(BodyType, on_delete=models.CASCADE)
    fuel_type = models.ForeignKey(FuelType, on_delete=models.CASCADE)
    price_range = models.ForeignKey(PriceRange, on_delete=models.CASCADE)

    # фото
    photo1 = models.ImageField(upload_to="cars/photos/", blank=True, null=True)
    photo2 = models.ImageField(upload_to="cars/photos/", blank=True, null=True)
    photo3 = models.ImageField(upload_to="cars/photos/", blank=True, null=True)
    photo4 = models.ImageField(upload_to="cars/photos/", blank=True, null=True)
    photo5 = models.ImageField(upload_to="cars/photos/", blank=True, null=True)

    # видео
    video = models.FileField(upload_to="cars/videos/", blank=True, null=True)

    # владелец
    owner_username = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.condition}, {self.price_range})"
