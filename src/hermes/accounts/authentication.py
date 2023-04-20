from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from hermes.accounts.models import User

class UserModelBackend(ModelBackend):
	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None
 
	def authenticate(self, request, username=None, password=None, **kwargs):
		try:
			user = User.objects.get(email=username)
		except User.DoesNotExist:
				return None
		else:
			if user.password == make_password(password, user.salt):
				return user
		return None
