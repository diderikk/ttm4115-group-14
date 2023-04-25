from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, QueryDict
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync, sync_to_async
from hermes.state_machines.StudentMachine import s
from hermes.api.models import Task, Delivery, Notifiction
from uuid import uuid4
import time, json


def render_state_student(request):
    state_cookie = request.COOKIES.get("STATE_COOKIE")
    if state_cookie != None and s.get_machine(state_cookie) != None:
        state = s.get_machine(state_cookie).state
        return render(request, f"{state}.html", get_state_context(request=request, state=state))
    else:
        cookie = str(uuid4())
        s.add_machine(cookie)
        time.sleep(0.3)
        state = s.get_machine(cookie).state
        response = render(request, f"{state}.html", get_state_context(
            request=request, state=state))
        response.set_cookie("STATE_COOKIE", value=cookie, httponly=True)
        return response
      
def render_task_state_student(request, id):
	state_cookie = request.COOKIES.get("STATE_COOKIE")
	if state_cookie != None and s.get_machine(state_cookie) != None and s.get_machine(state_cookie).state == 'task_overview':
		group = request.user.group
		task = Task.objects.get(pk=id)
		delivery = Delivery.objects.get_delivery(task=task, group=group)

		return render(request, "task_overview.html", {'task': task, 'delivery': delivery})
	elif state_cookie != None and s.get_machine(state_cookie) != None and s.get_machine(state_cookie).state == 'write_help_description':
		group = request.user.group
		notification = Notifiction.objects.get_notificaiton(group=group)
		return render(request, "write_help_description.html", {'notification': notification})
	else:
		return render_state_student(request)

def get_state_context(request, state):
    if state == 'task_select':
        return task_select_context(request=request)


def task_select_context(request):
    group = request.user.group
    delivered_tasks = Delivery.objects.filter(group=group).values_list('task__title', 'task__unit')
    unit_titles = {}
    for unit, title, uuid in Task.objects.values_list('unit', 'title', 'uuid'):
        delivered = (title, unit) in delivered_tasks
        if unit not in unit_titles:
            unit_titles[unit] = [(title, uuid, delivered)]
        else:
            unit_titles[unit].append((title, uuid, delivered))
            
    for unit, titles in unit_titles.items():
        all_delivered = all(delivered for _, _, delivered in titles)
        unit_titles[unit] = (unit_titles[unit], all_delivered)
            
        
    return {'unit_titles': unit_titles}


@csrf_exempt
def login(request):
    if request.method == 'POST':
        state_cookie = request.COOKIES.get("STATE_COOKIE")
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        s.trigger_login(uuid=state_cookie, request=request,
                        email=email, password=password)
        time.sleep(2)
        return JsonResponse({'success': True}, status=200)
    else:
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
      
@csrf_exempt
@login_required  
def select_task(request):
  state_cookie = request.COOKIES.get("STATE_COOKIE")
  s.trigger(uuid=state_cookie, trigger='task_selected')
  time.sleep(0.5)
  return JsonResponse({}, status=204)

@csrf_exempt
@login_required  
def back(request):
  state_cookie = request.COOKIES.get("STATE_COOKIE")
  s.trigger(uuid=state_cookie, trigger='back')
  time.sleep(0.5)
  return JsonResponse({}, status=204)

@csrf_exempt
@login_required  
def ask(request):
  state_cookie = request.COOKIES.get("STATE_COOKIE")
  s.trigger(uuid=state_cookie, trigger='ask')
  time.sleep(0.5)
  return JsonResponse({}, status=204)

@csrf_exempt
@login_required  
def cancel(request):
  state_cookie = request.COOKIES.get("STATE_COOKIE")
  s.trigger(uuid=state_cookie, trigger='cancel')
  time.sleep(0.5)
  return JsonResponse({}, status=204)
