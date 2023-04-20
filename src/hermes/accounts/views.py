from django.contrib.auth import authenticate, login as login_user, logout as user_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, QueryDict
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from hermes.accounts.models import User, Group, Task, Delivery
import json, os, sys

# sys.path.append(os.path.dirname(__file__))

def test_template(request):
  return render(request, "delivery.html")

def test_login(request):
  return render(request, "login.html")

@login_required
@csrf_exempt
def deliver(request):
  if request.method == 'POST' and request.FILES['myfile']:
    file = request.FILES['myfile']
    group = request.user.group
    task = Task.objects.get(pk="b425f6f7-080e-4f8d-8d49-97036d77cbfe") # TODO: read from request
    delivery = Delivery.objects.create_delivery(file=file, group=group, task=task)
    return JsonResponse({'id': delivery.uuid}, status=201)
  elif request.method == 'GET':
    return JsonResponse(list(map(serialize_delivery, Delivery.objects.all())), status=200, safe=False)
  else:
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def deliver_detail(request, id):
  if request.method == "GET":
    try:
      delivery = Delivery.objects.get(pk=id)
      return JsonResponse(serialize_delivery(delivery), status=200)
    except Task.DoesNotExist:
      return JsonResponse({'error': f'Delivery with id: {id} does not exist'}, status=404)
  elif request.method == 'PUT':
    data = json.loads(request.body)
    print(data)
    file = data['myfile']
    print(file)
    try: 
      delivery = Delivery.objects.update_delivery(id, file=file)
      return JsonResponse(serialize_task(task), status=200)
    except Task.DoesNotExist:
      return JsonResponse({'error': f'Delivery with id: {id} does not exist'}, status=404)
  elif request.method == 'DELETE':
    try: 
      Delivery.objects.delete_delivery(id)
      return JsonResponse({}, status=204)
    except Task.DoesNotExist:
      return JsonResponse({'error': f'Task with id: {id} does not exist'}, status=404)
  else:
    return JsonResponse({'error': 'Invalid request method.'}, status=405)
  

@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login_user(request, user)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=401)
    else:
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@login_required
@csrf_exempt
def logout(request):
    user_logout(request)
    return JsonResponse({}, status=204)
  
@login_required
@csrf_exempt
def tasks(request):
  if request.method == 'POST':
    data = json.loads(request.body)
    title = data.get('title')
    description = data.get('description')
    unit = data.get('unit')
    task = Task.objects.create_task(title=title, description=description, unit=unit)
    return JsonResponse(serialize_task(task), status=201)
  elif request.method == 'GET':
    return JsonResponse(list(map(serialize_task, Task.objects.all())), status=200, safe=False)
  else:
    return JsonResponse({'error': 'Invalid request method.'}, status=405)
  
@login_required
@csrf_exempt
def task_detail(request, id):
  if request.method == 'GET':
    try:
      task = Task.objects.get(pk=id)
      return JsonResponse(serialize_task(task), status=200)
    except Task.DoesNotExist:
      return JsonResponse({'error': f'Task with id: {id} does not exist'}, status=404)
  elif request.method == 'PUT':
    data = json.loads(request.body)
    title = data.get('title')
    description = data.get('description')
    unit = data.get('unit')
    try: 
      task = Task.objects.update_task(title=title, description=description, unit=unit, id=id)
      return JsonResponse(serialize_task(task), status=200)
    except Task.DoesNotExist:
      return JsonResponse({'error': f'Task with id: {id} does not exist'}, status=404)
  elif request.method == 'DELETE':
    try: 
      Task.objects.delete_task(id)
      return JsonResponse({}, status=204)
    except Task.DoesNotExist:
      return JsonResponse({'error': f'Task with id: {id} does not exist'}, status=404)
  else:
    return JsonResponse({'error': 'Invalid request method.'}, status=405)
  

@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        is_admin = data.get('isAdmin') | False
        group_number = data.get('groupNumber')
        group = Group.objects.create_group(group_number)
        if group or is_admin:
          if email and password:
            user = User.objects.create_user(email=email, password=password, is_admin=is_admin, group=group)
            return JsonResponse(serialize_user(user), status=201)
          else:
              return JsonResponse({'error': 'Email and password are required.'}, status=400)
        else: 
          return JsonResponse({'error': 'Could not create group.'}, status=500)
    elif request.method == "GET":
      users = User.objects.all()
      return JsonResponse(list(map(serialize_user, users)), status=200, safe=False)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)
      

def serialize_user(user: User):
  return {'id': user.uuid,'email': user.email, 'isStaff': user.is_admin, 'group': user.group.number if not user.is_admin else None}

def serialize_task(task: Task):
  return {'id': task.uuid, 'title': task.title, 'description': task.description, 'unit': task.unit}

def serialize_delivery(delivery: Delivery):
  return {'id': delivery.uuid, 'file': delivery.file.name, 'task': delivery.task.unit, 'group': delivery.group.number}
