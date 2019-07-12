import json

from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='recv_msg')
    sender = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='sended_msg')
    date = models.fields.DateField(auto_now=True)
    msg = models.fields.CharField(max_length=512)
    type = models.fields.CharField(max_length=16)


class Dataset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='dataset')
    name = models.fields.CharField(max_length=255, unique=True)
    file = models.fields.FilePathField()
    algorithm = models.fields.CharField(max_length=255, null=True)
    config = models.fields.TextField(null=True, default={})
    result = models.fields.FilePathField(
        verbose_name="结果序列化文件")


class Photo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='photo')
    photo_url = models.fields.CharField(max_length=255, default='photo.jpg')
