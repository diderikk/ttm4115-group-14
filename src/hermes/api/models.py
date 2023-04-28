from uuid import uuid4
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager, GroupManager, TaskManager, DeliveryManager, NotificationManager



class Group(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
	number = models.IntegerField(unique=True)
 
	REQUIRED_FIELDS = ['number']
 
	objects = GroupManager()
 
	def __str__(self):
		return self.number


class Task(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
	title = models.CharField(max_length=64, null=False)
	description = models.CharField(max_length=1024, null=False)
	unit = models.IntegerField(null=False)
 
	REQUIRED_FIELDS = ['title', 'description', 'unit']
 
	class Meta:
		unique_together = [('title', 'uuid')]
	
 
	objects = TaskManager()
 
	def __str__(self):
		return f'Unit {unit}: {title}'

class Delivery(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
	file = models.FileField(upload_to="deliveries/")
	group = models.ForeignKey(Group, on_delete=models.CASCADE)
	task = models.ForeignKey(Task, on_delete=models.CASCADE)
  
	objects = DeliveryManager()
  
	def __str__(self):
		return f'{uuid}'
 
class User(AbstractBaseUser):
	uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
	email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
	is_admin = models.BooleanField(default=False)
	salt = models.CharField(max_length=64)
	password = models.CharField(max_length=256)
	group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['password']

	objects = UserManager()

	def __str__(self):
			return self.email
 
	def get_user_id(self):
		return str(self.id)

	@property
	def is_staff(self):
			return self.is_admin
 

class Notifiction(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
	description = models.CharField(max_length=255, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	group = models.OneToOneField(Group, on_delete=models.CASCADE, unique=True)
	task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True)
	assignee = models.OneToOneField(User, on_delete=models.SET_NULL, default=None, null=True)
  
	objects = NotificationManager()
  
	def __str__(self):
		return f'{uuid}'