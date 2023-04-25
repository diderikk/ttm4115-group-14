import stmpy
import logging
from threading import Thread
import json
from .TeacherMachineLogic import login as login_, logout as logout_, complete_help

class TeacherMachine:
    def __init__(self, uuid):

        t_initial = {"source": "initial", "target": "authentication"}

        # Change 1: effect is removed
        t_login = {
            "trigger": "login",
            "source": "authentication",
            "function": login_,
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
        
        t_logout = {
            "trigger": "logout",
            "source": "progression_view",
            "target": "authentication",
            "effect": logout_
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
            "function": complete_help,
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

    def print_state(self, name):
        print(f"ENTERED STATE {name}")


class TeacherDriver:
    def __init__(self):
        self.stm_driver = stmpy.Driver()
        self.stm_driver.start(keep_active=True)

    def trigger(self, uuid, trigger, kwargs={}):
        self.stm_driver.send(trigger, uuid, [''], kwargs=kwargs)

    def add_machine(self, uuid):
        student_machine = TeacherMachine(uuid=uuid).stm
        self.stm_driver.add_machine(student_machine)
        
    def get_machine(self, uuid):
        return self.stm_driver._stms_by_id.get(uuid)
    
    def stop(self):
        self.mqtt_client.loop_stop()
        self.stm_driver.stop()


t = TeacherDriver()