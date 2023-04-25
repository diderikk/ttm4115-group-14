from django.contrib.auth import authenticate, login as login_user, logout as logout_user


def login(arg, **args) -> str:
	email = args["email"]
	password = args["password"]
	request = args["request"]
	print(email)
	user = authenticate(request, username=email, password=password)

	if user is not None:
			login_user(request, user)
			return "task_select"
	else:
			return "login"
		
def logout(arg, **args):
	request = args["request"]
	logout_user(request)
 