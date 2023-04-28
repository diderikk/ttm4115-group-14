from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as logout_user
from django.http import JsonResponse, QueryDict
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync, sync_to_async
from hermes.state_machines.TeacherMachine import t
from hermes.api.models import Task, Delivery, Notifiction, Group
from uuid import uuid4
import time, json


def render_state_teacher(request):
  state_cookie = request.COOKIES.get("STATE_COOKIE")
  if state_cookie != None and "TEACHER" not in state_cookie:
    t.pop_machine(state_cookie)
  if state_cookie != None and t.get_machine(state_cookie) != None:
    state = t.get_machine(state_cookie).state
    return render(request, f"{state}.html", get_state_context(request=request, state=state))
  else:
    cookie = "TEACHER" + str(uuid4())
    t.add_machine(cookie)
    time.sleep(0.3)
    state = t.get_machine(cookie).state
    response = render(request, f"{state}.html", get_state_context(request=request, state=state))
    response.set_cookie("STATE_COOKIE", value=cookie, httponly=True)
    return response

def get_state_context(request, state):
  if state == 'authentication':
    return {}
  elif state == 'progression_view':
    return progression_view_context()
  elif state == 'assist_group':
    return assisting_group_context(request)

def progression_view_context():
  unit_titles = {}
  for unit, title in Task.objects.values_list('unit', 'title'):
        # If the unit is not yet in the dictionary, add it and set the value to an empty list
    if unit not in unit_titles:
        unit_titles[unit] = [(title, unit)]
    else:
      unit_titles[unit].append((title, unit))
      
  group_task = {}
  groups = Group.objects.values_list('number', flat=True).distinct()
  for group in Group.objects.values_list('number', flat=True).distinct():
    group_task[f"{group}"] = []
  
  for group, task_title, task_unit in Delivery.objects.values_list('group__number', 'task__title', 'task__unit'):
    group_task[f"{group}"].append((task_title, task_unit))
    
  notifications = Notifiction.objects.order_by('created_at').values_list('group__number', flat=True)
      
  return {'unit_titles': unit_titles, 'group_task': group_task, 'notifications': notifications}

def assisting_group_context(request):
  user = request.user
  notification = Notifiction.objects.get(assignee=user)
  return {'group': notification.group.number}


@login_required
@csrf_exempt
def duty(request):
  state_cookie = request.COOKIES.get("STATE_COOKIE")
  t.trigger(uuid=state_cookie, trigger='duty')
  time.sleep(0.5)
  return JsonResponse({'success': True}, status=200)

@login_required
@csrf_exempt
def cancel(request):
  state_cookie = request.COOKIES.get("STATE_COOKIE")
  t.trigger(uuid=state_cookie, trigger='cancel')
  time.sleep(0.5)
  return JsonResponse({}, status=204)


@csrf_exempt
def login(request):
  if request.method == 'POST':
    state_cookie = request.COOKIES.get("STATE_COOKIE")
    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('password')
    t.trigger(trigger='login', uuid=state_cookie, kwargs={
                             'request': request, 'email': email, 'password': password})
    time.sleep(2)
    return JsonResponse({'success': True}, status=200)
  else:
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
  
@csrf_exempt
@login_required  
def logout(request):
  state_cookie = request.COOKIES.get("STATE_COOKIE")
  t.trigger(trigger='logout', uuid=state_cookie, kwargs={'request': request})
  time.sleep(0.5)
  response = JsonResponse({}, status=204)
  response.delete_cookie('STATE_COOKIE')
  return response