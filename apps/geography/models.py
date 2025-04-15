# geography/models.py

from django.db import models



class Region(models.Model):
    region_name = models.CharField(max_length=45)

    def __str__(self):
        return self.region_name

class City(models.Model):
    name = models.CharField(max_length=45)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='cities')

    def __str__(self):
        return self.name


class Site(models.Model):
    name = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.city.name})"

