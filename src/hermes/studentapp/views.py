from django.shortcuts import render
from django.http import HttpResponse

import os, sys
import time

sys.path.append(os.path.dirname(__file__))

import statemachine as stm


def on_enter_active():
    print("State machine is now active")


# def start(request):
#     # Your view logic here
#     state = stm.state_machine.state
#     stm.state_machine.send('start')
#     # Return an HttpResponse or redirect as appropriate
#     # i = 0
#     # while (state  ==  stm.state_machine.state and i < 10):
#     #     i += 1
#     time.sleep(0.1)
#     context = {'state': stm.state_machine.state}
#     return render(request, state_to_html(), context)

def send(request):
    msg = request.path.replace("/", "")
    stm.state_machine.send(msg)
    print(msg)
    time.sleep(0.1)
    context = {'state': stm.state_machine.state}
    return render(request, state_to_html(), context)


def state_to_html():
    return stm.state_machine.state + ".html"


def idle_view(request):
    context = {'state': stm.state_machine.state}
    return render(request, 'idle.html', context)


def active_view(request):
    context = {'state': stm.state_machine.state}
    return render(request, 'active.html', context)