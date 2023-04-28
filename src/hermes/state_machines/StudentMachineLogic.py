from django.contrib.auth import authenticate, login as login_user, logout as logout_user
from asgiref.sync import async_to_sync, sync_to_async
from hermes.api.websocket import send_to_group
import json
from hermes.api.models import Notifiction, Task, Delivery, Group

@async_to_sync
async def send_to_ws(message):
  await send_to_group('teacher', message)

def login(arg, **args) -> str:
	email = args["email"]
	password = args["password"]
	request = args["request"]
	user = authenticate(request, username=email, password=password)

	if user is not None:
			login_user(request, user)
			return "task_select"
	else:
			return "login"
		
def logout(arg, **args):
	request = args["request"]
	logout_user(request)
	return "login"

def post_notification(arg, **args):
	request = args["request"]
	if request.method == 'POST':
		data = json.loads(request.body)
		description = data.get("description")
		group = request.user.group
		notification = Notifiction.objects.get_notification(group)
		if notification is None:
			notification = Notifiction.objects.create_notification(description=description, group=group)
			message = serialize_message(notification=notification, group=group, method="POST")
			send_to_ws(message)
	else:
		data = json.loads(request.body)
		description = data.get("description")
		group = request.user.group
		Notifiction.objects.update_notification(group, description)
	return "task_select"

def post_notification_without_description(group_number):
	group = Group.objects.get(number=group_number)
	notification = Notifiction.objects.get_notification(group)
	if notification is None:
		notification = Notifiction.objects.create_notification(group=group, description="")
		message = serialize_message(notification=notification, group=group, method="POST")
		send_to_ws(message)


def complete_help(group_number):
	group = Group.objects.get(number=group_number)
	if (notification := Notifiction.objects.get_notification(group)) is not None:
		notification.delete()
		message = serialize_message(notification=notification, group=group, method="DELETE")
		send_to_ws(message)

def complete_delivery(arg, **args):
	request = args["request"]
	task = args["task"]
	group = request.user.group
	message = json.dumps({'unit': task.unit, 'group': group.number, 'title': task.title})
	send_to_ws(message)
	return "task_select"


def serialize_message(notification: Notifiction, group: Group, method: str):
	return json.dumps({'id': str(notification.uuid), 'description': notification.description, 'group': group.number, 'method': method})