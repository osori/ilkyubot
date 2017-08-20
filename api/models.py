from django.db import models

# Create your models here.
class User(models.Model):
	user_text = models.CharField(max_length=100)

class Input(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	input_text = models.CharField(max_length=100)