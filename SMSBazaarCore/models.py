import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


class Nonuser(models.Model):
    phone_number = models.CharField(max_length=200, primary_key=True)


class Scratch(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    amount = models.PositiveIntegerField()


class Item(models.Model):
    item_name = models.CharField(max_length=200, primary_key=True)
    description = models.CharField(max_length=200)
    upload = models.ImageField(upload_to='uploads/')
    city = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    price = models.PositiveIntegerField()
    vendor_ph_num = models.CharField(max_length=200)

    def __str__(self):
        return self.item_name + " | " + self.description + " | " + self.city + " | " + str(self.price)
