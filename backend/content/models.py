from django.db import models

# Create your models here.


class Content(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title


class Link(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()
    content = models.ForeignKey(
        Content, on_delete=models.CASCADE, related_name='links')

    def __str__(self):
        return self.name
