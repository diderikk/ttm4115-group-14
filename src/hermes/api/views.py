from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, QueryDict
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync, sync_to_async
from .models import User, Group, Task, Delivery, Notifiction
from .websocket import send_to_group
from hermes.state_machines.TeacherMachine import t
from hermes.state_machines.StudentMachine import s
import json, os, sys, time, uuid

@async_to_sync
async def send_to_ws(message):
  await send_to_group('teacher', message)
  
@login_required(login_url='/login/')
@csrf_exempt
def deliver(request):
  state_cookie = request.COOKIES.get("STATE_COOKIE")
  if request.method == 'POST':
    f = request.FILES["file"]
    print(f)
    task_id = request.POST["id"]
    group = request.user.group
    task = Task.objects.get(pk=task_id)
    delivery = Delivery.objects.create_delivery(file=f, group=group, task=task)
    message = json.dumps({'unit': task.unit, 'group': group.number, 'title': task.title})
    send_to_ws(message)
    time.sleep(0.3)
    s.trigger(uuid=state_cookie, trigger='back')
    return JsonResponse({'id': delivery.uuid}, status=201)
  elif request.method == 'GET':
    # deliveries = await get_all_deliveries()
    return JsonResponse(list(map(serialize_delivery, Delivery.objects.all())), status=200, safe=False)
  else:
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def deliver_detail(request, id):
  if request.method == 'DELETE':
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
  state_cookie = request.COOKIES.get("STATE_COOKIE")
  if request.method == 'POST':
    data = json.loads(request.body)
    description = data.get("description")
    group = request.user.group
    # TODO: Move to state machine?
    notification = Notifiction.objects.create_notification(description=description, group=group)
    message = json.dumps({'id': str(notification.uuid), 'description': notification.description, 'group': group.number})
    send_to_ws(message)
    s.trigger(uuid=state_cookie, trigger='send_notification')
    time.sleep(0.5)
    return JsonResponse(serialize_notification(notification), status=201)
  elif request.method == 'PUT':
    data = json.loads(request.body)
    description = data.get("description")
    group = request.user.group
    Notifiction.objects.update_notification(group, description)
    s.trigger(uuid=state_cookie, trigger='send_notification')
    time.sleep(0.5)
    return JsonResponse({}, status=204)
  elif request.method == 'GET':
    return JsonResponse(list(map(serialize_notification, Notifiction.objects.all().order_by('created_at'))), status=200, safe=False)
  elif request.method == 'DELETE':
    user = request.user
    Notifiction.objects.delete_notification_by_assignee(assignee=user)
    t.trigger(uuid=state_cookie, trigger='complete_help')
      
    time.sleep(0.5)
    return JsonResponse({}, status=204)
  else:
    return JsonResponse({'error': 'Invalid request method.'}, status=405)
  
  
@csrf_exempt
@login_required
def notifications_detail(request, group_number):
  state_cookie = request.COOKIES.get("STATE_COOKIE")
  if request.method == 'PUT':
    user = request.user
    Notifiction.objects.update_assignee(group_number=group_number, user=user)
    t.trigger(uuid=state_cookie, trigger='assistance_notification')
    time.sleep(0.5)
    return JsonResponse({}, status=204)
  else:
    return JsonResponse({'error': 'Invalid request method.'}, status=405)
  
@login_required
@csrf_exempt
def tasks(request):
  state_cookie = request.COOKIES.get("STATE_COOKIE")
  if request.method == 'POST':
    data = json.loads(request.body)
    title = data.get('title')
    description = data.get('description')
    unit = data.get('unit')
    # TODO: Move to state machine?
    task = Task.objects.create_task(title=title, description=description, unit=unit)
    t.trigger(uuid=state_cookie, trigger='task_published')
    time.sleep(0.5)
    return JsonResponse(serialize_task(task), status=201)
  elif request.method == 'GET':
    return JsonResponse(list(map(serialize_task, Task.objects.all())), status=200, safe=False)
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
