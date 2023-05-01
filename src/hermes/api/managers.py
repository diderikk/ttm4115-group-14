import secrets
from django.db import models
from django.core.files.base import ContentFile
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.hashers import make_password

class GroupManager(models.Manager):
	def create_group(self, number):
		if number == None:
			return None
		try:
			return self.get(number=number)
		except:
			group = self.model(
			number=number
			)
			group.save()
		return group

class NotificationManager(models.Manager):
	def get_notification(self, group):
		try:
			return self.get(group=group)
		except:
			return None

	def create_notification(self, description, group, task=None):
		notification = self.model(
		description=description,
		group=group,
		task=task
		)
		notification.save()
		return notification

	def update_notification(self, group, description):
		notification = self.get(group=group)
		notification.description = description
		notification.save()


	def update_assignee(self, group_number, user):
		if group_number == None:
			notification = self.get(assignee=user)
			notification.assignee = None
			notification.save()
		else:
			notification = self.get(group__number=group_number)
			notification.assignee = user
			notification.save()

		return True

	def delete_notification_by_assignee(self, assignee):
		notification = self.get(assignee=assignee)
		notification.delete()
    

class TaskManager(models.Manager):
	def create_task(self, title, description, unit):
   
		task = self.model(
				title=title,
				description=description,
				unit=unit
		)
  
		task.save()
		return task

	def update_task(self, id, title, description, unit):
		task = self.get(pk=id)
		task.title = title
		task.description = description
		task.unit = unit
		task.save()
		return task

	def delete_task(self, id):
		task = self.get(pk=id)
		task.delete()
  
class DeliveryManager(models.Manager):
	def create_delivery(self, file, group, task):
		prev_delivery = self.get_delivery(task, group)
		if prev_delivery == None:
			delivery = self.model(
				file=file,
				group=group,
				task=task
			)

			delivery.save()
			return delivery
		else:
			prev_delivery.file.delete()
			prev_delivery.file = file
			prev_delivery.save()
			return prev_delivery
  
	def get_delivery(self, task, group):
		try:
			return self.get(task=task, group=group)
		except:
			return None
  
	def delete_delivery(self, id):
		delivery = self.get(pk=id)
		delivery.file.delete()
		return delivery.delete()

class UserManager(BaseUserManager):
	def create_user(self, email, password, is_admin, group):
		user = self.validate_user(email, password, is_admin, group)
		user.save()
		return user
		
	def validate_user(self, email, password, is_admin, group):
		if not email:
			raise ValueError('Users must have an email address')
		if not password:
			raise ValueError('Users must have a password')
		if not group and not is_admin:
			raise ValueError('Users must have a group')
 
		salt = secrets.token_hex(32)
		return self.model(
			email=self.normalize_email(email),
			password=make_password(password, salt=salt),
			salt=salt,
   		is_admin=is_admin,
			group=group if not is_admin else None
		)
  
