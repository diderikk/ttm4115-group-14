# import paho.mqtt.client as mqtt
from django.contrib.auth import authenticate, login as login_user
from hermes.api.models import Notifiction
import stmpy
import logging
from threading import Thread
import json

class TeacherMachine:
    def __init__(self, uuid):

        t_initial = {"source": "initial", "target": "authentication"}

        # Change 1: effect is removed
        t_login = {
            "trigger": "login",
            "source": "authentication",
            "function": self.login,
        }

        # Change 2: effect is removed here, too
        t_duty = {
            "trigger": "duty",
            "source": "progression_view",
            "target": "publish_task",
        }

        t_published_task = {
            "trigger": "task_published",
            "source": "publish_task",
            "target": "progression_view",
        }
        
        t_cancel = {
            "trigger": "cancel",
            "source": "publish_task",
            "target": "progression_view",
        }

        t_assistance_notification = {
            "trigger": "assistance_notification",
            "source": "progression_view",
            "target": "assist_group",
        }

        t_complete_help = {
            "trigger": "complete_help",
            "source": "assist_group",
            "function": lambda: self.complete_help(),
        }

        authentication = {
            "name": "authentication",
            "entry": 'print_state("authentication")',
        }

        progression_view = {
            "name": "progression_view",
            "entry": 'print_state("progression_view")',
        }

        publish_task = {"name": "publish_task", "entry": 'print_state("publish_task")'}

        assist_group = {"name": "assist_group", "entry": 'print_state("assist_group")'}

        self.stm = stmpy.Machine(
            name=uuid,
            transitions=[
                t_initial,
                t_login,
                t_duty,
                t_cancel,
                t_published_task,
                t_assistance_notification,
                t_complete_help,
            ],
            states=[authentication, progression_view, publish_task, assist_group],
            obj=self,
        )

    def login(self, arg, **args) -> str:
        email = args["email"]
        password = args["password"]
        request = args["request"]
        user = authenticate(request, username=email, password=password)
        if user is not None and user.is_admin:
            login_user(request, user)
            return "progression_view"
        else:
            return "authentication"

    def complete_help(self) -> str:
        notifications = Notifiction.objects.all().filter(assignee=None)
        if len(notifications) == 0:
            return "progression_view"
        else:
            return "assist_group"

    def print_state(self, name):
        print(f"ENTERED STATE {name}")


class TeacherDriver:
    def __init__(self):
        self.stm_driver = stmpy.Driver()
        self.stm_driver.start(keep_active=True)

    def trigger(self, uuid, trigger):
        self.stm_driver.send(trigger, uuid)
    
    def trigger_login(self, uuid, request, email, password):
        self.stm_driver.send("login", uuid, [''], {'request': request, 'email': email, 'password': password})

    def add_machine(self, uuid):
        student_machine = TeacherMachine(uuid=uuid).stm
        self.stm_driver.add_machine(student_machine)
        
    def get_machine(self, uuid):
        return self.stm_driver._stms_by_id.get(uuid)
    
    def stop(self):
        self.mqtt_client.loop_stop()
        self.stm_driver.stop()


t = TeacherDriver()