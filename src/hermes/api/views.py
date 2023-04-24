from django.contrib.auth import authenticate, login as login_user
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, QueryDict
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync, sync_to_async
from .models import User, Group, Task, Delivery, Notifiction
from .websocket import send_to_group
from hermes.state_machines.TeacherMachine import t
import json, os, sys, time

def test_template(request):
  return render(request, "delivery.html")

def test_task_form(request):
  return render(request, "task_form.html")

def render_state(request):
  state = t.student_machine.state
  return render(request, f"{state}.html", get_state_context(request=request, state=state))

def get_state_context(request, state):
  if state == 'authentication':
    return {}
  elif state == 'progression_view':
    return progression_view_context()

def progression_view_context():
  unit_titles = {}
  for unit, title in Task.objects.values_list('unit', 'title'):
        # If the unit is not yet in the dictionary, add it and set the value to an empty list
    if unit not in unit_titles:
        unit_titles[unit] = [title]
    else:
      unit_titles[unit].append(title)
      
  group_task = {}
  groups = Group.objects.values_list('number', flat=True).distinct()
  for group in Group.objects.values_list('number', flat=True).distinct():
    group_task[f"{group}"] = []
  
  for group, task in Delivery.objects.values_list('group__number', 'task__title'):
    group_task[f"{group}"].append(task)
    
  notifications = Notifiction.objects.order_by('created_at').values_list('group__number', flat=True)
  print(notifications)
      
  return {'unit_titles': unit_titles, 'group_task': group_task, 'notifications': notifications}


async def test_http_to_websocket(request):
  await send_to_group('teacher', json.dumps({'unit': 1, 'group': 1, 'title': 'Title 2'}))
  return JsonResponse({'test': 'test'}, status=200)


@async_to_sync
async def send_to_ws(message):
  await send_to_group('teacher', message)
  
@login_required(login_url='/login/')
@csrf_exempt
def deliver(request):
  if request.method == 'POST' and request.FILES['myfile']:
    file = request.FILES['myfile']
    group = request.user.group
    task = Task.objects.get(pk="1d886973-ed06-44bb-8628-5c1d6f011fc1") # TODO: read from request
    delivery = Delivery.objects.create_delivery(file=file, group=group, task=task)
    message = json.dumps({'unit': task.unit, 'group': group.number, 'title': task.title})
    send_to_ws(message)
    return JsonResponse({'id': delivery.uuid}, status=201)
  elif request.method == 'GET':
    # deliveries = await get_all_deliveries()
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
    file = data['myfile']
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
@login_required
def notifications(request):
  if request.method == 'POST':
    data = json.loads(request.body)
    description = data.get("description")
    group = request.user.group
    # TODO: Move to state machine?
    notification = Notifiction.objects.create_notification(description=description, group=group)
    message = json.dumps({'id': str(notification.uuid), 'description': notification.description, 'group': group.number})
    send_to_ws(message)
    return JsonResponse(serialize_notification(notification), status=201)
  elif request.method == 'GET':
    return JsonResponse(list(map(serialize_notification, Notifiction.objects.all().order_by('created_at'))), status=200, safe=False)
  else:
    return JsonResponse({'error': 'Invalid request method.'}, status=405)
  
@csrf_exempt
@login_required
def notifications_detail(request, id):
  if request.method == 'PUT':
    user = request.user
    return JsonResponse({}, status=204)
  elif request.method == 'DELETE':
    try:
      notification = Notifiction.objects.get(pk=id)
      notification.delete()
      return JsonResponse({}, status=204)
    except Notifiction.DoesNotExist:
      return JsonResponse({'error': 'Not found'}, status=404) 
    
  else:
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def login(request):
  if request.method == 'POST':
    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('password')
    t.trigger_login(request=request, email=email, password=password)
    time.sleep(2)
    return JsonResponse({'success': True}, status=200)
  else:
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@login_required
@csrf_exempt
def duty(request):
    t.trigger('duty')
    time.sleep(0.5)
    return JsonResponse({'success': True}, status=200)
  
@login_required
@csrf_exempt
def tasks(request):
  if request.method == 'POST':
    data = json.loads(request.body)
    title = data.get('title')
    description = data.get('description')
    unit = data.get('unit')
    # TODO: Move to state machine?
    task = Task.objects.create_task(title=title, description=description, unit=unit)
    t.trigger('task_published')
    time.sleep(0.5)
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

def serialize_notification(notification: Notifiction):
  return {'id': notification.uuid, 'description': notification.description, 'group': notification.group.number}
