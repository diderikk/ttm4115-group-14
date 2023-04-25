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
		return "authentication"

def complete_help(arg, **args):
	request = args["request"]
	user = request.user
	Notifiction.objects.delete_notification_by_assignee(assignee=user)
	return "progression_view"


def assistance_notification(arg, **args):
	user = request.user
	Notifiction.objects.update_assignee(group_number=group_number, user=user)
	return "assist_group"
