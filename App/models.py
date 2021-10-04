from django.db import models
# Create your models here.
from mongoengine import Document, fields


class Blogs(Document):
    name = fields.StringField()
    topic = fields.StringField()
    date = fields.DateTimeField()
    addition_info = fields.DictField()


class MongoModel(models.Model):
    title = models.CharField(max_length=70, blank=False, default='')
    description = models.CharField(max_length=200, blank=False, default='')
    published = models.BooleanField(default=False)
