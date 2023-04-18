from django.shortcuts import render
from django.http import HttpResponse

import os, sys

sys.path.append(os.path.dirname(__file__))

import statemachine as stm


def on_enter_active():
    print("State machine is now active")


def start(request):
    # Your view logic here
    stm.state_machine.send("start")
    # Return an HttpResponse or redirect as appropriate

    context = {"state": stm.state_machine.state}
    return render(request, state_to_html(), context)


def stop(request):
    # Your view logic here
    stm.state_machine.send("stop")
    # Return an HttpResponse or redirect as appropriate

    context = {"state": stm.state_machine.state}
    return render(request, state_to_html(), context)


def state_to_html():
    if stm.state_machine.state == "idle":
        return "idle.html"
    elif stm.state_machine.state == "active":
        return "active.html"


def idle_view(request):
    context = {"state": stm.state_machine.state}
    return render(request, "idle.html", context)


def active_view(request):
    context = {"state": stm.state_machine.state}
    return render(request, "active.html", context)
