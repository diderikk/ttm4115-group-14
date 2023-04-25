from django.contrib.auth import authenticate, login as login_user, logout as logout_user
from hermes.api.models import Notifiction

def login(arg, **args) -> str:
		email = args["email"]
		password = args["password"]
		request = args["request"]
		user = authenticate(request, username=email, password=password)
		if user is not None and user.is_admin:
				login_user(request, user)
				return "progression_view"
		else:
				return "authentication"
		
def logout(arg, **args):
		request = args["request"]
		logout_user(request)

def complete_help() -> str:
		notifications = Notifiction.objects.all().filter(assignee=None)
		if len(notifications) == 0:
				return "progression_view"
		else:
				return "assist_group"
