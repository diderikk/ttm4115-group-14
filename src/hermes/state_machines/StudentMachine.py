from django.contrib.auth import authenticate, login as login_user
import stmpy
import logging
from threading import Thread
import json



class StudentMachine:
    def __init__(self, uuid):
        self.tmp_int = 0

        t_initial = {"source": "initial", "target": "login"}

        # Change 1: effect is removed
        t_login = {
            "trigger": "login",
            "source": "login",
            "function": self.login,
        }

        # Change 2: effect is removed here, too
        t_task_selected = {
            "trigger": "task_selected",
            "source": "task_select",
            "target": "task_overview",
        }

        t_back = {"trigger": "back", "source": "task_overview", "target": "task_select"}

        t_ask = {
            "trigger": "ask",
            "source": "task_overview",
            "target": "write_help_description",
        }

        t_cancel = {
            "trigger": "cancel",
            "source": "write_help_description",
            "target": "task_overview",
        }

        t_send_notification = {
            "trigger": "send_notification",
            "source": "write_help_description",
            "target": "task_overview",
        }

        t_finish = {
            "trigger": "finish",
            "source": "task_overview",
            "function": lambda: self.finish(),
        }

        task_select = {"name": "task_select", "entry": 'print_state("task_select")'}

        login = {"name": "login", "entry": 'print_state("login")'}

        task_overview = {
            "name": "task_overview",
            "entry": 'print_state("task_overview")',
        }

        write_help_description = {
            "name": "write_help_description",
            "entry": 'print_state("write_help_description")',
        }

        finished_work = {
            "name": "finished_work",
            "entry": 'print_state("finished_work")',
        }

        self.stm = stmpy.Machine(
            name=uuid,
            transitions=[
                t_initial,
                t_login,
                t_task_selected,
                t_back,
                t_ask,
                t_cancel,
                t_send_notification,
                t_finish,
            ],
            states=[
                task_select,
                login,
                task_overview,
                write_help_description,
                finished_work,
            ],
            obj=self,
        )

    def login(self, arg, **args) -> str:
        email = args["email"]
        password = args["password"]
        request = args["request"]
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login_user(request, user)
            return "task_select"
        else:
            return "login"

    def finish(self) -> str:
        self.tmp_int += 1
        if self.tmp_int >= 3:
            return "finished_work"
        else:
            return "task_overview"

    def print_state(self, name):
        print(f"ENTERED STATE {name}")


class StudentDriver:
    def __init__(self):
        self.stm_driver = stmpy.Driver()
        self.stm_driver.start(keep_active=True)
        
    def trigger(self, uuid, trigger):
        self.stm_driver.send(trigger, uuid)
    
    def trigger_login(self, uuid, request, email, password):
        self.stm_driver.send("login", uuid, [''], {'request': request, 'email': email, 'password': password})

    def add_machine(self, uuid):
        student_machine = StudentMachine(uuid=uuid).stm
        self.stm_driver.add_machine(student_machine)
        
    def get_machine(self, uuid):
        return self.stm_driver._stms_by_id.get(uuid)

    def stop(self):
        self.mqtt_client.loop_stop()
        self.stm_driver.stop()


s = StudentDriver()

